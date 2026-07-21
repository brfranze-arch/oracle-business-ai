from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, UniqueConstraint
from database import Base


class PartnerProfile(Base):
    __tablename__ = "partner_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    company_name = Column(String, default="")
    vat_number = Column(String, default="")
    phone = Column(String, default="")
    website = Column(String, default="")
    notes = Column(Text, default="")
    referral_code = Column(String, unique=True, index=True, nullable=False)
    level = Column(String, default="SILVER", index=True)
    status = Column(String, default="PENDING", index=True)
    commission_rate = Column(Float, default=10.0)
    active = Column(Boolean, default=False)
    approved_by_user_id = Column(Integer, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PartnerCustomer(Base):
    __tablename__ = "partner_customers"
    __table_args__ = (UniqueConstraint("customer_user_id", name="uq_partner_customer_user"),)
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, index=True, nullable=False)
    customer_user_id = Column(Integer, index=True, nullable=False)
    source = Column(String, default="REFERRAL")
    status = Column(String, default="ACTIVE", index=True)
    attributed_at = Column(DateTime, default=datetime.utcnow)


class PartnerCommission(Base):
    __tablename__ = "partner_commissions"
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, index=True, nullable=False)
    customer_user_id = Column(Integer, index=True, nullable=True)
    external_reference = Column(String, index=True, nullable=True)
    description = Column(String, default="Commissione abbonamento")
    gross_amount = Column(Float, default=0.0)
    commission_rate = Column(Float, default=0.0)
    commission_amount = Column(Float, default=0.0)
    currency = Column(String, default="EUR")
    status = Column(String, default="EARNED", index=True)
    earned_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PartnerPayout(Base):
    __tablename__ = "partner_payouts"
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, index=True, nullable=False)
    amount = Column(Float, default=0.0)
    currency = Column(String, default="EUR")
    status = Column(String, default="REQUESTED", index=True)
    method = Column(String, default="BANK_TRANSFER")
    note = Column(Text, default="")
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
