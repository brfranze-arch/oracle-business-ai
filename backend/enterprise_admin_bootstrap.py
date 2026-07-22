import os
from sqlalchemy.orm import Session

from auth_utils import hash_password
from models import User

_TRUE_VALUES = {"1", "true", "yes", "on", "si", "sì"}


def _env_enabled(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in _TRUE_VALUES


def bootstrap_enterprise_admin(db: Session) -> dict:
    """Create the initial Enterprise Super Admin from environment variables.

    The operation is intentionally idempotent: an existing account is never
    overwritten and its password is never reset during an application restart.
    """
    if not _env_enabled("ENTERPRISE_ADMIN_BOOTSTRAP_ENABLED", default=False):
        return {"status": "disabled"}

    email = os.getenv("ENTERPRISE_ADMIN_EMAIL", "").strip().lower()
    password = os.getenv("ENTERPRISE_ADMIN_PASSWORD", "")
    name = os.getenv("ENTERPRISE_ADMIN_NAME", "Orizzonte360 Super Admin").strip()

    if not email or "@" not in email:
        raise RuntimeError("ENTERPRISE_ADMIN_EMAIL mancante o non valida")
    if len(password) < 10:
        raise RuntimeError("ENTERPRISE_ADMIN_PASSWORD deve contenere almeno 10 caratteri")

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {
            "status": "exists",
            "email": existing.email,
            "role": existing.role,
        }

    admin = User(
        email=email,
        name=name or "Orizzonte360 Super Admin",
        password_hash=hash_password(password),
        role="superadmin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    return {
        "status": "created",
        "email": admin.email,
        "role": admin.role,
    }
