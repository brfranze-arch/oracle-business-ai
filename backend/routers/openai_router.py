from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from deps import get_db, get_current_user
from models import (
    Company,
    Revenue,
    Customer,
    ComplianceItem,
    CyberAsset,
    CyberFinding,
    CyberThreat,
    User,
)
from billing_engine import user_has_permission
from tenant_security import user_can_access_company, tenant_company_error
from openai_engine import openai_engine
from openai_models import OpenAIUsageLog
from config import settings

router = APIRouter(prefix="/api/openai", tags=["OpenAI Enterprise"])


@router.post("/company-advisor/{company_id}")
def openai_company_advisor(
    company_id: int,
    question: str,
    x_tenant_id: int = Header(default=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return {"error": "Non autenticato"}

    if not user_has_permission(db, current_user.id, "openai"):
        return {"error": "Modulo OpenAI disponibile dal piano BUSINESS"}

    if not user_can_access_company(db, current_user.id, x_tenant_id, company_id):
        return tenant_company_error()

    company = db.query(Company).filter(Company.id == company_id).first()

    if not company:
        return {"error": "Azienda non trovata"}

    revenues = db.query(Revenue).filter(Revenue.company_id == company_id).all()
    customers = db.query(Customer).filter(Customer.company_id == company_id).all()
    compliance_items = db.query(ComplianceItem).filter(
        ComplianceItem.company_id == company_id
    ).all()
    cyber_assets = db.query(CyberAsset).filter(CyberAsset.company_id == company_id).all()
    cyber_findings = db.query(CyberFinding).filter(
        CyberFinding.company_id == company_id
    ).all()
    cyber_threats = db.query(CyberThreat).filter(
        CyberThreat.company_id == company_id
    ).all()

    total_revenue = sum(r.amount for r in revenues)

    system_prompt = """
Sei Oracle Business AI Enterprise.
Rispondi in italiano.
Devi comportarti come un consulente aziendale senior.
Usa solo i dati forniti.
Se mancano dati, dichiaralo chiaramente.
Fornisci sempre:
1. Sintesi
2. Rischi principali
3. Azioni consigliate
4. Priorità operative
"""

    user_prompt = f"""
Azienda:
- Nome: {company.name}
- Settore: {company.sector}
- Paese: {company.country}
- Dominio: {company.domain}

Finance:
- Entrate totali: {total_revenue}
- Numero operazioni: {len(revenues)}

Customer:
- Numero clienti: {len(customers)}

Compliance:
- Elementi compliance: {len(compliance_items)}

Cyber:
- Asset: {len(cyber_assets)}
- Finding: {len(cyber_findings)}
- Threat: {len(cyber_threats)}

Domanda utente:
{question}
"""

    ai_result = openai_engine.generate_business_answer(system_prompt, user_prompt)

    if ai_result.get("error"):
        return ai_result

    log = OpenAIUsageLog(
        user_id=current_user.id,
        company_id=company_id,
        model=settings.OPENAI_MODEL,
        question=question,
        answer=ai_result["answer"],
    )

    db.add(log)
    db.commit()

    return ai_result


@router.get("/usage/{company_id}")
def openai_usage_history(
    company_id: int,
    x_tenant_id: int = Header(default=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return {"error": "Non autenticato"}

    if not user_can_access_company(db, current_user.id, x_tenant_id, company_id):
        return tenant_company_error()

    return db.query(OpenAIUsageLog).filter(
        OpenAIUsageLog.company_id == company_id
    ).order_by(OpenAIUsageLog.created_at.desc()).limit(100).all()
