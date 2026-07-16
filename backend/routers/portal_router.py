from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import secrets

from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth_utils import generate_token, hash_password, verify_password
from billing_engine import get_user_subscription
from billing_models import Plan, Subscription
from deps import get_current_user, get_db, security
from models import User, UserSession
from portal_models import CustomerPortalProfile
from portal_license_models import (
    PortalDownload, PortalDownloadLog, PortalDownloadToken, PortalLicense,
    PortalLicenseActivation, PortalRelease,
)
from tenant_models import TenantCompany, TenantMember

router = APIRouter(prefix="/api/portal", tags=["Customer Portal"])

PLAN_RANK = {"FREE": 0, "PROFESSIONAL": 1, "BUSINESS": 2, "ENTERPRISE": 3}
PLAN_DEFAULTS = {
    "FREE": {"max_seats": 1, "max_companies": 1},
    "PROFESSIONAL": {"max_seats": 3, "max_companies": 1},
    "BUSINESS": {"max_seats": 10, "max_companies": 5},
    "ENTERPRISE": {"max_seats": 50, "max_companies": 50},
}


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255)
    company_name: str = Field(default="", max_length=180)
    phone: str = Field(default="", max_length=60)
    job_title: str = Field(default="", max_length=120)
    preferred_language: str = Field(default="it", max_length=10)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)


class ActivationCreate(BaseModel):
    device_name: str = Field(default="Browser", max_length=120)
    device_fingerprint: str = Field(min_length=8, max_length=255)


def _profile_for(db: Session, user: User) -> CustomerPortalProfile:
    profile = db.query(CustomerPortalProfile).filter(CustomerPortalProfile.user_id == user.id).first()
    if profile:
        return profile
    profile = CustomerPortalProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _profile_response(user: User, profile: CustomerPortalProfile) -> dict:
    return {
        "id": user.id, "name": user.name, "email": user.email,
        "role": (user.role or "customer").upper(),
        "company_name": profile.company_name or "", "phone": profile.phone or "",
        "job_title": profile.job_title or "",
        "preferred_language": profile.preferred_language or "it",
        "created_at": user.created_at,
    }


def _plan_for(db: Session, user_id: int) -> tuple[str, Subscription | None]:
    subscription = get_user_subscription(db, user_id)
    plan = (subscription.plan if subscription else "FREE").upper()
    return plan if plan in PLAN_RANK else "FREE", subscription


def _license_key(user_id: int) -> str:
    return f"O360-{user_id:06d}-{secrets.token_hex(4).upper()}"


def _license_for(db: Session, user: User) -> PortalLicense:
    plan, subscription = _plan_for(db, user.id)
    license_obj = db.query(PortalLicense).filter(PortalLicense.user_id == user.id).first()
    defaults = PLAN_DEFAULTS[plan]
    expires_at = None
    if subscription:
        expires_at = subscription.cancel_date or subscription.renewal_date or subscription.trial_end
    if not license_obj:
        license_obj = PortalLicense(
            user_id=user.id, license_key=_license_key(user.id), edition="SAAS_CLOUD",
            plan=plan, status=(subscription.status if subscription else "active"),
            max_seats=defaults["max_seats"], max_companies=defaults["max_companies"],
            expires_at=expires_at,
        )
        db.add(license_obj)
    else:
        license_obj.plan = plan
        license_obj.status = subscription.status if subscription else "active"
        license_obj.max_seats = defaults["max_seats"]
        license_obj.max_companies = defaults["max_companies"]
        license_obj.expires_at = expires_at
    db.commit()
    db.refresh(license_obj)
    return license_obj


def _entitled(plan: str, item: PortalDownload) -> bool:
    if PLAN_RANK.get(plan, 0) < PLAN_RANK.get((item.min_plan or "FREE").upper(), 0):
        return False
    return item.required_edition in (None, "", "ANY", "SAAS_CLOUD")


def _fmt_date(value):
    return value.isoformat() if value else None


@router.get("/profile")
def get_profile(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    return _profile_response(current_user, _profile_for(db, current_user))


@router.put("/profile")
def update_profile(payload: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    normalized_email = payload.email.strip().lower()
    duplicate = db.query(User).filter(User.email == normalized_email, User.id != current_user.id).first()
    if duplicate: return {"error": "Email già utilizzata da un altro account"}
    current_user.name = payload.name.strip(); current_user.email = normalized_email
    profile = _profile_for(db, current_user)
    profile.company_name = payload.company_name.strip(); profile.phone = payload.phone.strip()
    profile.job_title = payload.job_title.strip(); profile.preferred_language = payload.preferred_language.strip() or "it"
    db.commit(); db.refresh(current_user); db.refresh(profile)
    return {"message": "Profilo aggiornato", "profile": _profile_response(current_user, profile)}


@router.post("/change-password")
def change_password(payload: PasswordChange, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or not credentials: return {"error": "Non autenticato"}
    if not verify_password(payload.current_password, current_user.password_hash): return {"error": "Password attuale non corretta"}
    if payload.current_password == payload.new_password: return {"error": "La nuova password deve essere diversa"}
    current_user.password_hash = hash_password(payload.new_password)
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    token = generate_token(); db.add(UserSession(user_id=current_user.id, token=token)); db.commit()
    return {"message": "Password aggiornata", "token": token}


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    if credentials:
        db.query(UserSession).filter(UserSession.token == credentials.credentials).delete(); db.commit()
    return {"message": "Logout completato"}


@router.get("/license")
def get_license(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    lic = _license_for(db, current_user)
    member_count = db.query(TenantMember).filter(TenantMember.user_id == current_user.id).count()
    company_count = db.query(func.count(func.distinct(TenantCompany.company_id))).join(TenantMember, TenantMember.tenant_id == TenantCompany.tenant_id).filter(TenantMember.user_id == current_user.id).scalar() or 0
    activations = db.query(PortalLicenseActivation).filter(PortalLicenseActivation.license_id == lic.id, PortalLicenseActivation.active == True).count()
    return {
        "id": lic.id, "license_key": lic.license_key, "edition": lic.edition, "plan": lic.plan,
        "status": lic.status, "max_seats": lic.max_seats, "used_seats": activations,
        "max_companies": lic.max_companies, "used_companies": company_count,
        "tenant_memberships": member_count, "current_version": lic.current_version,
        "starts_at": _fmt_date(lic.starts_at), "expires_at": _fmt_date(lic.expires_at),
    }


@router.get("/license/activations")
def list_activations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    lic = _license_for(db, current_user)
    rows = db.query(PortalLicenseActivation).filter(PortalLicenseActivation.license_id == lic.id).order_by(PortalLicenseActivation.last_seen_at.desc()).all()
    return [{"id": x.id, "device_name": x.device_name, "device_fingerprint": x.device_fingerprint, "active": x.active, "activated_at": _fmt_date(x.activated_at), "last_seen_at": _fmt_date(x.last_seen_at)} for x in rows]


@router.post("/license/activate")
def activate_license(payload: ActivationCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    lic = _license_for(db, current_user)
    existing = db.query(PortalLicenseActivation).filter(PortalLicenseActivation.license_id == lic.id, PortalLicenseActivation.device_fingerprint == payload.device_fingerprint).first()
    if existing:
        existing.device_name = payload.device_name; existing.active = True; existing.last_seen_at = datetime.utcnow()
        db.commit(); return {"message": "Dispositivo aggiornato", "activation_id": existing.id}
    active_count = db.query(PortalLicenseActivation).filter(PortalLicenseActivation.license_id == lic.id, PortalLicenseActivation.active == True).count()
    if active_count >= lic.max_seats: return {"error": "Limite postazioni raggiunto"}
    row = PortalLicenseActivation(license_id=lic.id, device_name=payload.device_name, device_fingerprint=payload.device_fingerprint, ip_address=request.client.host if request.client else "")
    db.add(row); db.commit(); db.refresh(row)
    return {"message": "Dispositivo attivato", "activation_id": row.id}


@router.delete("/license/activations/{activation_id}")
def deactivate_license(activation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    lic = _license_for(db, current_user)
    row = db.query(PortalLicenseActivation).filter(PortalLicenseActivation.id == activation_id, PortalLicenseActivation.license_id == lic.id).first()
    if not row: return {"error": "Attivazione non trovata"}
    row.active = False; db.commit(); return {"message": "Dispositivo disattivato"}


@router.get("/downloads")
def list_downloads(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    plan, _ = _plan_for(db, current_user.id)
    rows = db.query(PortalDownload).filter(PortalDownload.active == True).order_by(PortalDownload.created_at.desc()).all()
    return [{
        "id": x.id, "slug": x.slug, "title": x.title, "description": x.description,
        "category": x.category, "file_name": x.file_name, "version": x.version,
        "min_plan": x.min_plan, "required_edition": x.required_edition,
        "size_bytes": x.size_bytes, "checksum_sha256": x.checksum_sha256,
        "entitled": _entitled(plan, x),
    } for x in rows]


@router.post("/downloads/{download_id}/token")
def create_download_token(download_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    plan, _ = _plan_for(db, current_user.id)
    item = db.query(PortalDownload).filter(PortalDownload.id == download_id, PortalDownload.active == True).first()
    if not item: return {"error": "Download non trovato"}
    if not _entitled(plan, item): return {"error": f"Risorsa disponibile dal piano {item.min_plan}"}
    token = secrets.token_urlsafe(32)
    row = PortalDownloadToken(token=token, user_id=current_user.id, download_id=item.id, expires_at=datetime.utcnow() + timedelta(minutes=5))
    db.add(row); db.commit()
    return {"token": token, "download_url": f"/api/portal/download/{token}", "expires_in_seconds": 300}


@router.get("/download/{token}")
def download_file(token: str, request: Request, db: Session = Depends(get_db)):
    row = db.query(PortalDownloadToken).filter(PortalDownloadToken.token == token).first()
    if not row or row.used_at or row.expires_at < datetime.utcnow():
        return PlainTextResponse("Token non valido o scaduto", status_code=403)
    item = db.query(PortalDownload).filter(PortalDownload.id == row.download_id, PortalDownload.active == True).first()
    if not item: return PlainTextResponse("File non disponibile", status_code=404)
    path = Path(item.storage_path).resolve()
    allowed_root = (Path(__file__).resolve().parents[1] / "portal_downloads").resolve()
    if allowed_root not in path.parents or not path.is_file():
        return PlainTextResponse("Percorso file non valido", status_code=404)
    row.used_at = datetime.utcnow()
    db.add(PortalDownloadLog(user_id=row.user_id, download_id=item.id, file_name=item.file_name, ip_address=request.client.host if request.client else ""))
    db.commit()
    return FileResponse(path=str(path), filename=item.file_name, media_type="application/octet-stream")


@router.get("/downloads/history")
def download_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    rows = db.query(PortalDownloadLog).filter(PortalDownloadLog.user_id == current_user.id).order_by(PortalDownloadLog.downloaded_at.desc()).limit(100).all()
    return [{"id": x.id, "download_id": x.download_id, "file_name": x.file_name, "downloaded_at": _fmt_date(x.downloaded_at)} for x in rows]


@router.get("/releases")
def list_releases(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    plan, _ = _plan_for(db, current_user.id)
    rows = db.query(PortalRelease).order_by(PortalRelease.published_at.desc()).all()
    return [{"id": x.id, "version": x.version, "channel": x.channel, "status": x.status, "title": x.title, "summary": x.summary, "changelog": x.changelog, "min_plan": x.min_plan, "published_at": _fmt_date(x.published_at), "entitled": PLAN_RANK.get(plan,0) >= PLAN_RANK.get((x.min_plan or "FREE").upper(),0)} for x in rows]


@router.get("/releases/{release_id}/notes")
def release_notes(release_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    row = db.query(PortalRelease).filter(PortalRelease.id == release_id).first()
    if not row: return {"error": "Release non trovata"}
    return PlainTextResponse(f"{row.title}\n\n{row.summary}\n\nCHANGELOG\n{row.changelog}", media_type="text/plain; charset=utf-8")
