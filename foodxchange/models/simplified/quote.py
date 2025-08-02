"""Simplified Quote model - supplier responses to RFQs"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, DECIMAL, String, func
from sqlalchemy.orm import relationship
from foodxchange.database import Base

class Quote(Base):
    """Quote/proposal from suppliers"""
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Related entities
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Quote details
    price = Column(DECIMAL(10, 2), nullable=False)
    delivery_days = Column(Integer)
    notes = Column(Text)
    
    # Status
    status = Column(String(20), default="pending", index=True)  # pending, accepted, rejected
    
    # Timestamp
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="quotes")
    supplier = relationship("User", back_populates="quotes")
    
    def accept(self):
        """Accept this quote"""
        self.status = "accepted"
        # Reject other quotes for the same project
        for quote in self.project.quotes:
            if quote.id != self.id and quote.status == "pending":
                quote.status = "rejected"
    
    def reject(self):
        """Reject this quote"""
        self.status = "rejected"
    
    def __repr__(self):
        return f"<Quote(id={self.id}, project_id={self.project_id}, price={self.price}, status='{self.status}')>"