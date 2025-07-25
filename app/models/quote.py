from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text, func
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Quote(Base):
    """Quote model for supplier responses to RFQs."""
    __tablename__ = "quotes"

    id: int = Column(Integer, primary_key=True, index=True)
    rfq_id: int = Column(Integer, ForeignKey("rfqs.id"))
    supplier_id: int = Column(Integer, ForeignKey("suppliers.id"))
    price_per_unit = Column(Numeric(10,2))
    total_price = Column(Numeric(10,2))
    currency: str = Column(String(10), default="USD")
    delivery_time: str = Column(String(50))
    payment_terms: str = Column(String(100))
    notes: str = Column(Text)
    status: str = Column(String(50), default="pending")
    created_at: datetime.datetime = Column(DateTime, default=func.now())

    rfq = relationship("RFQ", back_populates="quotes")
    supplier = relationship("Supplier") 