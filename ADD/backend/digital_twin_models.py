from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime
from database import Base


class DigitalTwinSnapshot(Base):
    __tablename__ = "digital_twin_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    twin_score = Column(Float, default=50)
    level = Column(String, default="STABILE")

    finance_index = Column(Float, default=50)
    customer_index = Column(Float, default=50)
    compliance_index = Column(Float, default=50)
    cyber_index = Column(Float, default=50)
    osint_index = Column(Float, default=50)
    predictive_index = Column(Float, default=50)
    agents_index = Column(Float, default=50)

    current_state = Column(Text)
    forecast_state = Column(Text)
    scenario_summary = Column(Text)
    recommendation = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
