from datetime import datetime, timedelta

from billing_models import Plan, PlanPermission, Subscription


DEFAULT_PLANS = [
    {
        "name": "FREE",
        "price_month": 0,
        "price_year": 0,
        "max_companies": 1,
        "max_users": 1,
        "description": "Piano gratuito per testare Oracle Business AI.",
        "permissions": {
            "finance": True,
            "customer": True,
            "compliance": True,
            "cyber": False,
            "assistant": True,
            "reports": False,
            "timeline": False,
            "import_data": False,
            "openai": False,
            "osint": False,
            "predictive": False,
            "agents": False,
            "multi_company": False,
            "pdf_export": False,
            "api_access": False,
        },
    },
    {
        "name": "PROFESSIONAL",
        "price_month": 49,
        "price_year": 490,
        "max_companies": 5,
        "max_users": 5,
        "description": "Piano professionale per aziende e consulenti.",
        "permissions": {
            "finance": True,
            "customer": True,
            "compliance": True,
            "cyber": True,
            "assistant": True,
            "reports": True,
            "timeline": True,
            "import_data": True,
            "openai": False,
            "osint": False,
            "predictive": False,
            "agents": False,
            "multi_company": True,
            "pdf_export": True,
            "api_access": False,
        },
    },
    {
        "name": "BUSINESS",
        "price_month": 149,
        "price_year": 1490,
        "max_companies": 20,
        "max_users": 20,
        "description": "Piano business con AI avanzata, API e funzioni predittive.",
        "permissions": {
            "finance": True,
            "customer": True,
            "compliance": True,
            "cyber": True,
            "assistant": True,
            "reports": True,
            "timeline": True,
            "import_data": True,
            "openai": True,
            "osint": True,
            "predictive": True,
            "agents": False,
            "multi_company": True,
            "pdf_export": True,
            "api_access": True,
        },
    },
    {
        "name": "ENTERPRISE",
        "price_month": 399,
        "price_year": 3990,
        "max_companies": 999999,
        "max_users": 999999,
        "description": "Piano enterprise con agenti autonomi, OSINT, API e white label.",
        "permissions": {
            "finance": True,
            "customer": True,
            "compliance": True,
            "cyber": True,
            "assistant": True,
            "reports": True,
            "timeline": True,
            "import_data": True,
            "openai": True,
            "osint": True,
            "predictive": True,
            "agents": True,
            "multi_company": True,
            "pdf_export": True,
            "api_access": True,
        },
    },
]


def seed_default_plans(db):
    for item in DEFAULT_PLANS:
        existing = db.query(Plan).filter(Plan.name == item["name"]).first()

        if existing:
            continue

        plan = Plan(
            name=item["name"],
            price_month=item["price_month"],
            price_year=item["price_year"],
            max_companies=item["max_companies"],
            max_users=item["max_users"],
            description=item["description"],
            active=True,
        )

        db.add(plan)
        db.commit()
        db.refresh(plan)

        permissions = PlanPermission(
            plan_id=plan.id,
            **item["permissions"],
        )

        db.add(permissions)
        db.commit()


def create_free_subscription_for_user(db, user_id: int):
    existing = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()

    if existing:
        return existing

    subscription = Subscription(
        user_id=user_id,
        plan="FREE",
        status="active",
        trial=True,
        trial_end=datetime.utcnow() + timedelta(days=14),
        provider="internal",
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


def get_user_subscription(db, user_id: int):
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user_id
    ).first()

    if not subscription:
        subscription = create_free_subscription_for_user(db, user_id)

    return subscription


def get_user_permissions(db, user_id: int):
    subscription = get_user_subscription(db, user_id)

    plan = db.query(Plan).filter(
        Plan.name == subscription.plan
    ).first()

    if not plan:
        return {}

    permissions = db.query(PlanPermission).filter(
        PlanPermission.plan_id == plan.id
    ).first()

    if not permissions:
        return {}

    return {
        "plan": subscription.plan,
        "status": subscription.status,
        "trial": subscription.trial,
        "trial_end": subscription.trial_end,
        "max_companies": plan.max_companies,
        "max_users": plan.max_users,
        "finance": permissions.finance,
        "customer": permissions.customer,
        "compliance": permissions.compliance,
        "cyber": permissions.cyber,
        "assistant": permissions.assistant,
        "reports": permissions.reports,
        "timeline": permissions.timeline,
        "import_data": permissions.import_data,
        "openai": permissions.openai,
        "osint": permissions.osint,
        "predictive": permissions.predictive,
        "agents": permissions.agents,
        "multi_company": permissions.multi_company,
        "pdf_export": permissions.pdf_export,
        "api_access": permissions.api_access,
    }


def user_has_permission(db, user_id: int, permission_name: str) -> bool:
    permissions = get_user_permissions(db, user_id)
    return bool(permissions.get(permission_name, False))