from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, UniqueConstraint
from database import Base


class WhiteLabelBrand(Base):
    __tablename__ = "white_label_brands"
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, unique=True, nullable=False, index=True)
    brand_name = Column(String(180), default="Orizzonte360", nullable=False)
    tagline = Column(String(255), default="La tua azienda. Vista a 360°.")
    logo_url = Column(Text, default="")
    favicon_url = Column(Text, default="")
    primary_color = Column(String(16), default="#2563EB")
    secondary_color = Column(String(16), default="#0F172A")
    accent_color = Column(String(16), default="#22C55E")
    background_color = Column(String(16), default="#F8FAFC")
    support_email = Column(String(255), default="support@orizzonte360.it")
    support_phone = Column(String(80), default="")
    website_url = Column(Text, default="https://orizzonte360.it")
    footer_text = Column(String(500), default="Powered by Orizzonte360")
    privacy_url = Column(Text, default="https://orizzonte360.it/privacy.html")
    terms_url = Column(Text, default="https://orizzonte360.it/termini.html")
    hide_powered_by = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WhiteLabelDomain(Base):
    __tablename__ = "white_label_domains"
    __table_args__ = (UniqueConstraint("hostname", name="uq_white_label_hostname"),)
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, nullable=False, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    portal_type = Column(String(30), default="app")
    verified = Column(Boolean, default=False)
    verification_token = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
