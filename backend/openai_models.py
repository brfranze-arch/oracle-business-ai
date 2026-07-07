from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime

from database import Base


class OpenAIUsageLog(Base):
    __tablename__ = "openai_usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    company_id = Column(Integer, index=True)

    model = Column(String)
    question = Column(Text)
    answer = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
