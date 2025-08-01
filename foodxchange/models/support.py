"""
Support System Database Models
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from foodxchange.models.base import Base


class TicketStatus(enum.Enum):
    """Support ticket status enumeration"""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(enum.Enum):
    """Support ticket priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(enum.Enum):
    """Support ticket category enumeration"""
    AUTHENTICATION = "authentication"
    RFQ_PROCESSING = "rfq_processing"
    SUPPLIER_MANAGEMENT = "supplier_management"
    EMAIL_INTELLIGENCE = "email_intelligence"
    PAYMENT_TRANSACTION = "payment_transaction"
    UI_UX_ISSUE = "ui_ux_issue"
    SYSTEM_ERROR = "system_error"
    FEATURE_REQUEST = "feature_request"
    GENERAL_INQUIRY = "general_inquiry"


class ErrorSeverity(enum.Enum):
    """Error severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SupportTicket(Base):
    """Support ticket model"""
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(TicketCategory), nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(Enum(TicketStatus), default=TicketStatus.NEW)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    error_id = Column(String(100), nullable=True)  # Link to error logs
    browser_info = Column(JSON, nullable=True)
    device_info = Column(JSON, nullable=True)
    steps_to_reproduce = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    actual_behavior = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)  # List of file paths
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="support_tickets")
    assignee = relationship("User", foreign_keys=[assigned_to])
    status_history = relationship("TicketStatusHistory", back_populates="ticket")
    responses = relationship("TicketResponse", back_populates="ticket")


class TicketStatusHistory(Base):
    """Ticket status change history"""
    __tablename__ = "ticket_status_history"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    status = Column(Enum(TicketStatus), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="status_history")
    user = relationship("User", foreign_keys=[changed_by])


class TicketResponse(Base):
    """Support ticket responses"""
    __tablename__ = "ticket_responses"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes vs user-visible
    attachments = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="responses")
    user = relationship("User", foreign_keys=[user_id])


class ErrorLog(Base):
    """Enhanced error logging with support integration"""
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    error_id = Column(String(100), unique=True, index=True, nullable=False)
    request_id = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    severity = Column(Enum(ErrorSeverity), default=ErrorSeverity.MEDIUM)
    category = Column(Enum(TicketCategory), nullable=True)
    url_path = Column(String(500), nullable=True)
    http_method = Column(String(10), nullable=True)
    status_code = Column(Integer, nullable=True)
    browser_info = Column(JSON, nullable=True)
    device_info = Column(JSON, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    context_data = Column(JSON, nullable=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=True)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    ticket = relationship("SupportTicket", foreign_keys=[ticket_id])


class SupportAnalytics(Base):
    """Support system analytics"""
    __tablename__ = "support_analytics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    total_tickets = Column(Integer, default=0)
    new_tickets = Column(Integer, default=0)
    resolved_tickets = Column(Integer, default=0)
    avg_resolution_time = Column(Float, nullable=True)  # in hours
    tickets_by_category = Column(JSON, nullable=True)
    tickets_by_priority = Column(JSON, nullable=True)
    tickets_by_status = Column(JSON, nullable=True)
    error_count = Column(Integer, default=0)
    critical_errors = Column(Integer, default=0)
    user_satisfaction_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserFeedback(Base):
    """User feedback and bug reports"""
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    feedback_type = Column(String(50), nullable=False)  # bug_report, feature_request, general
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(TicketCategory), nullable=True)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    browser_info = Column(JSON, nullable=True)
    device_info = Column(JSON, nullable=True)
    screenshots = Column(JSON, nullable=True)
    contact_email = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")  # pending, reviewed, implemented, rejected
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by]) 