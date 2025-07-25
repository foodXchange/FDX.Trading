"""
Payment model for tracking financial transactions
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class PaymentMethod(enum.Enum):
    """Payment methods"""
    WIRE_TRANSFER = "wire_transfer"
    ACH = "ach"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    CASH = "cash"
    CREDIT_MEMO = "credit_memo"
    OTHER = "other"


class PaymentStatus(enum.Enum):
    """Payment processing statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Payment(Base):
    """
    Payment transactions
    """
    __tablename__ = "payments"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Payment identification
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    reference_number = Column(String(100))  # External reference (check #, transaction ID)
    
    # Related entities
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    payer_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    payee_company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    # Payment details
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Amounts (in cents)
    amount = Column(Integer, nullable=False)  # Payment amount
    currency = Column(String(3), default="USD", nullable=False)
    
    # Processing fees (if applicable)
    processing_fee = Column(Integer, default=0)
    net_amount = Column(Integer)  # Amount after fees
    
    # Dates
    payment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_date = Column(DateTime)
    cleared_date = Column(DateTime)  # When funds actually cleared
    
    # Bank/Card information (encrypted/tokenized)
    account_last_four = Column(String(4))  # Last 4 digits of account/card
    routing_number_last_four = Column(String(4))  # For ACH/Wire
    
    # Payment processor information
    processor = Column(String(50))  # Stripe, PayPal, etc.
    processor_transaction_id = Column(String(255))
    processor_response = Column(JSON)  # Full response from processor
    
    # Notes
    notes = Column(Text)
    internal_notes = Column(Text)
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciled_date = Column(DateTime)
    reconciled_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Refund information (if this is a refund)
    is_refund = Column(Boolean, default=False)
    original_payment_id = Column(Integer, ForeignKey("payments.id"))
    refund_reason = Column(String(200))
    
    # Additional data
    additional_data = Column(JSON)  # Additional payment-specific data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoice = relationship("Invoice", back_populates="payments")
    payer_company = relationship("Company", foreign_keys=[payer_company_id])
    payee_company = relationship("Company", foreign_keys=[payee_company_id])
    reconciled_by = relationship("User", foreign_keys=[reconciled_by_user_id])
    original_payment = relationship("Payment", remote_side=[id])
    
    def __repr__(self):
        return f"<Payment {self.payment_number} - {self.amount/100} {self.currency}>"
    
    @property
    def display_amount(self):
        """Get formatted payment amount"""
        return f"{self.currency} {self.amount / 100:.2f}"
    
    @property
    def display_net_amount(self):
        """Get formatted net amount"""
        if self.net_amount:
            return f"{self.currency} {self.net_amount / 100:.2f}"
        return self.display_amount
    
    def calculate_net_amount(self):
        """Calculate net amount after fees"""
        self.net_amount = self.amount - self.processing_fee
    
    def mark_as_processed(self):
        """Mark payment as processed"""
        self.status = PaymentStatus.PROCESSING
        self.processed_date = datetime.utcnow()
    
    def mark_as_completed(self):
        """Mark payment as completed"""
        self.status = PaymentStatus.COMPLETED
        self.cleared_date = datetime.utcnow()
    
    def reconcile(self, user_id: int):
        """Mark payment as reconciled"""
        self.is_reconciled = True
        self.reconciled_date = datetime.utcnow()
        self.reconciled_by_user_id = user_id
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "payment_number": self.payment_number,
            "reference_number": self.reference_number,
            "invoice_number": self.invoice.invoice_number if self.invoice else None,
            "payment_method": self.payment_method.value,
            "status": self.status.value,
            "amount": self.display_amount,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "is_reconciled": self.is_reconciled,
            "is_refund": self.is_refund
        }