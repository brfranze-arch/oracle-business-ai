from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from database import Base


class PortalLicense(Base):
    __tablename__ = "portal_licenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True, nullable=False)
    license_key = Column(String, unique=True, index=True, nullable=False)
    edition = Column(String, default="SAAS_CLOUD")
    plan = Column(String, default="FREE")
    status = Column(String, default="active")
    max_seats = Column(Integer, default=1)
    max_companies = Column(Integer, default=1)
    current_version = Column(String, default="1.0.0-RC1")
    starts_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PortalLicenseActivation(Base):
    __tablename__ = "portal_license_activations"

    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, index=True, nullable=False)
    device_name = Column(String, default="Browser")
    device_fingerprint = Column(String, index=True, nullable=False)
    ip_address = Column(String, default="")
    active = Column(Boolean, default=True)
    activated_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow)


class PortalDownload(Base):
    __tablename__ = "portal_downloads"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="DOCUMENTATION")
    file_name = Column(String, nullable=False)
    storage_path = Column(Text, nullable=False)
    version = Column(String, default="1.0.0")
    min_plan = Column(String, default="FREE")
    required_edition = Column(String, default="ANY")
    size_bytes = Column(Integer, default=0)
    checksum_sha256 = Column(String, default="")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PortalRelease(Base):
    __tablename__ = "portal_releases"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True, nullable=False)
    channel = Column(String, default="stable")
    status = Column(String, default="available")
    title = Column(String, default="")
    summary = Column(Text, default="")
    changelog = Column(Text, default="")
    min_plan = Column(String, default="FREE")
    published_at = Column(DateTime, default=datetime.utcnow)


class PortalDownloadToken(Base):
    __tablename__ = "portal_download_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    download_id = Column(Integer, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PortalDownloadLog(Base):
    __tablename__ = "portal_download_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    download_id = Column(Integer, index=True, nullable=False)
    file_name = Column(String, nullable=False)
    ip_address = Column(String, default="")
    downloaded_at = Column(DateTime, default=datetime.utcnow)
