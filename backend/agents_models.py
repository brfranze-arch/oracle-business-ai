from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from database import Base


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)

    agent_name = Column(String, index=True)
    status = Column(String, default="completed")

    summary = Column(Text)
    actions = Column(Text)
    priority = Column(String, default="medium")

    created_at = Column(DateTime, default=datetime.utcnow)