"""
Communication Log model for tracking all interactions
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from foodxchange.models.base import Base


class CommunicationType(enum.Enum):
    """Types of communication"""
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    MEETING = "meeting"
    VIDEO_CALL = "video_call"
    CHAT = "chat"
    SYSTEM = "system"  # Automated communications
    OTHER = "other"


class CommunicationDirection(enum.Enum):
    """Direction of communication"""
    INBOUND = "inbound"  # From external to us
    OUTBOUND = "outbound"  # From us to external
    INTERNAL = "internal"  # Within the system


class CommunicationLog(Base):
    """
    Track all communications with contacts and companies
    """
    __tablename__ = "communication_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Type and direction
    type = Column(SQLEnum(CommunicationType), nullable=False)
    direction = Column(SQLEnum(CommunicationDirection), nullable=False)
    
    # Parties involved
    from_user_id = Column(Integer, ForeignKey("users.id"))
    to_user_id = Column(Integer, ForeignKey("users.id"))
    
    contact_id = Column(Integer, ForeignKey("contacts.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # Related entities
    entity_type = Column(String(50))  # order, rfq, quote, etc.
    entity_id = Column(Integer)
    
    # Communication details
    subject = Column(String(500))
    content = Column(Text)
    summary = Column(Text)  # Brief summary for quick viewing
    
    # Email specific
    email_message_id = Column(String(255))  # Email Message-ID header
    email_thread_id = Column(String(255))  # For threading
    
    # Phone/Meeting specific
    duration_seconds = Column(Integer)  # Call/meeting duration
    recording_url = Column(String(500))  # If recorded
    
    # Participants (for meetings/calls)
    participants = Column(JSON)  # List of participant names/emails
    
    # Attachments
    attachments = Column(JSON)  # List of attachment references
    
    # Outcome
    outcome = Column(String(200))  # Result of communication
    follow_up_required = Column(String(200))
    follow_up_date = Column(DateTime)
    
    # Sentiment analysis (if AI processed)
    sentiment = Column(String(50))  # positive, neutral, negative
    key_points = Column(JSON)  # AI extracted key points
    
    # Additional data
    additional_data = Column(JSON)  # Additional communication-specific data
    
    # Timestamps
    communication_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
    contact = relationship("Contact", back_populates="communication_logs")
    
    def __repr__(self):
        return f"<CommunicationLog {self.type.value} {self.direction.value} on {self.communication_date}>"
    
    @property
    def is_recent(self):
        """Check if communication is within last 7 days"""
        return (datetime.utcnow() - self.communication_date).days <= 7
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "type": self.type.value,
            "direction": self.direction.value,
            "subject": self.subject,
            "summary": self.summary,
            "contact_name": self.contact.full_name if self.contact else None,
            "company_name": self.contact.company.name if self.contact and self.contact.company else None,
            "communication_date": self.communication_date.isoformat() if self.communication_date else None,
            "outcome": self.outcome,
            "follow_up_required": self.follow_up_required,
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None
        }