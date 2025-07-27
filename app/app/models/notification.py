"""
Notification model for system alerts and messages
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.models.base import Base


class NotificationType(enum.Enum):
    """Types of notifications"""
    # RFQ related
    NEW_RFQ = "new_rfq"
    RFQ_RESPONSE = "rfq_response"
    RFQ_EXPIRED = "rfq_expired"
    
    # Quote related
    NEW_QUOTE = "new_quote"
    QUOTE_ACCEPTED = "quote_accepted"
    QUOTE_REJECTED = "quote_rejected"
    QUOTE_EXPIRED = "quote_expired"
    
    # Order related
    ORDER_PLACED = "order_placed"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_SHIPPED = "order_shipped"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    
    # Payment related
    PAYMENT_RECEIVED = "payment_received"
    PAYMENT_OVERDUE = "payment_overdue"
    INVOICE_GENERATED = "invoice_generated"
    
    # System
    SYSTEM_ALERT = "system_alert"
    PRICE_ALERT = "price_alert"
    INVENTORY_ALERT = "inventory_alert"
    
    # Communication
    NEW_MESSAGE = "new_message"
    DOCUMENT_SHARED = "document_shared"
    
    # Account
    ACCOUNT_VERIFIED = "account_verified"
    PASSWORD_RESET = "password_reset"
    PROFILE_UPDATE = "profile_update"


class NotificationPriority(enum.Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationChannel(enum.Enum):
    """Delivery channels for notifications"""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Notification(Base):
    """
    System notifications for users
    """
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    
    # Notification details
    type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    
    # Content
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Action link
    action_url = Column(String(500))  # Where to go when clicked
    action_text = Column(String(100))  # Button text
    
    # Related entities (polymorphic reference)
    entity_type = Column(String(50))  # order, rfq, quote, etc.
    entity_id = Column(Integer)
    
    # Additional data
    additional_data = Column(JSON)  # Extra data for rendering
    
    # Delivery channels
    channels = Column(JSON)  # List of channels to deliver to
    
    # Status tracking
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(DateTime)
    
    # Email tracking
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime)
    email_opened = Column(Boolean, default=False)
    email_opened_at = Column(DateTime)
    
    # SMS tracking
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime)
    
    # Push tracking
    push_sent = Column(Boolean, default=False)
    push_sent_at = Column(DateTime)
    
    # Expiration
    expires_at = Column(DateTime)  # Auto-delete after this date
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    company = relationship("Company", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.type.value} for User:{self.user_id}>"
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()
    
    def mark_email_sent(self):
        """Mark email as sent"""
        self.email_sent = True
        self.email_sent_at = datetime.utcnow()
    
    def mark_email_opened(self):
        """Mark email as opened"""
        self.email_opened = True
        self.email_opened_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "action_url": self.action_url,
            "action_text": self.action_text,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "additional_data": self.additional_data or {}
        }