"""Simplified Project model - basic RFQ tracking"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, DECIMAL, Date, func
from sqlalchemy.orm import relationship
from foodxchange.database import Base

class Project(Base):
    """Simplified project/RFQ model"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # User who created the project
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Simple status field
    status = Column(String(20), default="open", index=True)  # open, reviewing, closed
    
    # Budget information
    budget_min = Column(DECIMAL(10, 2))
    budget_max = Column(DECIMAL(10, 2))
    currency = Column(String(3), default="USD")
    
    # Timeline
    deadline = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="projects")
    quotes = relationship("Quote", back_populates="project")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.project_id:
            self.project_id = self.generate_project_id()
    
    def generate_project_id(self):
        """Generate simple project ID"""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        return f"RFQ-{timestamp}"
    
    def is_open(self):
        return self.status == "open"
    
    def close(self):
        self.status = "closed"
    
    def __repr__(self):
        return f"<Project(id={self.id}, title='{self.title}', status='{self.status}')>"