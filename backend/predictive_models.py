from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from database import Base


class PredictiveInsight(Base):
    __tablename__ = "predictive_insights"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    finance_risk = Column(Float, default=50)
    customer_risk = Column(Float, default=50)
    compliance_risk = Column(Float, default=50)
    cyber_risk = Column(Float, default=50)

    prediction_score = Column(Float, default=50)
    level = Column(String, default="STABILE")

    summary = Column(Text)
    recommendation = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)