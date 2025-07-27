from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema

class EmailClassification(str, Enum):
    NEW_RFQ = "new_rfq"
    QUOTE_RECEIVED = "quote_received"
    PRICE_UPDATE = "price_update"
    ORDER_CONFIRMATION = "order_confirmation"
    COMPLAINT = "complaint"
    COMPLIANCE_ALERT = "compliance_alert"
    FOLLOW_UP = "follow_up"
    FYI = "fyi"
    SPAM = "spam"
    UNKNOWN = "unknown"

class EmailStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    BOUNCED = "bounced"

class EmailTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class EmailCreate(BaseModel):
    """Schema for creating a new email"""
    subject: str = Field(..., min_length=1, max_length=255, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body content")
    html_body: Optional[str] = Field(None, description="HTML email body")
    from_email: EmailStr = Field(..., description="Sender email address")
    from_name: Optional[str] = Field(None, max_length=255, description="Sender name")
    to_emails: List[EmailStr] = Field(..., min_items=1, description="Recipient email addresses")
    cc_emails: Optional[List[EmailStr]] = Field(default=[], description="CC email addresses")
    bcc_emails: Optional[List[EmailStr]] = Field(default=[], description="BCC email addresses")
    reply_to: Optional[EmailStr] = Field(None, description="Reply-to email address")
    classification: EmailClassification = Field(default=EmailClassification.UNKNOWN, description="Email classification")
    status: EmailStatus = Field(default=EmailStatus.DRAFT, description="Email status")
    priority: int = Field(default=3, ge=1, le=5, description="Email priority (1=highest, 5=lowest)")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")
    attachments: Optional[List[str]] = Field(default=[], description="Attachment file names")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    template_id: Optional[str] = Field(None, description="Email template ID")
    template_data: Optional[Dict[str, Any]] = Field(default={}, description="Template data")
    
    @validator('scheduled_at')
    def validate_scheduled_at(cls, v):
        """Validate scheduled time is in the future"""
        if v and v <= datetime.utcnow():
            raise ValueError('Scheduled time must be in the future')
        return v

class EmailUpdate(BaseModel):
    """Schema for updating an email"""
    subject: Optional[str] = Field(None, min_length=1, max_length=255, description="Email subject")
    body: Optional[str] = Field(None, min_length=1, description="Email body content")
    html_body: Optional[str] = Field(None, description="HTML email body")
    from_name: Optional[str] = Field(None, max_length=255, description="Sender name")
    to_emails: Optional[List[EmailStr]] = Field(None, min_items=1, description="Recipient email addresses")
    cc_emails: Optional[List[EmailStr]] = Field(None, description="CC email addresses")
    bcc_emails: Optional[List[EmailStr]] = Field(None, description="BCC email addresses")
    reply_to: Optional[EmailStr] = Field(None, description="Reply-to email address")
    classification: Optional[EmailClassification] = Field(None, description="Email classification")
    status: Optional[EmailStatus] = Field(None, description="Email status")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Email priority")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled send time")
    attachments: Optional[List[str]] = Field(None, description="Attachment file names")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    template_data: Optional[Dict[str, Any]] = Field(None, description="Template data")
    sent_at: Optional[datetime] = Field(None, description="Sent timestamp")
    delivered_at: Optional[datetime] = Field(None, description="Delivered timestamp")
    read_at: Optional[datetime] = Field(None, description="Read timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class EmailResponse(BaseSchema):
    """Schema for email response"""
    id: int
    subject: str
    body: str
    html_body: Optional[str]
    from_email: str
    from_name: Optional[str]
    to_emails: List[str]
    cc_emails: Optional[List[str]]
    bcc_emails: Optional[List[str]]
    reply_to: Optional[str]
    classification: EmailClassification
    status: EmailStatus
    priority: int
    scheduled_at: Optional[datetime]
    attachments: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    template_id: Optional[str]
    template_data: Optional[Dict[str, Any]]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

class EmailList(BaseSchema):
    """Schema for email list response"""
    id: int
    subject: str
    from_email: str
    from_name: Optional[str]
    to_emails: List[str]
    classification: EmailClassification
    status: EmailStatus
    priority: int
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    created_at: datetime

class EmailTaskCreate(BaseModel):
    """Schema for creating an email task"""
    email_id: int = Field(..., description="Email ID")
    task_type: str = Field(..., description="Task type (send, track, analyze)")
    status: EmailTaskStatus = Field(default=EmailTaskStatus.PENDING, description="Task status")
    priority: int = Field(default=3, ge=1, le=5, description="Task priority")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled execution time")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Task parameters")
    retry_count: int = Field(default=0, ge=0, description="Retry count")
    max_retries: int = Field(default=3, ge=0, description="Maximum retries")

class EmailTaskUpdate(BaseModel):
    """Schema for updating an email task"""
    status: Optional[EmailTaskStatus] = Field(None, description="Task status")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Task priority")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled execution time")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Task parameters")
    retry_count: Optional[int] = Field(None, ge=0, description="Retry count")
    max_retries: Optional[int] = Field(None, ge=0, description="Maximum retries")
    started_at: Optional[datetime] = Field(None, description="Started timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completed timestamp")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result")
    error_message: Optional[str] = Field(None, description="Error message")

class EmailTaskResponse(BaseSchema):
    """Schema for email task response"""
    id: int
    email_id: int
    task_type: str
    status: EmailTaskStatus
    priority: int
    scheduled_at: Optional[datetime]
    parameters: Optional[Dict[str, Any]]
    retry_count: int
    max_retries: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime

class EmailSearch(BaseModel):
    """Schema for email search parameters"""
    query: Optional[str] = Field(None, description="Search query")
    from_email: Optional[str] = Field(None, description="Filter by sender")
    to_email: Optional[str] = Field(None, description="Filter by recipient")
    classification: Optional[EmailClassification] = Field(None, description="Filter by classification")
    status: Optional[EmailStatus] = Field(None, description="Filter by status")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Filter by priority")
    sent_after: Optional[datetime] = Field(None, description="Sent after date")
    sent_before: Optional[datetime] = Field(None, description="Sent before date")
    scheduled_after: Optional[datetime] = Field(None, description="Scheduled after date")
    scheduled_before: Optional[datetime] = Field(None, description="Scheduled before date")

class EmailTemplate(BaseModel):
    """Schema for email template"""
    id: str
    name: str
    subject: str
    body: str
    html_body: Optional[str]
    variables: List[str]
    category: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

class EmailAnalytics(BaseModel):
    """Schema for email analytics"""
    total_sent: int
    total_delivered: int
    total_read: int
    total_failed: int
    delivery_rate: float
    read_rate: float
    failure_rate: float
    average_response_time: Optional[float]
    classification_breakdown: Dict[str, int]
    status_breakdown: Dict[str, int]
    daily_stats: List[Dict[str, Any]] 