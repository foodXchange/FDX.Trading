"""
Activity log model for tracking user and system actions
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from foodxchange.models.base import Base


class ActivityLog(Base):
    """
    Log of all activities in the system
    """
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null for system actions
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    details = Column(JSON)  # Additional data as JSON
    
    # Entity reference (polymorphic)
    entity_type = Column(String(50))  # supplier, product, rfq, etc.
    entity_id = Column(Integer)
    
    # Result
    status = Column(String(50), default="success")  # success, failed, partial
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    company = relationship("Company", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog {self.action} by user {self.user_id}>"