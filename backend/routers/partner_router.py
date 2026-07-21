from datetime import datetime
import secrets
import string
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from deps import get_current_user, get_db
from models import User
from partner_models import PartnerProfile, PartnerCustomer, PartnerCommission, PartnerPayout

router = APIRouter(prefix="/api/partners", tags=["Partner Portal"])
LEVELS = {"SILVER": 10.0, "GOLD": 15.0, "PLATINUM": 20.0}
COMMISSION_STATUSES = {"EARNED", "APPROVED", "PAID", "CANCELLED"}

class PartnerApplication(BaseModel):
    company_name: str = Field(min_length=2, max_length=180)
    vat_number: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=60)
    website: str = Field(default="", max_length=255)
    notes: str = Field(default="", max_length=2000)

class PartnerUpdate(BaseModel):
    company_name: str = Field(min_length=2, max_length=180)
    vat_number: str = Field(default="", max_length=50)
    phone: str = Field(default="", max_length=60)
    website: str = Field(default="", max_length=255)

class ApprovalPayload(BaseModel):
    level: str = "SILVER"
    commission_rate: float | None = None

class LinkCustomerPayload(BaseModel):
    customer_email: str

class CommissionCreate(BaseModel):
    customer_user_id: int | None = None
    external_reference: str | None = None
    description: str = "Commissione abbonamento"
    gross_amount: float = Field(gt=0)

class CommissionStatus(BaseModel):
    status: str

class PayoutCreate(BaseModel):
    amount: float = Field(gt=0)
    method: str = "BANK_TRANSFER"
    note: str = ""

class PayoutStatus(BaseModel):
    status: str


def _is_admin(user: User | None) -> bool:
    return bool(user and (user.role or "").lower() in {"admin", "superadmin", "partner_manager"})


def _code(db: Session) -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        value = "O360-" + "".join(secrets.choice(alphabet) for _ in range(8))
        if not db.query(PartnerProfile).filter(PartnerProfile.referral_code == value).first():
            return value


def _partner(db: Session, user: User | None):
    if not user:
        return None
    return db.query(PartnerProfile).filter(PartnerProfile.user_id == user.id).first()


def _serialize_profile(row: PartnerProfile, user: User | None = None):
    return {
        "id": row.id, "user_id": row.user_id,
        "name": user.name if user else None, "email": user.email if user else None,
        "company_name": row.company_name, "vat_number": row.vat_number,
        "phone": row.phone, "website": row.website, "referral_code": row.referral_code,
        "level": row.level, "status": row.status, "commission_rate": row.commission_rate,
        "active": row.active, "approved_at": row.approved_at.isoformat() if row.approved_at else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.post("/apply")
def apply(payload: PartnerApplication, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    existing = _partner(db, current_user)
    if existing: return {"error": "Richiesta partner già presente", "partner": _serialize_profile(existing, current_user)}
    row = PartnerProfile(user_id=current_user.id, company_name=payload.company_name.strip(), vat_number=payload.vat_number.strip(), phone=payload.phone.strip(), website=payload.website.strip(), notes=payload.notes.strip(), referral_code=_code(db))
    db.add(row); db.commit(); db.refresh(row)
    return {"message": "Richiesta partner inviata", "partner": _serialize_profile(row, current_user)}


@router.get("/me")
def me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    row = _partner(db, current_user)
    if not row: return {"error": "Profilo partner non trovato", "can_apply": True}
    return _serialize_profile(row, current_user)


@router.put("/me")
def update_me(payload: PartnerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = _partner(db, current_user)
    if not row: return {"error": "Profilo partner non trovato"}
    row.company_name = payload.company_name.strip(); row.vat_number = payload.vat_number.strip()
    row.phone = payload.phone.strip(); row.website = payload.website.strip()
    db.commit(); db.refresh(row)
    return {"message": "Profilo aggiornato", "partner": _serialize_profile(row, current_user)}


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = _partner(db, current_user)
    if not row: return {"error": "Profilo partner non trovato"}
    customers = db.query(PartnerCustomer).filter(PartnerCustomer.partner_id == row.id).count()
    earned = db.query(func.coalesce(func.sum(PartnerCommission.commission_amount), 0)).filter(PartnerCommission.partner_id == row.id, PartnerCommission.status.in_(["EARNED", "APPROVED", "PAID"])).scalar() or 0
    approved = db.query(func.coalesce(func.sum(PartnerCommission.commission_amount), 0)).filter(PartnerCommission.partner_id == row.id, PartnerCommission.status == "APPROVED").scalar() or 0
    paid = db.query(func.coalesce(func.sum(PartnerCommission.commission_amount), 0)).filter(PartnerCommission.partner_id == row.id, PartnerCommission.status == "PAID").scalar() or 0
    pending_payouts = db.query(func.coalesce(func.sum(PartnerPayout.amount), 0)).filter(PartnerPayout.partner_id == row.id, PartnerPayout.status.in_(["REQUESTED", "PROCESSING"])).scalar() or 0
    return {"partner": _serialize_profile(row, current_user), "metrics": {"customers": customers, "earned_total": round(float(earned), 2), "approved_available": round(float(approved), 2), "paid_total": round(float(paid), 2), "pending_payouts": round(float(pending_payouts), 2), "currency": "EUR"}}


@router.get("/customers")
def customers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = _partner(db, current_user)
    if not row: return {"error": "Profilo partner non trovato"}
    links = db.query(PartnerCustomer).filter(PartnerCustomer.partner_id == row.id).order_by(PartnerCustomer.attributed_at.desc()).all()
    result = []
    for link in links:
        user = db.query(User).filter(User.id == link.customer_user_id).first()
        result.append({"id": link.id, "customer_user_id": link.customer_user_id, "name": user.name if user else "", "email": user.email if user else "", "source": link.source, "status": link.status, "attributed_at": link.attributed_at.isoformat()})
    return result


@router.get("/commissions")
def commissions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = _partner(db, current_user)
    if not row: return {"error": "Profilo partner non trovato"}
    rows = db.query(PartnerCommission).filter(PartnerCommission.partner_id == row.id).order_by(PartnerCommission.created_at.desc()).all()
    return [{"id": x.id, "customer_user_id": x.customer_user_id, "external_reference": x.external_reference, "description": x.description, "gross_amount": x.gross_amount, "commission_rate": x.commission_rate, "commission_amount": x.commission_amount, "currency": x.currency, "status": x.status, "earned_at": x.earned_at.isoformat() if x.earned_at else None, "paid_at": x.paid_at.isoformat() if x.paid_at else None} for x in rows]


@router.get("/payouts")
def payouts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = _partner(db, current_user)
    if not row: return {"error": "Profilo partner non trovato"}
    rows = db.query(PartnerPayout).filter(PartnerPayout.partner_id == row.id).order_by(PartnerPayout.requested_at.desc()).all()
    return [{"id": x.id, "amount": x.amount, "currency": x.currency, "status": x.status, "method": x.method, "note": x.note, "requested_at": x.requested_at.isoformat(), "processed_at": x.processed_at.isoformat() if x.processed_at else None} for x in rows]


@router.post("/payouts")
def request_payout(payload: PayoutCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    row = _partner(db, current_user)
    if not row or not row.active: return {"error": "Partner non attivo"}
    available = db.query(func.coalesce(func.sum(PartnerCommission.commission_amount), 0)).filter(PartnerCommission.partner_id == row.id, PartnerCommission.status == "APPROVED").scalar() or 0
    reserved = db.query(func.coalesce(func.sum(PartnerPayout.amount), 0)).filter(PartnerPayout.partner_id == row.id, PartnerPayout.status.in_(["REQUESTED", "PROCESSING"])).scalar() or 0
    if payload.amount > float(available) - float(reserved): return {"error": "Importo superiore al saldo disponibile"}
    payout = PartnerPayout(partner_id=row.id, amount=round(payload.amount, 2), method=payload.method.upper(), note=payload.note)
    db.add(payout); db.commit(); db.refresh(payout)
    return {"message": "Richiesta pagamento inviata", "payout_id": payout.id}


@router.get("/admin")
def admin_list(status: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_admin(current_user): return {"error": "Permesso amministratore richiesto"}
    query = db.query(PartnerProfile)
    if status: query = query.filter(PartnerProfile.status == status.upper())
    rows = query.order_by(PartnerProfile.created_at.desc()).all()
    return [_serialize_profile(x, db.query(User).filter(User.id == x.user_id).first()) for x in rows]


@router.post("/admin/{partner_id}/approve")
def approve(partner_id: int, payload: ApprovalPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_admin(current_user): return {"error": "Permesso amministratore richiesto"}
    row = db.query(PartnerProfile).filter(PartnerProfile.id == partner_id).first()
    if not row: return {"error": "Partner non trovato"}
    level = payload.level.upper()
    if level not in LEVELS: return {"error": "Livello non valido"}
    row.level = level; row.commission_rate = payload.commission_rate if payload.commission_rate is not None else LEVELS[level]
    row.status = "APPROVED"; row.active = True; row.approved_by_user_id = current_user.id; row.approved_at = datetime.utcnow()
    user = db.query(User).filter(User.id == row.user_id).first()
    if user and (user.role or "").lower() == "client": user.role = "partner"
    db.commit(); db.refresh(row)
    return {"message": "Partner approvato", "partner": _serialize_profile(row, user)}


@router.post("/admin/{partner_id}/reject")
def reject(partner_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_admin(current_user): return {"error": "Permesso amministratore richiesto"}
    row = db.query(PartnerProfile).filter(PartnerProfile.id == partner_id).first()
    if not row: return {"error": "Partner non trovato"}
    row.status = "REJECTED"; row.active = False; db.commit()
    return {"message": "Richiesta partner rifiutata"}


@router.post("/admin/{partner_id}/customers")
def admin_link_customer(partner_id: int, payload: LinkCustomerPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_admin(current_user): return {"error": "Permesso amministratore richiesto"}
    partner = db.query(PartnerProfile).filter(PartnerProfile.id == partner_id).first()
    customer = db.query(User).filter(func.lower(User.email) == payload.customer_email.strip().lower()).first()
    if not partner or not customer: return {"error": "Partner o cliente non trovato"}
    existing = db.query(PartnerCustomer).filter(PartnerCustomer.customer_user_id == customer.id).first()
    if existing: return {"error": "Cliente già attribuito a un partner"}
    link = PartnerCustomer(partner_id=partner.id, customer_user_id=customer.id, source="ADMIN")
    db.add(link); db.commit(); db.refresh(link)
    return {"message": "Cliente associato", "link_id": link.id}


@router.post("/admin/{partner_id}/commissions")
def admin_commission(partner_id: int, payload: CommissionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_admin(current_user): return {"error": "Permesso amministratore richiesto"}
    partner = db.query(PartnerProfile).filter(PartnerProfile.id == partner_id).first()
    if not partner: return {"error": "Partner non trovato"}
    amount = round(payload.gross_amount * partner.commission_rate / 100, 2)
    row = PartnerCommission(partner_id=partner.id, customer_user_id=payload.customer_user_id, external_reference=payload.external_reference, description=payload.description, gross_amount=round(payload.gross_amount, 2), commission_rate=partner.commission_rate, commission_amount=amount)
    db.add(row); db.commit(); db.refresh(row)
    return {"message": "Commissione registrata", "commission_id": row.id, "commission_amount": amount}


@router.patch("/admin/commissions/{commission_id}")
def admin_commission_status(commission_id: int, payload: CommissionStatus, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_admin(current_user): return {"error": "Permesso amministratore richiesto"}
    status = payload.status.upper()
    if status not in COMMISSION_STATUSES: return {"error": "Stato non valido"}
    row = db.query(PartnerCommission).filter(PartnerCommission.id == commission_id).first()
    if not row: return {"error": "Commissione non trovata"}
    row.status = status
    if status == "APPROVED": row.approved_at = datetime.utcnow()
    if status == "PAID": row.paid_at = datetime.utcnow()
    db.commit(); return {"message": "Stato commissione aggiornato"}


@router.patch("/admin/payouts/{payout_id}")
def admin_payout_status(payout_id: int, payload: PayoutStatus, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not _is_admin(current_user): return {"error": "Permesso amministratore richiesto"}
    status = payload.status.upper()
    if status not in {"REQUESTED", "PROCESSING", "PAID", "REJECTED"}: return {"error": "Stato non valido"}
    row = db.query(PartnerPayout).filter(PartnerPayout.id == payout_id).first()
    if not row: return {"error": "Pagamento non trovato"}
    row.status = status
    if status in {"PAID", "REJECTED"}: row.processed_at = datetime.utcnow()
    db.commit(); return {"message": "Pagamento aggiornato"}
