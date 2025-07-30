"""Buyer model for tracking buyer customers who request product sourcing"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Buyer(Base):
    """Buyer model to track buyer customers"""
    __tablename__ = "buyers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Business information
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)  # Small, Medium, Large
    annual_revenue = Column(String(100), nullable=True)
    
    # Preferences and requirements
    preferred_categories = Column(JSON, nullable=True)  # List of preferred product categories
    certification_requirements = Column(JSON, nullable=True)  # List of required certifications
    payment_terms = Column(String(100), nullable=True)
    minimum_order_quantity = Column(String(100), nullable=True)
    
    # Status and verification
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    verification_date = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="buyer")
    
    def __repr__(self):
        return f"<Buyer(id={self.id}, name='{self.name}', company='{self.company_name}')>" 