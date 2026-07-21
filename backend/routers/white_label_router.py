from datetime import datetime
import re, secrets
from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from deps import get_current_user, get_db
from models import User
from tenant_engine import user_can_access_tenant
from tenant_models import TenantMember
from white_label_models import WhiteLabelBrand, WhiteLabelDomain

router = APIRouter(prefix="/api/white-label", tags=["White Label"])
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
HOST = re.compile(r"^(?=.{1,253}$)(?!-)[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")
PORTALS = {"app", "customer", "partner", "login", "website"}

class BrandPayload(BaseModel):
    brand_name: str = Field(min_length=2, max_length=180)
    tagline: str = Field(default="", max_length=255)
    logo_url: str = Field(default="", max_length=5000)
    favicon_url: str = Field(default="", max_length=5000)
    primary_color: str = "#2563EB"
    secondary_color: str = "#0F172A"
    accent_color: str = "#22C55E"
    background_color: str = "#F8FAFC"
    support_email: str = Field(default="", max_length=255)
    support_phone: str = Field(default="", max_length=80)
    website_url: str = Field(default="", max_length=1000)
    footer_text: str = Field(default="", max_length=500)
    privacy_url: str = Field(default="", max_length=1000)
    terms_url: str = Field(default="", max_length=1000)
    hide_powered_by: bool = False
    enabled: bool = True

class DomainPayload(BaseModel):
    hostname: str = Field(min_length=3, max_length=255)
    portal_type: str = "app"

def _admin(user):
    return bool(user and (user.role or "").lower() in {"admin", "superadmin", "partner_manager"})

def _can_manage(db, user, tenant_id):
    if _admin(user): return True
    m = db.query(TenantMember).filter(TenantMember.user_id == user.id, TenantMember.tenant_id == tenant_id).first()
    return bool(m and (m.role or "").lower() in {"owner", "admin"})

def _brand(db, tenant_id):
    row = db.query(WhiteLabelBrand).filter(WhiteLabelBrand.tenant_id == tenant_id).first()
    if not row:
        row = WhiteLabelBrand(tenant_id=tenant_id)
        db.add(row); db.commit(); db.refresh(row)
    return row

def _serialize(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns if c.name not in {"created_at", "updated_at"}}

def _public(row, portal_type="app", hostname=""):
    data = _serialize(row)
    data.pop("id", None); data.pop("tenant_id", None)
    data["portal_type"] = portal_type
    data["hostname"] = hostname
    return data

@router.get("/public/resolve")
def resolve(request: Request, hostname: str = "", tenant_id: int = 0, portal_type: str = "app", db: Session = Depends(get_db)):
    host = (hostname or request.headers.get("x-forwarded-host") or request.headers.get("host") or "").split(":")[0].lower().strip()
    domain = db.query(WhiteLabelDomain).filter(WhiteLabelDomain.hostname == host, WhiteLabelDomain.verified == True).first() if host else None
    selected_tenant = domain.tenant_id if domain else tenant_id
    selected_portal = domain.portal_type if domain else portal_type
    if selected_tenant:
        row = db.query(WhiteLabelBrand).filter(WhiteLabelBrand.tenant_id == selected_tenant, WhiteLabelBrand.enabled == True).first()
        if row: return _public(row, selected_portal, host)
    return _public(WhiteLabelBrand(tenant_id=0), selected_portal, host)

@router.get("/brand")
def get_brand(x_tenant_id: int = Header(default=0), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    if not x_tenant_id or not user_can_access_tenant(db, current_user.id, x_tenant_id): return {"error": "Tenant non autorizzato"}
    return _serialize(_brand(db, x_tenant_id))

@router.put("/brand")
def update_brand(payload: BrandPayload, x_tenant_id: int = Header(default=0), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user: return {"error": "Non autenticato"}
    if not x_tenant_id or not _can_manage(db, current_user, x_tenant_id): return {"error": "Permesso owner/admin richiesto"}
    for value in [payload.primary_color,payload.secondary_color,payload.accent_color,payload.background_color]:
        if not HEX.match(value): return {"error": f"Colore HEX non valido: {value}"}
    row = _brand(db, x_tenant_id)
    for k,v in (payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()).items(): setattr(row,k,v.strip() if isinstance(v,str) else v)
    db.commit(); db.refresh(row)
    return {"message":"Branding aggiornato", "brand":_serialize(row)}

@router.get("/domains")
def domains(x_tenant_id: int = Header(default=0), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or not x_tenant_id or not user_can_access_tenant(db,current_user.id,x_tenant_id): return {"error":"Tenant non autorizzato"}
    rows=db.query(WhiteLabelDomain).filter(WhiteLabelDomain.tenant_id==x_tenant_id).order_by(WhiteLabelDomain.created_at.desc()).all()
    return [{"id":r.id,"hostname":r.hostname,"portal_type":r.portal_type,"verified":r.verified,"verification_token":r.verification_token,"dns_record":f"orizzonte360-verification={r.verification_token}"} for r in rows]

@router.post("/domains")
def add_domain(payload: DomainPayload, x_tenant_id: int = Header(default=0), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user or not x_tenant_id or not _can_manage(db,current_user,x_tenant_id): return {"error":"Permesso owner/admin richiesto"}
    host=payload.hostname.lower().strip().replace("https://","").replace("http://","").split("/")[0].split(":")[0]
    portal=payload.portal_type.lower().strip()
    if not HOST.match(host): return {"error":"Hostname non valido"}
    if portal not in PORTALS: return {"error":"Tipo portale non valido"}
    if db.query(WhiteLabelDomain).filter(WhiteLabelDomain.hostname==host).first(): return {"error":"Dominio già registrato"}
    row=WhiteLabelDomain(tenant_id=x_tenant_id,hostname=host,portal_type=portal,verification_token=secrets.token_urlsafe(24))
    db.add(row); db.commit(); db.refresh(row)
    return {"message":"Dominio aggiunto. Configura il record TXT e verifica.","id":row.id,"verification_token":row.verification_token,"dns_record":f"orizzonte360-verification={row.verification_token}"}

@router.post("/domains/{domain_id}/verify")
def verify_domain(domain_id:int, confirmation_token:str="", x_tenant_id:int=Header(default=0), db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    if not current_user or not x_tenant_id or not _can_manage(db,current_user,x_tenant_id): return {"error":"Permesso owner/admin richiesto"}
    row=db.query(WhiteLabelDomain).filter(WhiteLabelDomain.id==domain_id,WhiteLabelDomain.tenant_id==x_tenant_id).first()
    if not row:return {"error":"Dominio non trovato"}
    # In locale/test il token conferma il possesso. In produzione sostituire con lookup DNS TXT automatico.
    if confirmation_token != row.verification_token:return {"error":"Token di verifica non valido"}
    row.verified=True; row.verified_at=datetime.utcnow(); db.commit()
    return {"message":"Dominio verificato","hostname":row.hostname}

@router.delete("/domains/{domain_id}")
def delete_domain(domain_id:int,x_tenant_id:int=Header(default=0),db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not current_user or not x_tenant_id or not _can_manage(db,current_user,x_tenant_id):return {"error":"Permesso owner/admin richiesto"}
    row=db.query(WhiteLabelDomain).filter(WhiteLabelDomain.id==domain_id,WhiteLabelDomain.tenant_id==x_tenant_id).first()
    if not row:return {"error":"Dominio non trovato"}
    db.delete(row);db.commit();return {"message":"Dominio rimosso"}
