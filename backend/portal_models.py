from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class CustomerPortalProfile(Base):
    __tablename__ = "customer_portal_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    company_name = Column(String, default="")
    phone = Column(String, default="")
    job_title = Column(String, default="")
    preferred_language = Column(String, default="it")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
