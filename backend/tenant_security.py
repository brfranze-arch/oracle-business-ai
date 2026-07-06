from tenant_engine import user_can_access_tenant, get_tenant_company_ids


def user_can_access_company(db, user_id: int, tenant_id: int, company_id: int) -> bool:
    if not tenant_id:
        return False

    if not user_can_access_tenant(db, user_id, tenant_id):
        return False

    company_ids = get_tenant_company_ids(db, tenant_id)

    return company_id in company_ids


def tenant_company_error():
    return {
        "error": "Azienda non autorizzata per questo workspace"
    }