"""
Error Handling Models and Data Classes
Defines the data structures used by the error handling service
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import traceback


class ErrorType(Enum):
    """Error type categories"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    EXTERNAL_API = "external_api"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryAction(Enum):
    """Recovery action types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    NOTIFY = "notify"
    ESCALATE = "escalate"
    IGNORE = "ignore"
    MANUAL = "manual"


@dataclass
class ErrorContext:
    """Context information for error"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    environment: str = "production"
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorDetails:
    """Detailed error information"""
    error_id: str
    type: ErrorType
    severity: ErrorSeverity
    message: str
    technical_message: str
    stack_trace: Optional[str] = None
    error_code: Optional[str] = None
    http_status: Optional[int] = None
    source_file: Optional[str] = None
    source_line: Optional[int] = None
    context: Optional[ErrorContext] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "error_id": self.error_id,
            "type": self.type.value,
            "severity": self.severity.value,
            "message": self.message,
            "technical_message": self.technical_message,
            "stack_trace": self.stack_trace,
            "error_code": self.error_code,
            "http_status": self.http_status,
            "source_file": self.source_file,
            "source_line": self.source_line,
            "context": self.context.__dict__ if self.context else None,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    def to_user_friendly(self) -> Dict[str, Any]:
        """Get user-friendly error representation"""
        return {
            "error_id": self.error_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "support_code": self.error_id[:8]  # Short code for support
        }


@dataclass
class RecoveryOption:
    """Recovery option for an error"""
    action: RecoveryAction
    description: str
    success_probability: float
    estimated_time: Optional[int] = None  # seconds
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action": self.action.value,
            "description": self.description,
            "success_probability": self.success_probability,
            "estimated_time": self.estimated_time,
            "parameters": self.parameters
        }


@dataclass
class ErrorNotification:
    """Error notification configuration"""
    error_id: str
    severity: ErrorSeverity
    recipients: List[str]
    channels: List[str]  # email, slack, pagerduty, etc.
    message: str
    error_details: ErrorDetails
    sent_at: Optional[datetime] = None
    
    def should_notify(self) -> bool:
        """Check if notification should be sent"""
        # Always notify for critical errors
        if self.severity == ErrorSeverity.CRITICAL:
            return True
        
        # Check other conditions
        # Could implement rate limiting, business hours, etc.
        return self.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]


@dataclass
class ErrorPattern:
    """Pattern for error detection and handling"""
    pattern_id: str
    name: str
    description: str
    error_types: List[ErrorType]
    keywords: List[str]
    regex_patterns: List[str]
    severity_override: Optional[ErrorSeverity] = None
    recovery_actions: List[RecoveryAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorMetrics:
    """Error metrics for monitoring"""
    error_type: ErrorType
    count: int = 0
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    severity_breakdown: Dict[str, int] = field(default_factory=dict)
    recovery_success_rate: float = 0.0
    average_resolution_time: float = 0.0  # seconds
    
    def update(self, error: ErrorDetails, recovered: bool = False, resolution_time: Optional[float] = None):
        """Update metrics with new error"""
        self.count += 1
        
        if not self.first_seen:
            self.first_seen = error.timestamp
        self.last_seen = error.timestamp
        
        # Update severity breakdown
        severity_key = error.severity.value
        self.severity_breakdown[severity_key] = self.severity_breakdown.get(severity_key, 0) + 1
        
        # Update recovery metrics
        if recovered:
            # Simple moving average
            self.recovery_success_rate = (
                (self.recovery_success_rate * (self.count - 1) + 1) / self.count
            )
        
        if resolution_time:
            # Simple moving average
            self.average_resolution_time = (
                (self.average_resolution_time * (self.count - 1) + resolution_time) / self.count
            )