from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime

from database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    owner_user_id = Column(Integer, index=True)
    plan = Column(String, default="FREE")
    created_at = Column(DateTime, default=datetime.utcnow)


class TenantMember(Base):
    __tablename__ = "tenant_members"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, index=True)
    user_id = Column(Integer, index=True)
    role = Column(String, default="owner")  # owner, admin, member, viewer
    created_at = Column(DateTime, default=datetime.utcnow)