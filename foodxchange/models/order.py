"""
Order model for confirmed purchases
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from foodxchange.models.base import Base


class OrderStatus(enum.Enum):
    """Order lifecycle statuses"""
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(enum.Enum):
    """Payment statuses"""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    REFUNDED = "refunded"


class Order(Base):
    """
    Confirmed purchase orders
    """
    __tablename__ = "orders"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Order identification
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    po_number = Column(String(50))  # Buyer's PO number
    
    # Parties involved
    buyer_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    supplier_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    buyer_contact_id = Column(Integer, ForeignKey("contacts.id"))
    supplier_contact_id = Column(Integer, ForeignKey("contacts.id"))
    
    # Source references
    rfq_id = Column(Integer, ForeignKey("rfqs.id"))
    quote_id = Column(Integer, ForeignKey("quotes.id"))
    
    # Order details
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Amounts (stored in cents)
    subtotal = Column(Integer, nullable=False)  # Sum of line items
    tax_amount = Column(Integer, default=0)
    shipping_amount = Column(Integer, default=0)
    discount_amount = Column(Integer, default=0)
    total_amount = Column(Integer, nullable=False)  # Final total
    currency = Column(String(3), default="USD", nullable=False)
    
    # Payment terms
    payment_terms = Column(String(200))  # e.g., "Net 30"
    payment_method = Column(String(50))  # e.g., "Wire Transfer"
    payment_due_date = Column(DateTime)
    
    # Delivery information
    delivery_date = Column(DateTime)
    requested_delivery_date = Column(DateTime)
    delivery_address = Column(Text)
    delivery_instructions = Column(Text)
    shipping_method = Column(String(100))
    tracking_number = Column(String(100))
    
    # Additional information
    notes = Column(Text)
    internal_notes = Column(Text)  # Not visible to supplier
    special_requirements = Column(Text)
    
    # Documents
    documents = Column(JSON)  # List of attached documents
    
    # Timestamps
    order_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_date = Column(DateTime)
    shipped_date = Column(DateTime)
    delivered_date = Column(DateTime)
    completed_date = Column(DateTime)
    cancelled_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    buyer_company = relationship("Company", foreign_keys=[buyer_company_id], back_populates="orders")
    supplier_company = relationship("Company", foreign_keys=[supplier_company_id])
    buyer_contact = relationship("Contact", foreign_keys=[buyer_contact_id])
    supplier_contact = relationship("Contact", foreign_keys=[supplier_contact_id])
    
    rfq = relationship("RFQ", back_populates="orders")
    quote = relationship("Quote", back_populates="orders")
    
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    status_history = relationship("OrderStatusHistory", back_populates="order", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="order")
    
    def __repr__(self):
        return f"<Order {self.order_number} - {self.status.value}>"
    
    @property
    def is_active(self):
        """Check if order is still active"""
        return self.status not in [OrderStatus.COMPLETED, OrderStatus.CANCELLED, OrderStatus.REFUNDED]
    
    @property
    def total_items(self):
        """Get total number of items"""
        return sum(item.quantity for item in self.order_items)
    
    @property
    def display_total(self):
        """Get formatted total amount"""
        return f"{self.currency} {self.total_amount / 100:.2f}"
    
    def update_status(self, new_status: OrderStatus, notes: str = None):
        """Update order status and create history record"""
        old_status = self.status
        self.status = new_status
        
        # Update relevant dates
        if new_status == OrderStatus.CONFIRMED:
            self.confirmed_date = datetime.utcnow()
        elif new_status == OrderStatus.SHIPPED:
            self.shipped_date = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED:
            self.delivered_date = datetime.utcnow()
        elif new_status == OrderStatus.COMPLETED:
            self.completed_date = datetime.utcnow()
        elif new_status == OrderStatus.CANCELLED:
            self.cancelled_date = datetime.utcnow()
    
    def calculate_totals(self):
        """Recalculate order totals from line items"""
        self.subtotal = sum(item.total_amount for item in self.order_items)
        self.total_amount = (
            self.subtotal + 
            self.tax_amount + 
            self.shipping_amount - 
            self.discount_amount
        )
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "order_number": self.order_number,
            "status": self.status.value,
            "payment_status": self.payment_status.value,
            "buyer_company": self.buyer_company.name if self.buyer_company else None,
            "supplier_company": self.supplier_company.name if self.supplier_company else None,
            "total_amount": self.display_total,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "items_count": len(self.order_items)
        }