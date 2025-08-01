from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship
from .base import Base
import datetime

class User(Base):
    """User model for FoodXchange platform."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    company = Column(String(255))  # Company name as string - matches database column
    role = Column(String(50), default="buyer")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Profile fields
    phone = Column(String(50))
    country = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    bio = Column(Text)
    profile_picture = Column(String(255))
    job_title = Column(String(100))
    department = Column(String(100))
    industry = Column(String(100))
    company_size = Column(String(50))
    website = Column(String(255))
    linkedin = Column(String(255))
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Relationships
    notifications = relationship("Notification", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    support_tickets = relationship("SupportTicket", foreign_keys="SupportTicket.user_id", back_populates="user") 