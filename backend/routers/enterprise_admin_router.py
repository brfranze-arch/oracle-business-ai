from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from deps import get_current_user, get_db
from models import User

router = APIRouter(prefix="/api/enterprise-admin", tags=["Enterprise Admin"])

ADMIN_ROLES = {"admin", "superadmin", "marketplace_manager", "partner_manager", "support"}
SUPER_ROLES = {"admin", "superadmin"}

ROLE_PERMISSIONS = {
    "superadmin": [
        "enterprise.dashboard", "marketplace.manage", "white_label.manage",
        "partners.manage", "billing.manage", "licenses.manage",
        "support.manage", "users.manage", "settings.manage"
    ],
    "admin": [
        "enterprise.dashboard", "marketplace.manage", "white_label.manage",
        "partners.manage", "billing.manage", "licenses.manage",
        "support.manage", "settings.manage"
    ],
    "marketplace_manager": ["enterprise.dashboard", "marketplace.manage"],
    "partner_manager": ["enterprise.dashboard", "partners.manage"],
    "support": ["enterprise.dashboard", "support.manage"],
}

def normalized_role(user: User | None) -> str:
    return (user.role or "").strip().lower() if user else ""

def require_enterprise_user(user: User | None) -> str:
    role = normalized_role(user)
    if not user:
        raise HTTPException(status_code=401, detail="Non autenticato")
    if role not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Accesso Enterprise non autorizzato")
    return role

@router.get("/access")
def enterprise_access(current_user: User = Depends(get_current_user)):
    role = require_enterprise_user(current_user)
    return {
        "authorized": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": role,
        },
        "permissions": ROLE_PERMISSIONS.get(role, ["enterprise.dashboard"]),
        "is_super_admin": role in SUPER_ROLES,
    }

@router.get("/users")
def list_enterprise_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = require_enterprise_user(current_user)
    if role not in SUPER_ROLES:
        raise HTTPException(status_code=403, detail="Permesso Super Admin richiesto")
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": (user.role or "client").lower(),
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]
