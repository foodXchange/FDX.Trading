"""Simplified User model - consolidates buyers and suppliers"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, func
from sqlalchemy.orm import relationship
from foodxchange.database import Base

class User(Base):
    """Unified user model for all user types"""
    __tablename__ = "users"
    
    # Core fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    company = Column(String(255), index=True)
    user_type = Column(String(20), default="buyer")  # buyer, supplier, both, admin
    
    # Contact information
    phone = Column(String(50))
    country = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    website = Column(String(255))
    
    # Business information
    industry = Column(String(100))
    company_size = Column(String(50))
    
    # Supplier-specific fields (null for buyers)
    certifications = Column(Text)
    payment_terms = Column(String(100))
    minimum_order = Column(String(100))
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    # Status fields
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    verification_date = Column(DateTime)
    
    # Simple preferences (no JSONB)
    preferences = Column(Text)  # Simple text notes
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    projects = relationship("Project", back_populates="user")
    quotes = relationship("Quote", back_populates="supplier")
    products = relationship("Product", back_populates="supplier")
    activity_logs = relationship("ActivityLog", back_populates="user")
    
    def is_buyer(self):
        return self.user_type in ["buyer", "both"]
    
    def is_supplier(self):
        return self.user_type in ["supplier", "both"]
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', type='{self.user_type}')>"