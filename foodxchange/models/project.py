"""Project model for saving AI product analysis searches and results"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Project(Base):
    """Project model to organize AI product analysis searches"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Buyer relationship - who requested this sourcing
    buyer_id = Column(Integer, ForeignKey("buyers.id"), nullable=True, index=True)
    
    # Search details
    search_type = Column(String(50), nullable=True)  # image, url, text
    product_description = Column(Text, nullable=True)
    product_category = Column(String(100), nullable=True)
    
    # Analysis results
    analyzed_images = Column(JSON, nullable=True)  # List of image URLs/data
    analysis_results = Column(JSON, nullable=True)  # Full AI analysis results
    
    # Project status
    status = Column(String(50), default="active")  # active, completed, archived
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    buyer = relationship("Buyer", back_populates="projects")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', buyer_id={self.buyer_id})>" 