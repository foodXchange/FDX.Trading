"""
Order Status History model for tracking order lifecycle
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from foodxchange.models.base import Base


class OrderStatusHistory(Base):
    """
    Track all status changes for orders
    """
    __tablename__ = "order_status_history"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Order association
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    
    # Status change
    from_status = Column(String(50))  # Previous status
    to_status = Column(String(50), nullable=False)  # New status
    
    # Who made the change
    changed_by_user_id = Column(Integer, ForeignKey("users.id"))
    changed_by_name = Column(String(200))  # Store name in case user is deleted
    changed_by_role = Column(String(50))  # buyer, supplier, system
    
    # Change details
    reason = Column(String(200))  # Reason for status change
    notes = Column(Text)  # Additional notes
    
    # Additional data
    additional_data = Column(JSON)  # Additional data like tracking info, etc.
    
    # System tracking
    ip_address = Column(String(45))  # IP address of user making change
    user_agent = Column(String(255))  # Browser/system info
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    order = relationship("Order", back_populates="status_history")
    changed_by_user = relationship("User")
    
    def __repr__(self):
        return f"<OrderStatusHistory Order:{self.order_id} {self.from_status}->{self.to_status}>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "changed_by": self.changed_by_name,
            "reason": self.reason,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }