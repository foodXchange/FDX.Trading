from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from .base import Base
import datetime

class User(Base):
    """User model for FoodXchange platform."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    company = Column(String(255))
    role = Column(String(50), default="buyer")
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 