from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, JSON, func, ARRAY, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class Supplier(Base):
    """Supplier model for FoodXchange platform."""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    
    # Company information
    company_name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(500))
    
    # Location
    address = Column(Text)
    city = Column(String(100))
    country = Column(String(100))
    
    # Business details
    categories = Column(JSON)  # Store as JSON for SQLite compatibility
    status = Column(String(50), default="pending")
    
    # Ratings and metrics
    rating = Column(Float)
    response_rate = Column(Float)
    average_response_time = Column(Float)
    is_verified = Column(Boolean, default=False)
    
    # Additional fields for FoodXchange
    name = Column(String(255))  # Alias for company_name
    specialties = Column(JSON)  # List of product specialties
    certifications = Column(JSON)  # List of certifications
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime)  # Last time website was scraped
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Company association
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # Relationships
    products_catalog = relationship("Product", back_populates="supplier")
    company = relationship("Company", back_populates="supplier_profile") 