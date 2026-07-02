import billing_models
from tenant_models import Tenant, TenantMember
from tenant_engine import (
    create_default_tenant_for_user,
    get_user_tenants,
    user_can_access_tenant
)
from stripe_engine import StripeEngine
from billing_models import Plan, PlanPermission, Subscription, Invoice, PaymentMethod
from billing_engine import (
    seed_default_plans,
    create_free_subscription_for_user,
    get_user_subscription,
    get_user_permissions,
    user_has_permission
)
from billing_webhook import process_stripe_event
from fastapi import FastAPI, Depends, Header, UploadFile, File, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal

import pandas as pd
import os
import tempfile

from models import (
    Company,
    Revenue,
    AiInsight,
    BusinessHealthReport,
    Customer,
    CustomerInsight,
    ComplianceItem,
    ComplianceInsight,
    User,
    UserSession,
    OracleMemory,
    OracleScoreSnapshot,
    CyberAsset,
    CyberScan,
    CyberFinding,
    CyberThreat,
    CyberPrediction,
    CyberScoreSnapshot,
    ImportJob
)
from ai_engine import (
    analyze_finance,
    calculate_oracle_score,
    analyze_business_health,
    analyze_customers,
    analyze_compliance,
    oracle_assistant_answer,
    analyze_cyber_risk
)

from auth_utils import hash_password, verify_password, generate_token

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    seed_default_plans(db)

app = FastAPI(title="Oracle Business AI")

security = HTTPBearer(auto_error=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if not credentials:
        return None

    token = credentials.credentials

    session = db.query(UserSession).filter(
        UserSession.token == token
    ).first()

    if not session:
        return None

    user = db.query(User).filter(
        User.id == session.user_id
    ).first()

    return user

@app.post("/api/auth/register")
def register(
    name: str,
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    existing = db.query(User).filter(User.email == email).first()

    if existing:
        return {"error": "Email già registrata"}

    user = User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role="client"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    create_free_subscription_for_user(db, user.id)
    create_default_tenant_for_user(db, user)

    token = generate_token()

    session = UserSession(
        user_id=user.id,
        token=token
    )

    db.add(session)
    db.commit()

    return {
        "message": "Registrazione completata",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }


@app.post("/api/auth/login")
def login(
    email: str,
    password: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return {"error": "Credenziali non valide"}

    if not verify_password(password, user.password_hash):
        return {"error": "Credenziali non valide"}

    token = generate_token()

    session = UserSession(
        user_id=user.id,
        token=token
    )

    db.add(session)
    db.commit()

    return {
        "message": "Login completato",
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }


@app.get("/api/auth/me")
def me(current_user: User = Depends(get_current_user)):
    if not current_user:
        return {"error": "Non autenticato"}

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role
    }

@app.get("/")
def home():
    return {
        "name": "Oracle Business AI",
        "status": "online",
        "version": "0.1",
        "modules": [
            "Finance Oracle AI",
            "Cyber Oracle AI",
            "Business Health AI"
        ]
    }


@app.post("/api/companies")
def create_company(
    name: str,
    sector: str,
    country: str,
    domain: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = Company(
        owner_id=current_user.id,
        name=name,
        sector=sector,
        country=country,
        domain=domain
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    return company

@app.get("/api/companies")
def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    if current_user.role == "admin":
        return db.query(Company).all()

    return db.query(Company).filter(
        Company.owner_id == current_user.id
    ).all()

@app.post("/api/revenues")
def add_revenue(
    company_id: int,
    amount: float,
    payment_method: str,
    category: str,
    customer_id: int = None,
    note: str = "",
    db: Session = Depends(get_db)
):
    revenue = Revenue(
        company_id=company_id,
        customer_id=customer_id,
        amount=amount,
        payment_method=payment_method.lower(),
        category=category,
        note=note
    )

    db.add(revenue)
    db.commit()
    db.refresh(revenue)

    return revenue


@app.get("/api/revenues/{company_id}")
def get_revenues(company_id: int, db: Session = Depends(get_db)):
    return db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).order_by(Revenue.created_at.desc()).all()


@app.get("/api/finance-summary/{company_id}")
def finance_summary(company_id: int, db: Session = Depends(get_db)):
    revenues = db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).all()

    total = sum(r.amount for r in revenues)
    cash = sum(r.amount for r in revenues if r.payment_method == "contanti")
    pos = sum(r.amount for r in revenues if r.payment_method == "pos")
    bank = sum(r.amount for r in revenues if r.payment_method == "bonifico")
    digital = sum(r.amount for r in revenues if r.payment_method == "digitale")

    return {
        "company_id": company_id,
        "total": total,
        "cash": cash,
        "pos": pos,
        "bank": bank,
        "digital": digital,
        "count": len(revenues)
    }


@app.post("/api/ai/analyze-finance/{company_id}")
def ai_analyze_finance(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return {"error": "Azienda non trovata"}

    revenues = db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).all()

    result = analyze_finance(company, revenues)

    insight = AiInsight(
        company_id=company_id,
        module="finance",
        title=result["title"],
        message=result["message"],
        score=result["score"],
        level=result["level"]
    )

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return insight


@app.get("/api/insights/{company_id}")
def get_insights(company_id: int, db: Session = Depends(get_db)):
    return db.query(AiInsight).filter(
        AiInsight.company_id == company_id
    ).order_by(AiInsight.created_at.desc()).all()

@app.get("/api/oracle-score/{company_id}")
def oracle_score(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        return {"error": "Azienda non trovata"}

    if current_user.role != "admin" and company.owner_id != current_user.id:
        return {"error": "Non autorizzato"}

    revenues = db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).all()

    insights = db.query(AiInsight).filter(
        AiInsight.company_id == company_id
    ).all()

    health_reports = db.query(BusinessHealthReport).filter(
        BusinessHealthReport.company_id == company_id
    ).order_by(BusinessHealthReport.created_at.desc()).all()

    customer_insights = db.query(CustomerInsight).filter(
        CustomerInsight.company_id == company_id
    ).order_by(CustomerInsight.created_at.desc()).all()

    compliance_insights = db.query(ComplianceInsight).filter(
        ComplianceInsight.company_id == company_id
    ).order_by(ComplianceInsight.created_at.desc()).all()

    cyber_predictions = db.query(CyberPrediction).filter(
        CyberPrediction.company_id == company_id
    ).order_by(CyberPrediction.created_at.desc()).all()

    result = calculate_oracle_score(
       company,
       revenues,
       insights,
       health_reports,
       customer_insights,
       compliance_insights,
       cyber_predictions
    )

    snapshot = OracleScoreSnapshot(
        company_id=company_id,
        oracle_score=result["oracle_score"],
        finance_score=result["finance_score"],
        business_health_score=result["business_health_score"],
        customer_score=result["customer_score"],
        compliance_score=result["compliance_score"],
        cyber_score=result["cyber_score"],
        level=result["level"]
    )

    db.add(snapshot)
    db.commit()

    return result

@app.post("/api/business-health/analyze/{company_id}")
def analyze_business_health_api(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return {"error": "Azienda non trovata"}

    revenues = db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).all()

    insights = db.query(AiInsight).filter(
        AiInsight.company_id == company_id
    ).all()

    result = analyze_business_health(company, revenues, insights)

    report = BusinessHealthReport(
        company_id=company_id,
        health_score=result["health_score"],
        level=result["level"],
        revenue_total=result["revenue_total"],
        operations_count=result["operations_count"],
        main_strength=result["main_strength"],
        main_risk=result["main_risk"],
        recommendation=result["recommendation"]
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


@app.get("/api/business-health/{company_id}")
def get_business_health_reports(company_id: int, db: Session = Depends(get_db)):
    return db.query(BusinessHealthReport).filter(
        BusinessHealthReport.company_id == company_id
    ).order_by(BusinessHealthReport.created_at.desc()).all()

@app.post("/api/customers")
def create_customer(
    company_id: int,
    name: str,
    email: str = "",
    phone: str = "",
    customer_type: str = "",
    notes: str = "",
    db: Session = Depends(get_db)
):
    customer = Customer(
        company_id=company_id,
        name=name,
        email=email,
        phone=phone,
        customer_type=customer_type,
        notes=notes
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


@app.get("/api/customers/{company_id}")
def get_customers(company_id: int, db: Session = Depends(get_db)):
    return db.query(Customer).filter(
        Customer.company_id == company_id
    ).all()


@app.post("/api/customer-ai/{company_id}")
def customer_ai(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        return {"error": "Azienda non trovata"}

    customers = db.query(Customer).filter(
        Customer.company_id == company_id
    ).all()

    revenues = db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).all()

    result = analyze_customers(
        company,
        customers,
        revenues
    )

    insight = CustomerInsight(
        company_id=company_id,
        customer_score=result["customer_score"],
        level=result["level"],
        top_customer_name=result["top_customer_name"],
        top_customer_revenue=result["top_customer_revenue"],
        customers_count=result["customers_count"],
        message=result["message"],
        recommendation=result["recommendation"]
    )

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return insight


@app.get("/api/customer-insights/{company_id}")
def customer_insights(company_id: int, db: Session = Depends(get_db)):
    return db.query(CustomerInsight).filter(
        CustomerInsight.company_id == company_id
    ).order_by(
        CustomerInsight.created_at.desc()
    ).all()

@app.post("/api/compliance-items")
def create_compliance_item(
    company_id: int,
    title: str,
    item_type: str,
    status: str,
    due_date: str = "",
    notes: str = "",
    db: Session = Depends(get_db)
):
    item = ComplianceItem(
        company_id=company_id,
        title=title,
        item_type=item_type,
        status=status,
        due_date=due_date,
        notes=notes
    )

    db.add(item)
    db.commit()
    db.refresh(item)

    return item


@app.get("/api/compliance-items/{company_id}")
def get_compliance_items(company_id: int, db: Session = Depends(get_db)):
    return db.query(ComplianceItem).filter(
        ComplianceItem.company_id == company_id
    ).all()


@app.post("/api/compliance-ai/{company_id}")
def compliance_ai(company_id: int, db: Session = Depends(get_db)):
    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        return {"error": "Azienda non trovata"}

    items = db.query(ComplianceItem).filter(
        ComplianceItem.company_id == company_id
    ).all()

    result = analyze_compliance(company, items)

    insight = ComplianceInsight(
        company_id=company_id,
        compliance_score=result["compliance_score"],
        level=result["level"],
        total_items=result["total_items"],
        completed_items=result["completed_items"],
        pending_items=result["pending_items"],
        expired_items=result["expired_items"],
        message=result["message"],
        recommendation=result["recommendation"]
    )

    db.add(insight)
    db.commit()
    db.refresh(insight)

    return insight


@app.get("/api/compliance-insights/{company_id}")
def compliance_insights(company_id: int, db: Session = Depends(get_db)):
    return db.query(ComplianceInsight).filter(
        ComplianceInsight.company_id == company_id
    ).order_by(
        ComplianceInsight.created_at.desc()
    ).all()

@app.post("/api/oracle-assistant/{company_id}")
def oracle_assistant(
    company_id: int,
    question: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        return {"error": "Azienda non trovata"}

    if current_user.role != "admin" and company.owner_id != current_user.id:
        return {"error": "Non autorizzato"}

    revenues = db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).all()

    insights = db.query(AiInsight).filter(
        AiInsight.company_id == company_id
    ).all()

    health_reports = db.query(BusinessHealthReport).filter(
        BusinessHealthReport.company_id == company_id
    ).order_by(BusinessHealthReport.created_at.desc()).all()

    customer_insights = db.query(CustomerInsight).filter(
        CustomerInsight.company_id == company_id
    ).order_by(CustomerInsight.created_at.desc()).all()

    compliance_insights = db.query(ComplianceInsight).filter(
        ComplianceInsight.company_id == company_id
    ).order_by(ComplianceInsight.created_at.desc()).all()

    cyber_predictions = db.query(CyberPrediction).filter(
        CyberPrediction.company_id == company_id
    ).order_by(CyberPrediction.created_at.desc()).all()

    cyber_findings = db.query(CyberFinding).filter(
        CyberFinding.company_id == company_id
    ).order_by(CyberFinding.created_at.desc()).all()

    cyber_threats = db.query(CyberThreat).filter(
        CyberThreat.company_id == company_id
    ).order_by(CyberThreat.created_at.desc()).all()

    cyber_assets = db.query(CyberAsset).filter(
        CyberAsset.company_id == company_id
    ).all()

    customers = db.query(Customer).filter(
        Customer.company_id == company_id
    ).all()

    oracle_score_data = calculate_oracle_score(
        company,
        revenues,
        insights,
        health_reports,
        customer_insights,
        compliance_insights
    )

    answer = oracle_assistant_answer(
        company,
        question,
        oracle_score_data,
        revenues,
        customers,
        compliance_insights,
        cyber_predictions,
        cyber_findings,
        cyber_threats,
        cyber_assets
    )

    memory = OracleMemory(
        company_id=company_id,
        question=question,
        answer=answer,
        oracle_score=oracle_score_data["oracle_score"]
    )

    db.add(memory)
    db.commit()

    return {
        "company_id": company_id,
        "question": question,
        "answer": answer,
        "oracle_score": oracle_score_data
    }

@app.get("/api/oracle-memory/{company_id}")
def get_oracle_memory(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    memories = db.query(OracleMemory).filter(
        OracleMemory.company_id == company_id
    ).order_by(
        OracleMemory.created_at.desc()
    ).limit(100).all()

    return memories

@app.get("/api/oracle-timeline/{company_id}")
def oracle_timeline(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        return {"error": "Azienda non trovata"}

    if current_user.role != "admin" and company.owner_id != current_user.id:
        return {"error": "Non autorizzato"}

    snapshots = db.query(OracleScoreSnapshot).filter(
        OracleScoreSnapshot.company_id == company_id
    ).order_by(
        OracleScoreSnapshot.created_at.asc()
    ).limit(100).all()

    return snapshots

@app.get("/api/revenue-analytics/{company_id}")
def revenue_analytics(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return {"error": "Azienda non trovata"}

    if current_user.role != "admin" and company.owner_id != current_user.id:
        return {"error": "Non autorizzato"}

    revenues = db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).order_by(Revenue.created_at.asc()).all()

    trend = []
    running_total = 0

    for index, r in enumerate(revenues):
        running_total += r.amount
        trend.append({
            "label": f"#{index + 1}",
            "amount": r.amount,
            "total": running_total,
            "payment_method": r.payment_method,
            "category": r.category
        })

    payment_mix = {}
    category_mix = {}

    for r in revenues:
        payment_mix[r.payment_method] = payment_mix.get(r.payment_method, 0) + r.amount
        category_mix[r.category] = category_mix.get(r.category, 0) + r.amount

    return {
        "company_id": company_id,
        "total_revenue": sum(r.amount for r in revenues),
        "operations": len(revenues),
        "trend": trend,
        "payment_mix": payment_mix,
        "category_mix": category_mix
    }

@app.post("/api/cyber-assets")
def create_cyber_asset(
    company_id: int,
    asset_type: str,
    value: str,
    provider: str = "unknown",
    technology_stack: str = "",
    notes: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return {"error": "Azienda non trovata"}

    if current_user.role != "admin" and company.owner_id != current_user.id:
        return {"error": "Non autorizzato"}

    asset = CyberAsset(
        company_id=company_id,
        asset_type=asset_type,
        value=value,
        provider=provider,
        technology_stack=technology_stack,
        notes=notes
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    return asset


@app.get("/api/cyber-assets/{company_id}")
def get_cyber_assets(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    return db.query(CyberAsset).filter(
        CyberAsset.company_id == company_id
    ).all()


@app.post("/api/cyber-findings")
def create_cyber_finding(
    company_id: int,
    asset_id: int,
    title: str,
    category: str,
    severity: str,
    description: str,
    recommendation: str,
    scan_id: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    finding = CyberFinding(
        company_id=company_id,
        scan_id=scan_id,
        asset_id=asset_id,
        title=title,
        category=category,
        severity=severity,
        description=description,
        recommendation=recommendation
    )

    db.add(finding)
    db.commit()
    db.refresh(finding)

    return finding


@app.get("/api/cyber-findings/{company_id}")
def get_cyber_findings(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    return db.query(CyberFinding).filter(
        CyberFinding.company_id == company_id
    ).order_by(CyberFinding.created_at.desc()).all()


@app.post("/api/cyber-threats")
def create_cyber_threat(
    company_id: int,
    source: str,
    threat_type: str,
    title: str,
    description: str,
    severity: str,
    score: float,
    cve_id: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    threat = CyberThreat(
        company_id=company_id,
        source=source,
        threat_type=threat_type,
        title=title,
        description=description,
        cve_id=cve_id,
        severity=severity,
        score=score
    )

    db.add(threat)
    db.commit()
    db.refresh(threat)

    return threat


@app.get("/api/cyber-threats/{company_id}")
def get_cyber_threats(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    return db.query(CyberThreat).filter(
        CyberThreat.company_id == company_id
    ).order_by(CyberThreat.created_at.desc()).all()


@app.post("/api/cyber-ai/{company_id}")
def cyber_ai(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return {"error": "Azienda non trovata"}

    if current_user.role != "admin" and company.owner_id != current_user.id:
        return {"error": "Non autorizzato"}

    assets = db.query(CyberAsset).filter(
        CyberAsset.company_id == company_id
    ).all()

    findings = db.query(CyberFinding).filter(
        CyberFinding.company_id == company_id
    ).all()

    threats = db.query(CyberThreat).filter(
        CyberThreat.company_id == company_id
    ).all()

    result = analyze_cyber_risk(company, assets, findings, threats)

    prediction = CyberPrediction(
        company_id=company_id,
        cyber_score=result["cyber_score"],
        level=result["level"],
        attack_probability_30d=result["attack_probability_30d"],
        attack_probability_90d=result["attack_probability_90d"],
        trend=result["trend"],
        main_risk=result["main_risk"],
        recommendation=result["recommendation"]
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    scan = CyberScan(
        company_id=company_id,
        asset_id=assets[0].id if assets else 0,
        scan_type="prediction",
        status="completed",
        cyber_score=result["cyber_score"],
        level=result["level"],
        summary=result["main_risk"]
    )

    db.add(scan)

    snapshot = CyberScoreSnapshot(
        company_id=company_id,
        cyber_score=result["cyber_score"],
        exposure_score=result["exposure_score"],
        vulnerability_score=result["vulnerability_score"],
        threat_score=result["threat_score"],
        prediction_score=result["prediction_score"],
        level=result["level"]
    )

    db.add(snapshot)
    db.commit()

    return {
        "company_id": company_id,
        "cyber_score": result["cyber_score"],
        "level": result["level"],
        "exposure_score": result["exposure_score"],
        "vulnerability_score": result["vulnerability_score"],
        "threat_score": result["threat_score"],
        "prediction_score": result["prediction_score"],
        "attack_probability_30d": result["attack_probability_30d"],
        "attack_probability_90d": result["attack_probability_90d"],
        "trend": result["trend"],
        "main_risk": result["main_risk"],
        "strengths": result["strengths"],
        "risks": result["risks"],
        "recommendation": result["recommendation"]
    }


@app.get("/api/cyber-predictions/{company_id}")
def cyber_predictions(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    return db.query(CyberPrediction).filter(
        CyberPrediction.company_id == company_id
    ).order_by(CyberPrediction.created_at.desc()).all()


@app.get("/api/cyber-timeline/{company_id}")
def cyber_timeline(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    return db.query(CyberScoreSnapshot).filter(
        CyberScoreSnapshot.company_id == company_id
    ).order_by(CyberScoreSnapshot.created_at.asc()).all()

def normalize_column(name: str) -> str:
    return str(name).strip().lower().replace(" ", "_").replace("-", "_")


def find_column(columns, possible_names):
    normalized = {normalize_column(c): c for c in columns}

    for name in possible_names:
        key = normalize_column(name)
        if key in normalized:
            return normalized[key]

    return None


def read_import_file(file_path: str, filename: str):
    lower = filename.lower()

    if lower.endswith(".csv"):
        return pd.read_csv(file_path)

    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return pd.read_excel(file_path)

    raise ValueError("Formato file non supportato. Usa CSV o Excel.")

@app.post("/api/import/revenues/{company_id}")
async def import_revenues(
    company_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return {"error": "Azienda non trovata"}

    if current_user.role != "admin" and company.owner_id != current_user.id:
        return {"error": "Non autorizzato"}

    temp_path = None

    try:
        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            temp_path = tmp.name

        df = read_import_file(temp_path, file.filename)

        amount_col = find_column(df.columns, ["amount", "importo", "totale", "valore"])
        method_col = find_column(df.columns, ["payment_method", "metodo", "metodo_pagamento", "pagamento"])
        category_col = find_column(df.columns, ["category", "categoria", "tipo"])
        note_col = find_column(df.columns, ["note", "nota", "descrizione"])
        customer_col = find_column(df.columns, ["customer", "cliente", "nome_cliente", "customer_name"])

        if not amount_col:
            return {"error": "Colonna importo non trovata"}

        rows_created = 0
        errors = []

        for index, row in df.iterrows():
            try:
                amount = float(row[amount_col])

                payment_method = "digitale"
                if method_col and not pd.isna(row[method_col]):
                    payment_method = str(row[method_col]).strip().lower()

                category = "import"
                if category_col and not pd.isna(row[category_col]):
                    category = str(row[category_col]).strip().lower()

                note = ""
                if note_col and not pd.isna(row[note_col]):
                    note = str(row[note_col])

                customer_id = None

                if customer_col and not pd.isna(row[customer_col]):
                    customer_name = str(row[customer_col]).strip()

                    customer = db.query(Customer).filter(
                        Customer.company_id == company_id,
                        Customer.name == customer_name
                    ).first()

                    if not customer:
                        customer = Customer(
                            company_id=company_id,
                            name=customer_name,
                            email="",
                            phone="",
                            customer_type="import",
                            notes="Creato da import automatico"
                        )
                        db.add(customer)
                        db.commit()
                        db.refresh(customer)

                    customer_id = customer.id

                revenue = Revenue(
                    company_id=company_id,
                    customer_id=customer_id,
                    amount=amount,
                    payment_method=payment_method,
                    category=category,
                    note=note
                )

                db.add(revenue)
                rows_created += 1

            except Exception as e:
                errors.append(f"Riga {index + 1}: {str(e)}")

        job = ImportJob(
            company_id=company_id,
            file_name=file.filename,
            import_type="revenues",
            status="completed" if not errors else "completed_with_errors",
            rows_processed=len(df),
            rows_created=rows_created,
            errors="\n".join(errors)
        )

        db.add(job)
        db.commit()

        return {
            "message": "Import entrate completato",
            "rows_processed": len(df),
            "rows_created": rows_created,
            "errors": errors
        }

    except Exception as e:
        job = ImportJob(
            company_id=company_id,
            file_name=file.filename,
            import_type="revenues",
            status="failed",
            rows_processed=0,
            rows_created=0,
            errors=str(e)
        )
        db.add(job)
        db.commit()

        return {"error": str(e)}

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/api/import/history/{company_id}")
def import_history(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    return db.query(ImportJob).filter(
        ImportJob.company_id == company_id
    ).order_by(ImportJob.created_at.desc()).all()

@app.get("/api/executive-dashboard/{company_id}")
def executive_dashboard(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(
        Company.id == company_id
    ).first()

    if not company:
        return {"error": "Azienda non trovata"}

    revenues = db.query(Revenue).filter(
        Revenue.company_id == company_id
    ).all()

    customers = db.query(Customer).filter(
        Customer.company_id == company_id
    ).all()

    customer_insights = db.query(CustomerInsight).filter(
        CustomerInsight.company_id == company_id
    ).order_by(CustomerInsight.created_at.desc()).all()

    compliance_items = db.query(ComplianceItem).filter(
        ComplianceItem.company_id == company_id
    ).all()

    cyber_predictions = db.query(CyberPrediction).filter(
        CyberPrediction.company_id == company_id
    ).order_by(CyberPrediction.created_at.desc()).all()

    oracle_score_data = calculate_oracle_score(
        company,
        revenues,
        [],
        [],
        customer_insights,
        [],
        cyber_predictions
    )

    total_revenue = sum(r.amount for r in revenues)

    top_customer = "N/A"

    if customer_insights:
        top_customer = customer_insights[0].top_customer_name

    cyber_score = 50
    attack30 = 0
    attack90 = 0

    if cyber_predictions:
        cyber_score = cyber_predictions[0].cyber_score
        attack30 = cyber_predictions[0].attack_probability_30d
        attack90 = cyber_predictions[0].attack_probability_90d

    return {
        "company_name": company.name,
        "oracle_score": oracle_score_data["oracle_score"],
        "oracle_level": oracle_score_data["level"],
        "total_revenue": total_revenue,
        "operations": len(revenues),

        "customers": len(customers),
        "top_customer": top_customer,

        "compliance_items": len(compliance_items),

        "cyber_score": cyber_score,
        "attack_probability_30d": attack30,
        "attack_probability_90d": attack90,

        "suggestions": oracle_score_data["suggestions"],
        "risks": oracle_score_data["risks"]
    }

@app.get("/api/daily-brief/{company_id}")
def daily_brief(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return {"error": "Azienda non trovata"}

    revenues = db.query(Revenue).filter(Revenue.company_id == company_id).all()
    customers = db.query(Customer).filter(Customer.company_id == company_id).all()

    customer_insights = db.query(CustomerInsight).filter(
        CustomerInsight.company_id == company_id
    ).order_by(CustomerInsight.created_at.desc()).all()

    compliance_insights = db.query(ComplianceInsight).filter(
        ComplianceInsight.company_id == company_id
    ).order_by(ComplianceInsight.created_at.desc()).all()

    cyber_predictions = db.query(CyberPrediction).filter(
        CyberPrediction.company_id == company_id
    ).order_by(CyberPrediction.created_at.desc()).all()

    oracle_score_data = calculate_oracle_score(
        company,
        revenues,
        [],
        [],
        customer_insights,
        compliance_insights,
        cyber_predictions
    )

    total_revenue = sum(r.amount for r in revenues)

    brief = []

    brief.append(f"Oracle Daily Brief per {company.name}.")
    brief.append(f"Oracle Score: {oracle_score_data['oracle_score']}/100, livello {oracle_score_data['level']}.")

    brief.append(f"Entrate registrate: €{round(total_revenue, 2)} su {len(revenues)} operazioni.")
    brief.append(f"Clienti registrati: {len(customers)}.")

    if customer_insights:
        brief.append(
            f"Customer Score: {customer_insights[0].customer_score}/100. "
            f"Top cliente: {customer_insights[0].top_customer_name}."
        )

    if compliance_insights:
        brief.append(
            f"Compliance Score: {compliance_insights[0].compliance_score}/100. "
            f"Elementi scaduti: {compliance_insights[0].expired_items}."
        )

    if cyber_predictions:
        brief.append(
            f"Cyber Score: {cyber_predictions[0].cyber_score}/100. "
            f"Probabilità attacco 30 giorni: {cyber_predictions[0].attack_probability_30d}%."
        )

    priorities = []

    if oracle_score_data["oracle_score"] < 65:
        priorities.append("Migliorare i moduli con punteggio più basso.")

    if compliance_insights and compliance_insights[0].expired_items > 0:
        priorities.append("Risolvere subito gli elementi Compliance scaduti.")

    if cyber_predictions and cyber_predictions[0].attack_probability_30d > 25:
        priorities.append("Ridurre il rischio cyber intervenendo sui finding ad alta severità.")

    if customer_insights and customer_insights[0].top_customer_revenue > total_revenue * 0.45:
        priorities.append("Ridurre la dipendenza dal cliente principale.")

    if not priorities:
        priorities.append("Continuare il monitoraggio e aggiornare i dati regolarmente.")

    return {
        "company_id": company_id,
        "company_name": company.name,
        "oracle_score": oracle_score_data["oracle_score"],
        "level": oracle_score_data["level"],
        "brief": brief,
        "priorities": priorities
    }

@app.get("/api/billing/plans")
def billing_plans(db: Session = Depends(get_db)):
    plans = db.query(Plan).filter(Plan.active == True).all()

    result = []

    for plan in plans:
        permissions = db.query(PlanPermission).filter(
            PlanPermission.plan_id == plan.id
        ).first()

        result.append({
            "id": plan.id,
            "name": plan.name,
            "price_month": plan.price_month,
            "price_year": plan.price_year,
            "max_companies": plan.max_companies,
            "max_users": plan.max_users,
            "description": plan.description,
            "permissions": {
                "finance": permissions.finance if permissions else False,
                "customer": permissions.customer if permissions else False,
                "compliance": permissions.compliance if permissions else False,
                "cyber": permissions.cyber if permissions else False,
                "assistant": permissions.assistant if permissions else False,
                "reports": permissions.reports if permissions else False,
                "timeline": permissions.timeline if permissions else False,
                "import_data": permissions.import_data if permissions else False,
                "openai": permissions.openai if permissions else False,
                "osint": permissions.osint if permissions else False,
                "predictive": permissions.predictive if permissions else False,
                "agents": permissions.agents if permissions else False,
                "multi_company": permissions.multi_company if permissions else False,
                "pdf_export": permissions.pdf_export if permissions else False,
                "api_access": permissions.api_access if permissions else False,
            }
        })

    return result


@app.get("/api/billing/me")
def billing_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    subscription = get_user_subscription(db, current_user.id)
    permissions = get_user_permissions(db, current_user.id)

    return {
        "user_id": current_user.id,
        "plan": subscription.plan,
        "status": subscription.status,
        "trial": subscription.trial,
        "trial_end": subscription.trial_end,
        "provider": subscription.provider,
        "renewal_date": subscription.renewal_date,
        "cancel_date": subscription.cancel_date,
        "permissions": permissions
    }


@app.get("/api/me/permissions")
def my_permissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    return get_user_permissions(db, current_user.id)


@app.post("/api/billing/change-plan")
def change_plan(
    plan: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    selected_plan = db.query(Plan).filter(
        Plan.name == plan.upper(),
        Plan.active == True
    ).first()

    if not selected_plan:
        return {"error": "Piano non valido"}

    subscription = get_user_subscription(db, current_user.id)
    subscription.plan = selected_plan.name
    subscription.status = "active"
    subscription.provider = "internal"

    db.commit()
    db.refresh(subscription)

    return {
        "message": "Piano aggiornato",
        "plan": subscription.plan,
        "permissions": get_user_permissions(db, current_user.id)
    }

@app.post("/api/billing/stripe-checkout")
def stripe_checkout(
    plan: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    selected_plan = db.query(Plan).filter(
        Plan.name == plan.upper(),
        Plan.active == True
    ).first()

    if not selected_plan:
        return {"error": "Piano non valido"}

    if selected_plan.name == "FREE":
        return {"error": "Il piano FREE non richiede pagamento"}

    try:
        session = StripeEngine.create_checkout_session(current_user, selected_plan.name)

        return {
            "checkout_url": session.url,
            "session_id": session.id
        }

    except Exception as e:
        return {"error": str(e)}

@app.post("/api/billing/stripe-webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = StripeEngine.construct_webhook_event(payload, sig_header)
    except Exception as e:
        return {"error": str(e)}

    return process_stripe_event(event, db)

@app.post("/api/billing/customer-portal")
def billing_customer_portal(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    subscription = get_user_subscription(db, current_user.id)

    if not subscription.provider_customer:
        return {"error": "Nessun cliente Stripe collegato"}

    try:
        session = StripeEngine.create_customer_portal(
            subscription.provider_customer
        )

        return {
            "portal_url": session.url
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/api/billing/invoices")
def billing_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    subscription = get_user_subscription(db, current_user.id)

    invoices = db.query(Invoice).filter(
        Invoice.subscription_id == subscription.id
    ).order_by(Invoice.created_at.desc()).all()

    return invoices

@app.post("/api/tenants")
def create_tenant(
    name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    tenant = Tenant(
        name=name,
        owner_user_id=current_user.id,
        plan="FREE"
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    member = TenantMember(
        tenant_id=tenant.id,
        user_id=current_user.id,
        role="owner"
    )

    db.add(member)
    db.commit()

    return tenant


@app.get("/api/tenants")
def my_tenants(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    tenants = get_user_tenants(db, current_user.id)

    if not tenants:
        default_tenant = create_default_tenant_for_user(db, current_user)
        tenants = [default_tenant]

    return tenants


@app.get("/api/tenants/{tenant_id}/members")
def tenant_members(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return {"error": "Non autenticato"}

    if not user_can_access_tenant(db, current_user.id, tenant_id):
        return {"error": "Non autorizzato"}

    return db.query(TenantMember).filter(
        TenantMember.tenant_id == tenant_id
    ).all()