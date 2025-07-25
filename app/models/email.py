from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, func
from sqlalchemy.orm import declarative_base
import datetime

Base = declarative_base()

class Email(Base):
    """Email model for storing and classifying emails."""
    __tablename__ = "emails"

    id: int = Column(Integer, primary_key=True, index=True)
    message_id: str = Column(String(255), unique=True)
    from_email: str = Column(String(255))
    subject: str = Column(Text)
    body: str = Column(Text)
    classification: str = Column(String(50))
    processed: bool = Column(Boolean, default=False)
    tasks_created = Column(JSON)
    created_at: datetime.datetime = Column(DateTime, default=func.now()) 