from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, index=True)
    name = Column(String, index=True)
    sector = Column(String)
    country = Column(String)
    domain = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Revenue(Base):
    __tablename__ = "revenues"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    customer_id = Column(Integer, nullable=True, index=True)
    amount = Column(Float)
    payment_method = Column(String)
    category = Column(String)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class AiInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    module = Column(String)
    title = Column(String)
    message = Column(Text)
    score = Column(Float)
    level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class BusinessHealthReport(Base):
    __tablename__ = "business_health_reports"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    health_score = Column(Float)
    level = Column(String)
    revenue_total = Column(Float)
    operations_count = Column(Integer)
    main_strength = Column(Text)
    main_risk = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    name = Column(String, index=True)
    email = Column(String)
    phone = Column(String)
    customer_type = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerInsight(Base):
    __tablename__ = "customer_insights"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    customer_score = Column(Float)
    level = Column(String)
    top_customer_name = Column(String)
    top_customer_revenue = Column(Float)
    customers_count = Column(Integer)
    message = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplianceItem(Base):
    __tablename__ = "compliance_items"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    title = Column(String)
    item_type = Column(String)
    status = Column(String)
    due_date = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ComplianceInsight(Base):
    __tablename__ = "compliance_insights"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    compliance_score = Column(Float)
    level = Column(String)
    total_items = Column(Integer)
    completed_items = Column(Integer)
    pending_items = Column(Integer)
    expired_items = Column(Integer)
    message = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    password_hash = Column(String)
    role = Column(String, default="client")
    created_at = Column(DateTime, default=datetime.utcnow)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class OracleMemory(Base):
    __tablename__ = "oracle_memories"

    id = Column(Integer, primary_key=True, index=True)

    company_id = Column(Integer, index=True)

    question = Column(Text)

    answer = Column(Text)

    oracle_score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

class OracleScoreSnapshot(Base):
    __tablename__ = "oracle_score_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    oracle_score = Column(Float)
    finance_score = Column(Float)
    business_health_score = Column(Float)
    customer_score = Column(Float)
    compliance_score = Column(Float)
    cyber_score = Column(Float)

    level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class CyberAsset(Base):
    __tablename__ = "cyber_assets"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    asset_type = Column(String)  # domain, subdomain, ip, email_domain, cloud
    value = Column(String, index=True)

    provider = Column(String)  # AWS, Azure, Cloudflare, Google Cloud, unknown
    technology_stack = Column(Text)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


class CyberScan(Base):
    __tablename__ = "cyber_scans"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    asset_id = Column(Integer, index=True)

    scan_type = Column(String)  # exposure, ssl, headers, dns, cve, prediction
    status = Column(String)  # completed, failed, pending
    cyber_score = Column(Float)
    level = Column(String)

    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class CyberFinding(Base):
    __tablename__ = "cyber_findings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    scan_id = Column(Integer, index=True)
    asset_id = Column(Integer, index=True)

    title = Column(String)
    category = Column(String)  # ssl, dns, headers, cve, exposure, email_security
    severity = Column(String)  # low, medium, high, critical
    description = Column(Text)
    recommendation = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


class CyberThreat(Base):
    __tablename__ = "cyber_threats"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    source = Column(String)  # NVD, CISA KEV, OSINT, internal
    threat_type = Column(String)  # cve, kev, ransomware, phishing, botnet
    title = Column(String)
    description = Column(Text)

    cve_id = Column(String)
    severity = Column(String)
    score = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)


class CyberPrediction(Base):
    __tablename__ = "cyber_predictions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    cyber_score = Column(Float)
    level = Column(String)

    attack_probability_30d = Column(Float)
    attack_probability_90d = Column(Float)

    trend = Column(String)  # improving, stable, worsening
    main_risk = Column(Text)
    recommendation = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)


class CyberScoreSnapshot(Base):
    __tablename__ = "cyber_score_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    cyber_score = Column(Float)
    exposure_score = Column(Float)
    vulnerability_score = Column(Float)
    threat_score = Column(Float)
    prediction_score = Column(Float)

    level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    file_name = Column(String)
    import_type = Column(String)  # revenues, customers, compliance
    status = Column(String)  # completed, failed

    rows_processed = Column(Integer, default=0)
    rows_created = Column(Integer, default=0)
    errors = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)