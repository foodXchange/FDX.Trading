"""Simple Activity Log model - basic user activity tracking"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from foodxchange.database import Base

class ActivityLog(Base):
    """Simple activity logging"""
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User who performed the action
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    
    # Action details
    action = Column(String(50), nullable=False)  # login, create_project, submit_quote, etc.
    details = Column(Text)  # Additional context
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="activity_logs")
    
    def __repr__(self):
        return f"<ActivityLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"