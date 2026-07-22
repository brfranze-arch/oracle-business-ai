from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, UniqueConstraint
from database import Base


class MarketplaceCategory(Base):
    __tablename__ = "marketplace_categories"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    icon = Column(String, default="▦")
    sort_order = Column(Integer, default=0)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class MarketplaceModule(Base):
    __tablename__ = "marketplace_modules"
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    category_id = Column(Integer, index=True, nullable=False)
    partner_id = Column(Integer, index=True, nullable=True)
    name = Column(String, nullable=False)
    short_description = Column(String, default="")
    description = Column(Text, default="")
    version = Column(String, default="1.0.0")
    icon = Column(String, default="◆")
    price = Column(Float, default=0.0)
    currency = Column(String, default="EUR")
    billing_type = Column(String, default="FREE", index=True)  # FREE, ONE_TIME, MONTHLY
    required_plan = Column(String, default="FREE", index=True)
    status = Column(String, default="PUBLISHED", index=True)  # DRAFT, REVIEW, PUBLISHED, SUSPENDED
    featured = Column(Boolean, default=False, index=True)
    active = Column(Boolean, default=True, index=True)
    install_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MarketplaceInstallation(Base):
    __tablename__ = "marketplace_installations"
    __table_args__ = (UniqueConstraint("user_id", "module_id", name="uq_marketplace_user_module"),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    company_id = Column(Integer, index=True, nullable=True)
    module_id = Column(Integer, index=True, nullable=False)
    status = Column(String, default="ACTIVE", index=True)
    source = Column(String, default="MARKETPLACE")
    installed_version = Column(String, default="1.0.0")
    license_key = Column(String, unique=True, index=True, nullable=False)
    installed_at = Column(DateTime, default=datetime.utcnow)
    uninstalled_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MarketplaceEvent(Base):
    __tablename__ = "marketplace_events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    module_id = Column(Integer, index=True, nullable=False)
    event_type = Column(String, index=True, nullable=False)
    details = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
