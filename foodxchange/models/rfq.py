from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import relationship
import datetime

from foodxchange.models.base import Base

class RFQ(Base):
    """RFQ (Request for Quotation) model."""
    __tablename__ = "rfqs"

    id: int = Column(Integer, primary_key=True, index=True)
    rfq_number: str = Column(String(50), unique=True, nullable=False, index=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    product_name: str = Column(String(255), nullable=False)
    category: str = Column(String(100))
    quantity: str = Column(String(100))
    delivery_date: datetime.date = Column(Date)
    delivery_location: str = Column(String(255))
    budget_min = Column(Numeric(10,2))
    budget_max = Column(Numeric(10,2))
    requirements: str = Column(Text)
    status: str = Column(String(50), default="draft")
    created_at: datetime.datetime = Column(DateTime, default=func.now())
    updated_at: datetime.datetime = Column(DateTime, default=func.now(), onupdate=func.now())

    # Add company association
    company_id = Column(Integer, ForeignKey("companies.id"))
    assigned_contact_id = Column(Integer, ForeignKey("contacts.id"))
    
    # Relationships
    user = relationship("User")
    quotes = relationship("Quote", back_populates="rfq")
    company = relationship("Company", back_populates="rfqs")
    assigned_contact = relationship("Contact", back_populates="assigned_rfqs")
    orders = relationship("Order", back_populates="rfq") 