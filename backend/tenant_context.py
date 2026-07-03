from fastapi import Header, HTTPException, Depends

from database import SessionLocal
from tenant_engine import user_can_access_tenant
from auth import get_current_user


def get_current_tenant(
    x_tenant_id: int = Header(...),
    current_user=Depends(get_current_user)
):
    db = SessionLocal()

    try:

        if not user_can_access_tenant(
            db,
            current_user.id,
            x_tenant_id
        ):
            raise HTTPException(
                status_code=403,
                detail="Tenant non autorizzato"
            )

        return x_tenant_id

    finally:
        db.close()