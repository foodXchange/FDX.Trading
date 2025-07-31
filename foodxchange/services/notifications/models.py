"""
Notification Models and Data Classes
Defines the data structures used by the notification service
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, asdict, field
from enum import Enum


class NotificationType(Enum):
    """Notification types"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    URGENT = "urgent"


class NotificationCategory(Enum):
    """Notification categories"""
    AI_ANALYSIS = "ai_analysis"
    PROJECTS = "projects"
    SUPPLIERS = "suppliers"
    BUYERS = "buyers"
    SYSTEM = "system"
    SECURITY = "security"
    COLLABORATION = "collaboration"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """Notification delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class NotificationAction:
    """Action button for notifications"""
    label: str
    url: str
    action_type: str = "link"  # link, ajax, dismiss
    style: str = "primary"  # primary, secondary, danger
    data: Optional[Dict[str, Any]] = None


@dataclass
class Notification:
    """Notification data model"""
    id: str
    user_id: str
    title: str
    message: str
    type: NotificationType
    category: NotificationCategory
    priority: NotificationPriority
    status: NotificationStatus
    created_at: datetime
    updated_at: datetime
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    actions: List[NotificationAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert notification to dictionary"""
        data = asdict(self)
        # Convert enums to values
        data['type'] = self.type.value
        data['category'] = self.category.value
        data['priority'] = self.priority.value
        data['status'] = self.status.value
        # Convert datetimes to ISO format
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        if self.read_at:
            data['read_at'] = self.read_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        return data
    
    def is_expired(self) -> bool:
        """Check if notification has expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False
    
    def is_read(self) -> bool:
        """Check if notification has been read"""
        return self.status == NotificationStatus.READ or self.read_at is not None


@dataclass
class NotificationTemplate:
    """Template for generating notifications"""
    id: str
    name: str
    category: NotificationCategory
    type: NotificationType
    priority: NotificationPriority
    title_template: str
    message_template: str
    action_templates: List[Dict[str, str]] = field(default_factory=list)
    default_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NotificationPreferences:
    """User notification preferences"""
    user_id: str
    enabled: bool = True
    email_enabled: bool = True
    push_enabled: bool = True
    categories: Dict[str, bool] = field(default_factory=dict)
    quiet_hours_start: Optional[int] = None  # Hour in 24-hour format
    quiet_hours_end: Optional[int] = None
    frequency_limit: int = 50  # Max notifications per day
    
    def is_category_enabled(self, category: NotificationCategory) -> bool:
        """Check if a category is enabled"""
        if not self.enabled:
            return False
        return self.categories.get(category.value, True)
    
    def is_quiet_hours(self) -> bool:
        """Check if currently in quiet hours"""
        if self.quiet_hours_start is None or self.quiet_hours_end is None:
            return False
        
        current_hour = datetime.now().hour
        
        if self.quiet_hours_start <= self.quiet_hours_end:
            # Normal case (e.g., 22:00 to 07:00)
            return self.quiet_hours_start <= current_hour < self.quiet_hours_end
        else:
            # Crosses midnight (e.g., 22:00 to 07:00)
            return current_hour >= self.quiet_hours_start or current_hour < self.quiet_hours_end