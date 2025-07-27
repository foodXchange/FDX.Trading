"""
Invoice model for billing and payments
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

from app.models.base import Base


class InvoiceStatus(enum.Enum):
    """Invoice statuses"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIAL = "partial"  # Partially paid
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Invoice(Base):
    """
    Invoices for orders
    """
    __tablename__ = "invoices"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Invoice identification
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Related entities
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    buyer_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    supplier_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Invoice details
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False, index=True)
    
    # Dates
    invoice_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    due_date = Column(DateTime, nullable=False)
    
    # Amounts (in cents)
    subtotal = Column(Integer, nullable=False)
    tax_amount = Column(Integer, default=0)
    tax_rate = Column(Integer)  # Tax percentage * 100 (e.g., 1000 = 10%)
    shipping_amount = Column(Integer, default=0)
    discount_amount = Column(Integer, default=0)
    total_amount = Column(Integer, nullable=False)
    amount_paid = Column(Integer, default=0)
    amount_due = Column(Integer, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Payment information
    payment_terms = Column(String(200))
    payment_instructions = Column(Text)  # Bank details, etc.
    
    # Billing addresses
    bill_to_address = Column(Text)
    ship_to_address = Column(Text)
    
    # Tax information
    buyer_tax_id = Column(String(50))
    supplier_tax_id = Column(String(50))
    
    # Notes
    notes = Column(Text)  # Visible on invoice
    internal_notes = Column(Text)  # Internal only
    
    # Tracking
    sent_date = Column(DateTime)
    viewed_date = Column(DateTime)
    paid_date = Column(DateTime)
    
    # Email tracking
    sent_to_emails = Column(JSON)  # List of email addresses
    reminder_count = Column(Integer, default=0)
    last_reminder_date = Column(DateTime)
    
    # Documents
    pdf_url = Column(String(500))  # Generated PDF
    attachments = Column(JSON)  # Additional documents
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="invoices")
    buyer_company = relationship("Company", foreign_keys=[buyer_company_id])
    supplier_company = relationship("Company", foreign_keys=[supplier_company_id])
    payments = relationship("Payment", back_populates="invoice")
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.status.value}>"
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status in [InvoiceStatus.PAID, InvoiceStatus.CANCELLED, InvoiceStatus.REFUNDED]:
            return False
        return datetime.utcnow() > self.due_date
    
    @property
    def days_overdue(self):
        """Get number of days overdue"""
        if not self.is_overdue:
            return 0
        return (datetime.utcnow() - self.due_date).days
    
    @property
    def payment_percentage(self):
        """Get percentage of invoice paid"""
        if self.total_amount == 0:
            return 100
        return int((self.amount_paid / self.total_amount) * 100)
    
    def calculate_due_date(self, payment_terms: str = None):
        """Calculate due date based on payment terms"""
        terms = payment_terms or self.payment_terms or "Net 30"
        
        # Parse common payment terms
        if "Net" in terms:
            days = int(''.join(filter(str.isdigit, terms)) or 30)
            self.due_date = self.invoice_date + timedelta(days=days)
        else:
            # Default to 30 days
            self.due_date = self.invoice_date + timedelta(days=30)
    
    def update_payment_status(self):
        """Update invoice status based on payments"""
        if self.amount_paid >= self.total_amount:
            self.status = InvoiceStatus.PAID
            self.paid_date = datetime.utcnow()
            self.amount_due = 0
        elif self.amount_paid > 0:
            self.status = InvoiceStatus.PARTIAL
            self.amount_due = self.total_amount - self.amount_paid
        elif self.is_overdue:
            self.status = InvoiceStatus.OVERDUE
            self.amount_due = self.total_amount
    
    def send_reminder(self):
        """Mark that a reminder was sent"""
        self.reminder_count += 1
        self.last_reminder_date = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "order_number": self.order.order_number if self.order else None,
            "status": self.status.value,
            "buyer_company": self.buyer_company.name if self.buyer_company else None,
            "supplier_company": self.supplier_company.name if self.supplier_company else None,
            "total_amount": f"{self.currency} {self.total_amount / 100:.2f}",
            "amount_due": f"{self.currency} {self.amount_due / 100:.2f}",
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_overdue": self.is_overdue,
            "days_overdue": self.days_overdue
        }