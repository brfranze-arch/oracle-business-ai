from tenant_models import Tenant, TenantMember


def create_default_tenant_for_user(db, user):
    existing = db.query(Tenant).filter(
        Tenant.owner_user_id == user.id
    ).first()

    if existing:
        return existing

    tenant = Tenant(
        name=f"Workspace di {user.name}",
        owner_user_id=user.id,
        plan="FREE",
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    member = TenantMember(
        tenant_id=tenant.id,
        user_id=user.id,
        role="owner",
    )

    db.add(member)
    db.commit()

    return tenant


def get_user_tenants(db, user_id: int):
    memberships = db.query(TenantMember).filter(
        TenantMember.user_id == user_id
    ).all()

    tenant_ids = [m.tenant_id for m in memberships]

    if not tenant_ids:
        return []

    return db.query(Tenant).filter(
        Tenant.id.in_(tenant_ids)
    ).all()


def user_can_access_tenant(db, user_id: int, tenant_id: int):
    member = db.query(TenantMember).filter(
        TenantMember.user_id == user_id,
        TenantMember.tenant_id == tenant_id
    ).first()

    return member is not None