from datetime import datetime
import secrets
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session
from deps import get_current_user, get_db
from models import User
from marketplace_models import MarketplaceCategory, MarketplaceModule, MarketplaceInstallation, MarketplaceEvent

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])
PLAN_RANK = {"FREE": 0, "PROFESSIONAL": 1, "BUSINESS": 2, "ENTERPRISE": 3}

class CategoryPayload(BaseModel):
    slug: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=120)
    description: str = Field(default="", max_length=1000)
    icon: str = Field(default="▦", max_length=20)
    sort_order: int = 0
    active: bool = True

class ModulePayload(BaseModel):
    slug: str = Field(min_length=2, max_length=100)
    category_id: int
    name: str = Field(min_length=2, max_length=180)
    short_description: str = Field(default="", max_length=300)
    description: str = Field(default="", max_length=5000)
    version: str = Field(default="1.0.0", max_length=40)
    icon: str = Field(default="◆", max_length=20)
    price: float = Field(default=0, ge=0)
    currency: str = Field(default="EUR", max_length=10)
    billing_type: str = "FREE"
    required_plan: str = "FREE"
    status: str = "PUBLISHED"
    featured: bool = False
    active: bool = True

class InstallPayload(BaseModel):
    company_id: int | None = None


def _admin(user: User | None):
    return bool(user and (user.role or "").lower() in {"admin", "superadmin", "marketplace_manager"})

def _require_user(user):
    if not user: raise HTTPException(status_code=401, detail="Non autenticato")

def _category(row):
    return {"id":row.id,"slug":row.slug,"name":row.name,"description":row.description,"icon":row.icon,"sort_order":row.sort_order,"active":row.active}

def _module(row, db, user_id=None):
    cat=db.query(MarketplaceCategory).filter(MarketplaceCategory.id==row.category_id).first()
    installed=False
    if user_id:
        installed=bool(db.query(MarketplaceInstallation).filter(MarketplaceInstallation.user_id==user_id,MarketplaceInstallation.module_id==row.id,MarketplaceInstallation.status=="ACTIVE").first())
    return {"id":row.id,"slug":row.slug,"name":row.name,"short_description":row.short_description,"description":row.description,"version":row.version,"icon":row.icon,"price":row.price,"currency":row.currency,"billing_type":row.billing_type,"required_plan":row.required_plan,"status":row.status,"featured":row.featured,"active":row.active,"install_count":row.install_count,"category":_category(cat) if cat else None,"installed":installed,"created_at":row.created_at.isoformat() if row.created_at else None}

@router.get("/categories")
def categories(db: Session=Depends(get_db)):
    return [_category(x) for x in db.query(MarketplaceCategory).filter(MarketplaceCategory.active==True).order_by(MarketplaceCategory.sort_order,MarketplaceCategory.name).all()]

@router.get("/catalog")
def catalog(q: str="", category: str="", billing_type: str="", featured: bool|None=None, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    query=db.query(MarketplaceModule).filter(MarketplaceModule.active==True,MarketplaceModule.status=="PUBLISHED")
    if q.strip():
        term=f"%{q.strip()}%"; query=query.filter(or_(MarketplaceModule.name.ilike(term),MarketplaceModule.short_description.ilike(term),MarketplaceModule.description.ilike(term)))
    if category:
        cat=db.query(MarketplaceCategory).filter(MarketplaceCategory.slug==category).first()
        query=query.filter(MarketplaceModule.category_id==(cat.id if cat else -1))
    if billing_type: query=query.filter(MarketplaceModule.billing_type==billing_type.upper())
    if featured is not None: query=query.filter(MarketplaceModule.featured==featured)
    return [_module(x,db,current_user.id if current_user else None) for x in query.order_by(MarketplaceModule.featured.desc(),MarketplaceModule.install_count.desc(),MarketplaceModule.name).all()]

@router.get("/catalog/{slug}")
def module_detail(slug: str, db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    row=db.query(MarketplaceModule).filter(MarketplaceModule.slug==slug,MarketplaceModule.active==True).first()
    if not row: raise HTTPException(status_code=404,detail="Modulo non trovato")
    return _module(row,db,current_user.id if current_user else None)

@router.get("/my-modules")
def my_modules(db: Session=Depends(get_db), current_user: User=Depends(get_current_user)):
    _require_user(current_user)
    rows=db.query(MarketplaceInstallation).filter(MarketplaceInstallation.user_id==current_user.id).order_by(MarketplaceInstallation.updated_at.desc()).all()
    out=[]
    for i in rows:
        m=db.query(MarketplaceModule).filter(MarketplaceModule.id==i.module_id).first()
        if m: out.append({"installation_id":i.id,"status":i.status,"company_id":i.company_id,"license_key":i.license_key,"installed_version":i.installed_version,"installed_at":i.installed_at.isoformat() if i.installed_at else None,"uninstalled_at":i.uninstalled_at.isoformat() if i.uninstalled_at else None,"module":_module(m,db,current_user.id)})
    return out

@router.post("/modules/{module_id}/install")
def install(module_id:int,payload:InstallPayload,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    _require_user(current_user)
    m=db.query(MarketplaceModule).filter(MarketplaceModule.id==module_id,MarketplaceModule.active==True,MarketplaceModule.status=="PUBLISHED").first()
    if not m: raise HTTPException(status_code=404,detail="Modulo non disponibile")
    if m.billing_type!="FREE" or m.price>0: raise HTTPException(status_code=409,detail="Il checkout dei moduli a pagamento sarà attivato nel PACK 05C")
    row=db.query(MarketplaceInstallation).filter(MarketplaceInstallation.user_id==current_user.id,MarketplaceInstallation.module_id==module_id).first()
    if row and row.status=="ACTIVE": return {"message":"Modulo già installato","installation_id":row.id}
    if not row:
        row=MarketplaceInstallation(user_id=current_user.id,company_id=payload.company_id,module_id=module_id,status="ACTIVE",installed_version=m.version,license_key="MKT-"+secrets.token_hex(12).upper())
        db.add(row); m.install_count=(m.install_count or 0)+1
    else:
        row.status="ACTIVE"; row.company_id=payload.company_id; row.installed_version=m.version; row.uninstalled_at=None; row.installed_at=datetime.utcnow()
        m.install_count=(m.install_count or 0)+1
    db.add(MarketplaceEvent(user_id=current_user.id,module_id=m.id,event_type="INSTALLED",details=f"version={m.version}")); db.commit(); db.refresh(row)
    return {"message":"Modulo installato","installation_id":row.id,"license_key":row.license_key}

@router.delete("/modules/{module_id}/uninstall")
def uninstall(module_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    _require_user(current_user)
    row=db.query(MarketplaceInstallation).filter(MarketplaceInstallation.user_id==current_user.id,MarketplaceInstallation.module_id==module_id,MarketplaceInstallation.status=="ACTIVE").first()
    if not row: raise HTTPException(status_code=404,detail="Installazione attiva non trovata")
    row.status="UNINSTALLED"; row.uninstalled_at=datetime.utcnow()
    m=db.query(MarketplaceModule).filter(MarketplaceModule.id==module_id).first()
    if m: m.install_count=max(0,(m.install_count or 0)-1)
    db.add(MarketplaceEvent(user_id=current_user.id,module_id=module_id,event_type="UNINSTALLED")); db.commit()
    return {"message":"Modulo disinstallato"}

@router.get("/admin/modules")
def admin_modules(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not _admin(current_user): raise HTTPException(status_code=403,detail="Accesso amministratore richiesto")
    return [_module(x,db) for x in db.query(MarketplaceModule).order_by(MarketplaceModule.updated_at.desc()).all()]

@router.post("/admin/modules")
def create_module(payload:ModulePayload,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not _admin(current_user): raise HTTPException(status_code=403,detail="Accesso amministratore richiesto")
    if db.query(MarketplaceModule).filter(MarketplaceModule.slug==payload.slug.strip().lower()).first(): raise HTTPException(status_code=409,detail="Slug già utilizzato")
    if not db.query(MarketplaceCategory).filter(MarketplaceCategory.id==payload.category_id).first(): raise HTTPException(status_code=400,detail="Categoria non valida")
    row=MarketplaceModule(**payload.model_dump()); row.slug=row.slug.strip().lower(); row.billing_type=row.billing_type.upper(); row.required_plan=row.required_plan.upper(); row.status=row.status.upper()
    db.add(row); db.commit(); db.refresh(row); return {"message":"Modulo creato","module":_module(row,db)}

@router.put("/admin/modules/{module_id}")
def update_module(module_id:int,payload:ModulePayload,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not _admin(current_user): raise HTTPException(status_code=403,detail="Accesso amministratore richiesto")
    row=db.query(MarketplaceModule).filter(MarketplaceModule.id==module_id).first()
    if not row: raise HTTPException(status_code=404,detail="Modulo non trovato")
    for k,v in payload.model_dump().items(): setattr(row,k,v)
    row.slug=row.slug.strip().lower(); row.billing_type=row.billing_type.upper(); row.required_plan=row.required_plan.upper(); row.status=row.status.upper()
    db.commit(); db.refresh(row); return {"message":"Modulo aggiornato","module":_module(row,db)}

@router.get("/admin/metrics")
def metrics(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not _admin(current_user): raise HTTPException(status_code=403,detail="Accesso amministratore richiesto")
    return {"modules":db.query(MarketplaceModule).count(),"published":db.query(MarketplaceModule).filter(MarketplaceModule.status=="PUBLISHED",MarketplaceModule.active==True).count(),"installations_active":db.query(MarketplaceInstallation).filter(MarketplaceInstallation.status=="ACTIVE").count(),"events":db.query(MarketplaceEvent).count()}
