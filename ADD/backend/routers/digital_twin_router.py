from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models import (
    Revenue,
    Customer,
    ComplianceItem,
    CyberPrediction,
    User,
)
from osint_models import OsintScan
from predictive_models import PredictiveInsight
from agents_models import AgentRun
from digital_twin_models import DigitalTwinSnapshot
from digital_twin_engine import build_digital_twin
from tenant_security import user_can_access_company, tenant_company_error
from billing_engine import user_has_permission

router = APIRouter(prefix="/api/digital-twin", tags=["Digital Twin"])


@router.post("/analyze/{company_id}")
def analyze_digital_twin(
    company_id: int,
    x_tenant_id: int = Header(default=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return {"error": "Non autenticato"}

    if not user_has_permission(db, current_user.id, "predictive"):
        return {"error": "Digital Twin disponibile dal piano BUSINESS"}

    if not user_can_access_company(db, current_user.id, x_tenant_id, company_id):
        return tenant_company_error()

    revenues = db.query(Revenue).filter(Revenue.company_id == company_id).all()
    customers = db.query(Customer).filter(Customer.company_id == company_id).all()
    compliance_items = db.query(ComplianceItem).filter(ComplianceItem.company_id == company_id).all()
    cyber_predictions = db.query(CyberPrediction).filter(
        CyberPrediction.company_id == company_id
    ).order_by(CyberPrediction.created_at.desc()).all()
    osint_scans = db.query(OsintScan).filter(
        OsintScan.company_id == company_id
    ).order_by(OsintScan.created_at.desc()).all()
    predictive_insights = db.query(PredictiveInsight).filter(
        PredictiveInsight.company_id == company_id
    ).order_by(PredictiveInsight.created_at.desc()).all()
    agent_runs = db.query(AgentRun).filter(
        AgentRun.company_id == company_id
    ).order_by(AgentRun.created_at.desc()).limit(10).all()

    result = build_digital_twin(
        revenues,
        customers,
        compliance_items,
        cyber_predictions,
        osint_scans,
        predictive_insights,
        agent_runs,
    )

    snapshot = DigitalTwinSnapshot(company_id=company_id, **result)
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return snapshot


@router.get("/history/{company_id}")
def digital_twin_history(
    company_id: int,
    x_tenant_id: int = Header(default=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return {"error": "Non autenticato"}

    if not user_can_access_company(db, current_user.id, x_tenant_id, company_id):
        return tenant_company_error()

    return db.query(DigitalTwinSnapshot).filter(
        DigitalTwinSnapshot.company_id == company_id
    ).order_by(DigitalTwinSnapshot.created_at.desc()).limit(100).all()
