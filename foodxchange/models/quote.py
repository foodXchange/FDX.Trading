from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import relationship
import datetime

from app.models.base import Base

class Quote(Base):
    """Quote model for supplier responses to RFQs."""
    __tablename__ = "quotes"

    id: int = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(Integer, ForeignKey("rfqs.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    price_per_unit = Column(Numeric(10,2))
    total_price = Column(Numeric(10,2))
    currency = Column(String(10), default="USD")
    delivery_time = Column(String(50))
    payment_terms = Column(String(100))
    notes = Column(Text)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=func.now())
    unit_price = Column(Numeric(10,2))  # Alias for price_per_unit

    rfq = relationship("RFQ", back_populates="quotes")
    supplier = relationship("Supplier")
    orders = relationship("Order", back_populates="quote") 