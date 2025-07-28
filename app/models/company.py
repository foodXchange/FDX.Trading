"""
Company model for organizations (buyers and suppliers)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class CompanyType(enum.Enum):
    """Types of companies in the system"""
    BUYER = "buyer"
    SUPPLIER = "supplier"
    BOTH = "both"  # Can act as both buyer and supplier


class CompanySize(enum.Enum):
    """Company size categories"""
    SMALL = "small"  # 1-50 employees
    MEDIUM = "medium"  # 51-250 employees
    LARGE = "large"  # 251-1000 employees
    ENTERPRISE = "enterprise"  # 1000+ employees


class Company(Base):
    """
    Company/Organization entity that can be a buyer, supplier, or both
    """
    __tablename__ = "companies"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    legal_name = Column(String(200))  # Official registered name
    registration_number = Column(String(100), unique=True, nullable=True)  # Tax/VAT number
    company_type = Column(SQLEnum(CompanyType), default=CompanyType.BUYER, nullable=False)
    
    # Contact information
    email = Column(String(120), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    website = Column(String(255))
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state_province = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), nullable=False)
    
    # Business details
    company_size = Column(SQLEnum(CompanySize))
    year_established = Column(Integer)
    annual_revenue = Column(String(50))  # Revenue range
    description = Column(Text)
    
    # Industry and categories
    industry = Column(String(100))
    categories = Column(JSON)  # List of product categories they deal with
    
    # Verification and status
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    verification_date = Column(DateTime)
    verification_documents = Column(JSON)  # List of document references
    
    # Ratings and metrics
    rating = Column(Integer, default=0)  # 0-5 stars
    total_reviews = Column(Integer, default=0)
    
    # Financial
    payment_terms = Column(String(100))  # Default payment terms
    credit_limit = Column(Integer)  # In cents
    currency = Column(String(3), default="USD")
    
    # Certifications
    certifications = Column(JSON)  # List of certifications with expiry dates
    
    # Preferences
    preferred_payment_methods = Column(JSON)  # List of accepted payment methods
    delivery_preferences = Column(JSON)
    communication_preferences = Column(JSON)
    
    # Integration
    external_id = Column(String(100))  # ID from external system
    integration_data = Column(JSON)  # Additional integration metadata
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    
    # For suppliers
    supplier_profile = relationship("Supplier", back_populates="company", uselist=False)
    products = relationship("Product", back_populates="company")
    
    # For buyers
    orders = relationship("Order", foreign_keys="Order.buyer_company_id", back_populates="buyer_company")
    rfqs = relationship("RFQ", back_populates="company")
    
    # Common
    activity_logs = relationship("ActivityLog", back_populates="company")
    notifications = relationship("Notification", back_populates="company")
    
    def __repr__(self):
        return f"<Company {self.name} ({self.company_type.value})>"
    
    @property
    def is_supplier(self):
        """Check if company can act as supplier"""
        return self.company_type in [CompanyType.SUPPLIER, CompanyType.BOTH]
    
    @property
    def is_buyer(self):
        """Check if company can act as buyer"""
        return self.company_type in [CompanyType.BUYER, CompanyType.BOTH]
    
    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [
            self.address_line1,
            self.address_line2,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ", ".join(filter(None, parts))
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.company_type.value,
            "email": self.email,
            "phone": self.phone,
            "website": self.website,
            "address": self.full_address,
            "country": self.country,
            "is_verified": self.is_verified,
            "rating": self.rating,
            "categories": self.categories or [],
            "certifications": self.certifications or [],
            "created_at": self.created_at.isoformat() if self.created_at else None
        }