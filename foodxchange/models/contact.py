"""
Contact model for people associated with companies
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from foodxchange.models.base import Base


class Contact(Base):
    """
    Individual contacts within a company
    """
    __tablename__ = "contacts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Company association
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    title = Column(String(100))  # Job title
    department = Column(String(100))
    
    # Contact information
    email = Column(String(120), nullable=False, index=True)
    phone = Column(String(20))
    mobile = Column(String(20))
    
    # Role and permissions
    role = Column(String(50))  # Primary contact, sales, procurement, etc.
    is_primary = Column(Boolean, default=False)  # Primary contact for company
    can_place_orders = Column(Boolean, default=False)
    can_approve_quotes = Column(Boolean, default=False)
    
    # Communication preferences
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50))
    communication_preferences = Column(JSON)  # Email, SMS, WhatsApp preferences
    
    # Additional info
    notes = Column(Text)
    tags = Column(JSON)  # Custom tags for filtering
    
    # Status
    is_active = Column(Boolean, default=True)
    last_contacted = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="contacts")
    communication_logs = relationship("CommunicationLog", back_populates="contact")
    assigned_rfqs = relationship("RFQ", back_populates="assigned_contact")
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_name(self):
        """Get display name with title"""
        if self.title:
            return f"{self.full_name}, {self.title}"
        return self.full_name
    
    def __repr__(self):
        return f"<Contact {self.full_name} at {self.company.name if self.company else 'Unknown'}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "company_id": self.company_id,
            "name": self.full_name,
            "title": self.title,
            "email": self.email,
            "phone": self.phone,
            "mobile": self.mobile,
            "role": self.role,
            "is_primary": self.is_primary,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }