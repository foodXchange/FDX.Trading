"""Supplier model for the FoodXchange platform"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from foodxchange.models.base import Base
from foodxchange.models.mixins import TimestampMixin, SoftDeleteMixin


class Supplier(Base, TimestampMixin, SoftDeleteMixin):
    """Model for suppliers"""
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    
    # Company Information
    company_name = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    
    # Location
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    
    # Business Details
    certifications = Column(Text, nullable=True)  # Comma-separated list
    payment_terms = Column(String(100), nullable=True)
    minimum_order = Column(String(100), nullable=True)
    
    # Additional Information
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    
    # Ratings and metrics
    rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    def to_dict(self):
        """Convert supplier to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'company_name': self.company_name,
            'industry': self.industry,
            'company_size': self.company_size,
            'country': self.country,
            'city': self.city,
            'address': self.address,
            'certifications': self.certifications,
            'payment_terms': self.payment_terms,
            'minimum_order': self.minimum_order,
            'description': self.description,
            'website': self.website,
            'rating': self.rating,
            'total_reviews': self.total_reviews,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }