from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from database import Base


class OsintScan(Base):
    __tablename__ = "osint_scans"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    domain = Column(String, index=True)

    dns_status = Column(String, default="unknown")
    ssl_status = Column(String, default="unknown")
    http_status = Column(String, default="unknown")

    exposure_score = Column(Float, default=50)
    summary = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


class OsintFinding(Base):
    __tablename__ = "osint_findings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    scan_id = Column(Integer, index=True)

    title = Column(String)
    category = Column(String)
    severity = Column(String)
    description = Column(Text)
    recommendation = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)