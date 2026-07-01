from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text

from database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    price_month = Column(Float, default=0)
    price_year = Column(Float, default=0)

    max_companies = Column(Integer, default=1)
    max_users = Column(Integer, default=1)

    description = Column(Text)
    active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class PlanPermission(Base):
    __tablename__ = "plan_permissions"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, index=True)

    finance = Column(Boolean, default=False)
    customer = Column(Boolean, default=False)
    compliance = Column(Boolean, default=False)
    cyber = Column(Boolean, default=False)
    assistant = Column(Boolean, default=False)
    reports = Column(Boolean, default=False)
    timeline = Column(Boolean, default=False)
    import_data = Column(Boolean, default=False)

    openai = Column(Boolean, default=False)
    osint = Column(Boolean, default=False)
    predictive = Column(Boolean, default=False)
    agents = Column(Boolean, default=False)

    multi_company = Column(Boolean, default=False)
    pdf_export = Column(Boolean, default=False)
    api_access = Column(Boolean, default=False)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, index=True)
    plan = Column(String, default="FREE")
    status = Column(String, default="active")

    trial = Column(Boolean, default=True)
    trial_end = Column(DateTime)

    provider = Column(String, default="internal")
    provider_customer = Column(String)
    provider_subscription = Column(String)

    renewal_date = Column(DateTime)
    cancel_date = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    subscription_id = Column(Integer, index=True)

    provider = Column(String, default="internal")
    invoice_number = Column(String)

    amount = Column(Float, default=0)
    currency = Column(String, default="EUR")
    status = Column(String, default="paid")

    invoice_url = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


class PaymentMethod(Base):
    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)

    subscription_id = Column(Integer, index=True)

    provider = Column(String, default="internal")
    type = Column(String, default="card")

    last4 = Column(String)
    brand = Column(String)
    exp_month = Column(Integer)
    exp_year = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)