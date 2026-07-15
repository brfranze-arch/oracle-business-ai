from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth_utils import generate_token, hash_password, verify_password
from deps import get_current_user, get_db, security
from models import User, UserSession
from portal_models import CustomerPortalProfile

router = APIRouter(prefix="/api/portal", tags=["Customer Portal"])


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


def _profile_for(db: Session, user: User) -> CustomerPortalProfile:
    profile = db.query(CustomerPortalProfile).filter(
        CustomerPortalProfile.user_id == user.id
    ).first()
    if profile:
        return profile

    profile = CustomerPortalProfile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def _response(user: User, profile: CustomerPortalProfile) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": (user.role or "customer").upper(),
        "company_name": profile.company_name or "",
        "phone": profile.phone or "",
        "job_title": profile.job_title or "",
        "preferred_language": profile.preferred_language or "it",
        "created_at": user.created_at,
    }


@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return {"error": "Non autenticato"}
    return _response(current_user, _profile_for(db, current_user))


@router.put("/profile")
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return {"error": "Non autenticato"}

    normalized_email = payload.email.strip().lower()
    duplicate = db.query(User).filter(
        User.email == normalized_email,
        User.id != current_user.id,
    ).first()
    if duplicate:
        return {"error": "Email già utilizzata da un altro account"}

    current_user.name = payload.name.strip()
    current_user.email = normalized_email
    profile = _profile_for(db, current_user)
    profile.company_name = payload.company_name.strip()
    profile.phone = payload.phone.strip()
    profile.job_title = payload.job_title.strip()
    profile.preferred_language = payload.preferred_language.strip() or "it"
    db.commit()
    db.refresh(current_user)
    db.refresh(profile)
    return {"message": "Profilo aggiornato", "profile": _response(current_user, profile)}


@router.post("/change-password")
def change_password(
    payload: PasswordChange,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user or not credentials:
        return {"error": "Non autenticato"}
    if not verify_password(payload.current_password, current_user.password_hash):
        return {"error": "Password attuale non corretta"}
    if payload.current_password == payload.new_password:
        return {"error": "La nuova password deve essere diversa"}

    current_user.password_hash = hash_password(payload.new_password)
    db.query(UserSession).filter(UserSession.user_id == current_user.id).delete()
    token = generate_token()
    db.add(UserSession(user_id=current_user.id, token=token))
    db.commit()
    return {"message": "Password aggiornata", "token": token}


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if credentials:
        db.query(UserSession).filter(UserSession.token == credentials.credentials).delete()
        db.commit()
    return {"message": "Logout completato"}
