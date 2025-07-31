"""
Intelligent Error Handling Service for FoodXchange Platform
Provides advanced error categorization, actionable recovery mechanisms, and notifications center integration
"""

import logging
import json
import re
import traceback
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import asyncio
from sqlalchemy.orm import Session

from foodxchange.database import get_db
from foodxchange.models.user import User
from foodxchange.services.notification_service import (
    IntelligentNotificationService, NotificationType, NotificationCategory, 
    NotificationPriority, NotificationStatus, NotificationAction
)

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error type classification"""
    FILE_FORMAT = "file_format"
    FILE_SIZE = "file_size"
    NETWORK_CONNECTIVITY = "network_connectivity"
    SERVICE_UNAVAILABLE = "service_unavailable"
    QUOTA_LIMIT = "quota_limit"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    PROCESSING = "processing"
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
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    UPLOAD_DIFFERENT_FILE = "upload_different_file"
    REDUCE_FILE_SIZE = "reduce_file_size"
    CHANGE_FILE_FORMAT = "change_file_format"
    CHECK_CONNECTION = "check_connection"
    CONTACT_SUPPORT = "contact_support"
    USE_ALTERNATIVE_METHOD = "use_alternative_method"
    SAVE_AS_DRAFT = "save_as_draft"
    MANUAL_ENTRY = "manual_entry"


@dataclass
class ErrorContext:
    """Error context information"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: Optional[datetime] = None
    workflow_step: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    system_state: Optional[Dict[str, Any]] = None


@dataclass
class ErrorDetails:
    """Detailed error information"""
    error_type: ErrorType
    severity: ErrorSeverity
    error_code: str
    technical_message: str
    user_friendly_message: str
    context: ErrorContext
    stack_trace: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class RecoveryOption:
    """Recovery option configuration"""
    action: RecoveryAction
    label: str
    description: str
    icon: str
    color: str
    requires_user_confirmation: bool = False
    automatic: bool = False
    max_attempts: Optional[int] = None
    backoff_delay: Optional[int] = None
    url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class ErrorNotification:
    """Error notification structure"""
    id: str
    user_id: str
    error_details: ErrorDetails
    recovery_options: List[RecoveryOption]
    created_at: datetime = field(default_factory=datetime.now)
    notification_id: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_method: Optional[str] = None
    user_feedback: Optional[str] = None


class IntelligentErrorHandler:
    """
    Intelligent error handling service with categorization, recovery, and notifications
    """
    
    def __init__(self):
        self.notification_service = IntelligentNotificationService()
        self.error_patterns = self._initialize_error_patterns()
        self.recovery_strategies = self._initialize_recovery_strategies()
        self.error_history = {}
        self.active_recoveries = {}
        
    def _initialize_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize error pattern recognition"""
        return {
            "file_format": {
                "patterns": [
                    r"unsupported.*format",
                    r"invalid.*file.*type",
                    r"format.*not.*supported",
                    r"file.*type.*error"
                ],
                "error_type": ErrorType.FILE_FORMAT,
                "severity": ErrorSeverity.MEDIUM
            },
            "file_size": {
                "patterns": [
                    r"file.*too.*large",
                    r"size.*exceeds.*limit",
                    r"maximum.*file.*size",
                    r"file.*size.*error"
                ],
                "error_type": ErrorType.FILE_SIZE,
                "severity": ErrorSeverity.MEDIUM
            },
            "network_connectivity": {
                "patterns": [
                    r"connection.*failed",
                    r"network.*error",
                    r"timeout",
                    r"connection.*refused",
                    r"no.*internet"
                ],
                "error_type": ErrorType.NETWORK_CONNECTIVITY,
                "severity": ErrorSeverity.HIGH
            },
            "service_unavailable": {
                "patterns": [
                    r"service.*unavailable",
                    r"azure.*service.*error",
                    r"api.*unavailable",
                    r"service.*down",
                    r"maintenance"
                ],
                "error_type": ErrorType.SERVICE_UNAVAILABLE,
                "severity": ErrorSeverity.HIGH
            },
            "quota_limit": {
                "patterns": [
                    r"quota.*exceeded",
                    r"rate.*limit",
                    r"daily.*limit",
                    r"usage.*limit",
                    r"plan.*limit"
                ],
                "error_type": ErrorType.QUOTA_LIMIT,
                "severity": ErrorSeverity.MEDIUM
            },
            "authentication": {
                "patterns": [
                    r"unauthorized",
                    r"authentication.*failed",
                    r"invalid.*token",
                    r"login.*required"
                ],
                "error_type": ErrorType.AUTHENTICATION,
                "severity": ErrorSeverity.HIGH
            },
            "authorization": {
                "patterns": [
                    r"forbidden",
                    r"permission.*denied",
                    r"access.*denied",
                    r"insufficient.*permissions"
                ],
                "error_type": ErrorType.AUTHORIZATION,
                "severity": ErrorSeverity.HIGH
            }
        }
    
    def _initialize_recovery_strategies(self) -> Dict[ErrorType, List[RecoveryOption]]:
        """Initialize recovery strategies for each error type"""
        return {
            ErrorType.FILE_FORMAT: [
                RecoveryOption(
                    action=RecoveryAction.CHANGE_FILE_FORMAT,
                    label="Upload Different Format",
                    description="Try uploading JPG, PNG, or WEBP format",
                    icon="fas fa-file-image",
                    color="primary",
                    requires_user_confirmation=True
                ),
                RecoveryOption(
                    action=RecoveryAction.USE_ALTERNATIVE_METHOD,
                    label="Use Manual Entry",
                    description="Enter product details manually",
                    icon="fas fa-edit",
                    color="secondary",
                    requires_user_confirmation=True
                )
            ],
            ErrorType.FILE_SIZE: [
                RecoveryOption(
                    action=RecoveryAction.REDUCE_FILE_SIZE,
                    label="Reduce File Size",
                    description="Compress image to under 10MB",
                    icon="fas fa-compress",
                    color="warning",
                    requires_user_confirmation=True
                ),
                RecoveryOption(
                    action=RecoveryAction.UPLOAD_DIFFERENT_FILE,
                    label="Upload Smaller Image",
                    description="Try a different image with smaller size",
                    icon="fas fa-upload",
                    color="primary",
                    requires_user_confirmation=True
                )
            ],
            ErrorType.NETWORK_CONNECTIVITY: [
                RecoveryOption(
                    action=RecoveryAction.RETRY_WITH_BACKOFF,
                    label="Retry Connection",
                    description="Automatically retry with increasing delays",
                    icon="fas fa-sync",
                    color="info",
                    automatic=True,
                    max_attempts=3,
                    backoff_delay=2000
                ),
                RecoveryOption(
                    action=RecoveryAction.CHECK_CONNECTION,
                    label="Check Connection",
                    description="Verify your internet connection",
                    icon="fas fa-wifi",
                    color="warning",
                    requires_user_confirmation=True
                )
            ],
            ErrorType.SERVICE_UNAVAILABLE: [
                RecoveryOption(
                    action=RecoveryAction.RETRY_WITH_BACKOFF,
                    label="Retry Service",
                    description="Service may be temporarily unavailable",
                    icon="fas fa-clock",
                    color="info",
                    automatic=True,
                    max_attempts=5,
                    backoff_delay=5000
                ),
                RecoveryOption(
                    action=RecoveryAction.SAVE_AS_DRAFT,
                    label="Save as Draft",
                    description="Save your work and try again later",
                    icon="fas fa-save",
                    color="secondary",
                    requires_user_confirmation=True
                )
            ],
            ErrorType.QUOTA_LIMIT: [
                RecoveryOption(
                    action=RecoveryAction.CONTACT_SUPPORT,
                    label="Upgrade Plan",
                    description="Contact support to increase your limits",
                    icon="fas fa-crown",
                    color="warning",
                    requires_user_confirmation=True
                ),
                RecoveryOption(
                    action=RecoveryAction.USE_ALTERNATIVE_METHOD,
                    label="Try Tomorrow",
                    description="Daily limits reset at midnight",
                    icon="fas fa-calendar",
                    color="info",
                    requires_user_confirmation=True
                )
            ]
        }

    async def handle_error(
        self,
        error: Exception,
        user_id: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        workflow_step: Optional[str] = None
    ) -> ErrorNotification:
        """
        Handle error with intelligent categorization and recovery options
        """
        try:
            # Create error context
            if context is None:
                context = ErrorContext(
                    user_id=user_id,
                    timestamp=datetime.now(),
                    workflow_step=workflow_step
                )
            
            # Analyze error
            error_details = self._analyze_error(error, context)
            
            # Get recovery options
            recovery_options = self._get_recovery_options(error_details)
            
            # Create error notification
            error_notification = ErrorNotification(
                id=str(uuid.uuid4()),
                user_id=user_id or "system",
                error_details=error_details,
                recovery_options=recovery_options,
                created_at=datetime.now()
            )
            
            # Store in history
            self.error_history[error_notification.id] = error_notification
            
            # Create notification
            if user_id:
                notification_id = await self._create_error_notification(error_notification)
                error_notification.notification_id = notification_id
            
            # Attempt automatic recovery if applicable
            await self._attempt_automatic_recovery(error_notification)
            
            return error_notification
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            # Fallback to basic error handling
            return await self._create_fallback_error_notification(error, user_id)

    def _analyze_error(self, error: Exception, context: ErrorContext) -> ErrorDetails:
        """Analyze error and categorize it"""
        error_message = str(error).lower()
        error_type = ErrorType.UNKNOWN
        severity = ErrorSeverity.MEDIUM
        
        # Pattern matching
        for pattern_name, pattern_info in self.error_patterns.items():
            for pattern in pattern_info["patterns"]:
                if re.search(pattern, error_message, re.IGNORECASE):
                    error_type = pattern_info["error_type"]
                    severity = pattern_info["severity"]
                    break
            if error_type != ErrorType.UNKNOWN:
                break
        
        # Generate error code
        error_code = self._generate_error_code(error_type, error)
        
        # Create user-friendly message
        user_message = self._create_user_friendly_message(error_type, error, context)
        
        return ErrorDetails(
            error_type=error_type,
            severity=severity,
            error_code=error_code,
            technical_message=str(error),
            user_friendly_message=user_message,
            context=context,
            stack_trace=traceback.format_exc(),
            metadata=self._extract_error_metadata(error, context)
        )

    def _generate_error_code(self, error_type: ErrorType, error: Exception) -> str:
        """Generate unique error code"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        error_hash = hash(str(error)) % 10000
        return f"{error_type.value.upper()}-{timestamp}-{error_hash:04d}"

    def _create_user_friendly_message(self, error_type: ErrorType, error: Exception, context: ErrorContext) -> str:
        """Create user-friendly error message"""
        base_messages = {
            ErrorType.FILE_FORMAT: "The image format isn't supported. Please use JPG, PNG, or WEBP files.",
            ErrorType.FILE_SIZE: "The image file is too large. Please reduce it to under 10MB.",
            ErrorType.NETWORK_CONNECTIVITY: "We're having trouble connecting to our services. Please check your internet connection.",
            ErrorType.SERVICE_UNAVAILABLE: "Our AI analysis service is temporarily unavailable. We're working to restore it.",
            ErrorType.QUOTA_LIMIT: "You've reached your daily analysis limit. Please try again tomorrow or upgrade your plan.",
            ErrorType.AUTHENTICATION: "Please log in again to continue.",
            ErrorType.AUTHORIZATION: "You don't have permission to perform this action.",
            ErrorType.VALIDATION: "Please check your input and try again.",
            ErrorType.PROCESSING: "We encountered an issue while processing your request.",
            ErrorType.SYSTEM: "A system error occurred. Our team has been notified.",
            ErrorType.UNKNOWN: "An unexpected error occurred. Please try again."
        }
        
        return base_messages.get(error_type, base_messages[ErrorType.UNKNOWN])

    def _get_recovery_options(self, error_details: ErrorDetails) -> List[RecoveryOption]:
        """Get recovery options for the error type"""
        return self.recovery_strategies.get(error_details.error_type, [
            RecoveryOption(
                action=RecoveryAction.RETRY,
                label="Try Again",
                description="Attempt the operation again",
                icon="fas fa-redo",
                color="primary",
                requires_user_confirmation=True
            ),
            RecoveryOption(
                action=RecoveryAction.CONTACT_SUPPORT,
                label="Contact Support",
                description="Get help from our support team",
                icon="fas fa-headset",
                color="warning",
                requires_user_confirmation=True
            )
        ])

    def _extract_error_metadata(self, error: Exception, context: ErrorContext) -> Dict[str, Any]:
        """Extract metadata from error and context"""
        metadata = {
            "error_class": error.__class__.__name__,
            "error_module": error.__class__.__module__,
            "timestamp": context.timestamp.isoformat() if context.timestamp else datetime.now().isoformat(),
            "workflow_step": context.workflow_step,
            "related_entity_type": context.related_entity_type,
            "related_entity_id": context.related_entity_id
        }
        
        # Add specific metadata based on error type
        if hasattr(error, 'response'):
            metadata["response_status"] = getattr(error.response, 'status_code', None)
            metadata["response_headers"] = dict(getattr(error.response, 'headers', {}))
        
        return metadata

    async def _create_error_notification(self, error_notification: ErrorNotification) -> str:
        """Create notification in the notification center"""
        try:
            # Create notification actions
            actions = []
            for option in error_notification.recovery_options:
                actions.append(NotificationAction(
                    label=option.label,
                    action=f"error_recovery_{option.action.value}",
                    url=option.url,
                    data={
                        "error_id": error_notification.id,
                        "recovery_action": option.action.value,
                        "requires_confirmation": option.requires_user_confirmation
                    },
                    icon=option.icon,
                    color=option.color
                ))
            
            # Create notification
            notification = await self.notification_service.create_notification(
                user_id=error_notification.user_id,
                template_key="error_notification",
                context={
                    "error_code": error_notification.error_details.error_code,
                    "user_message": error_notification.error_details.user_friendly_message,
                    "error_type": error_notification.error_details.error_type.value,
                    "severity": error_notification.error_details.severity.value,
                    "recovery_options": [asdict(option) for option in error_notification.recovery_options],
                    "timestamp": error_notification.created_at.isoformat()
                },
                priority=self._get_notification_priority(error_notification.error_details.severity),
                metadata={
                    "error_id": error_notification.id,
                    "error_type": error_notification.error_details.error_type.value,
                    "recovery_available": len(error_notification.recovery_options) > 0
                }
            )
            
            return notification.id
            
        except Exception as e:
            logger.error(f"Failed to create error notification: {e}")
            return None

    def _get_notification_priority(self, severity: ErrorSeverity) -> NotificationPriority:
        """Map error severity to notification priority"""
        priority_map = {
            ErrorSeverity.LOW: NotificationPriority.LOW,
            ErrorSeverity.MEDIUM: NotificationPriority.NORMAL,
            ErrorSeverity.HIGH: NotificationPriority.HIGH,
            ErrorSeverity.CRITICAL: NotificationPriority.URGENT
        }
        return priority_map.get(severity, NotificationPriority.NORMAL)

    async def _attempt_automatic_recovery(self, error_notification: ErrorNotification):
        """Attempt automatic recovery for applicable errors"""
        automatic_options = [
            option for option in error_notification.recovery_options 
            if option.automatic
        ]
        
        for option in automatic_options:
            await self._execute_recovery_action(error_notification, option)

    async def _execute_recovery_action(self, error_notification: ErrorNotification, option: RecoveryOption):
        """Execute a recovery action"""
        try:
            if option.action == RecoveryAction.RETRY_WITH_BACKOFF:
                await self._retry_with_backoff(error_notification, option)
            elif option.action == RecoveryAction.RETRY:
                await self._simple_retry(error_notification, option)
            # Add more recovery action implementations as needed
            
        except Exception as e:
            logger.error(f"Recovery action failed: {e}")

    async def _retry_with_backoff(self, error_notification: ErrorNotification, option: RecoveryOption):
        """Retry with exponential backoff"""
        recovery_id = f"{error_notification.id}_{option.action.value}"
        self.active_recoveries[recovery_id] = {
            "error_notification": error_notification,
            "option": option,
            "attempts": 0,
            "max_attempts": option.max_attempts or 3,
            "backoff_delay": option.backoff_delay or 2000
        }
        
        # Start retry process
        asyncio.create_task(self._retry_loop(recovery_id))

    async def _retry_loop(self, recovery_id: str):
        """Retry loop with backoff"""
        recovery = self.active_recoveries.get(recovery_id)
        if not recovery:
            return
        
        while recovery["attempts"] < recovery["max_attempts"]:
            recovery["attempts"] += 1
            
            try:
                # Wait before retry
                if recovery["attempts"] > 1:
                    delay = recovery["backoff_delay"] * (2 ** (recovery["attempts"] - 2))
                    await asyncio.sleep(delay / 1000)
                
                # Attempt recovery (this would call the original operation)
                success = await self._attempt_operation_recovery(recovery["error_notification"])
                
                if success:
                    await self._mark_error_resolved(recovery["error_notification"], "automatic_retry")
                    break
                    
            except Exception as e:
                logger.error(f"Retry attempt {recovery['attempts']} failed: {e}")
        
        # Clean up
        if recovery_id in self.active_recoveries:
            del self.active_recoveries[recovery_id]

    async def _attempt_operation_recovery(self, error_notification: ErrorNotification) -> bool:
        """Attempt to recover the original operation"""
        # This would implement the actual recovery logic
        # For now, return False to indicate failure
        return False

    async def _mark_error_resolved(self, error_notification: ErrorNotification, resolution_method: str):
        """Mark error as resolved"""
        error_notification.resolved_at = datetime.now()
        error_notification.resolution_method = resolution_method
        
        # Update notification
        if error_notification.notification_id:
            try:
                # Mark notification as read and update status
                await self.notification_service.mark_as_read(
                    error_notification.user_id, 
                    error_notification.notification_id
                )
            except Exception as e:
                logger.error(f"Failed to update notification: {e}")

    async def _create_fallback_error_notification(self, error: Exception, user_id: Optional[str]) -> ErrorNotification:
        """Create fallback error notification when error handling fails"""
        context = ErrorContext(
            user_id=user_id,
            timestamp=datetime.now()
        )
        
        error_details = ErrorDetails(
            error_type=ErrorType.UNKNOWN,
            severity=ErrorSeverity.HIGH,
            error_code="FALLBACK-ERROR",
            technical_message=str(error),
            user_friendly_message="An unexpected error occurred. Please try again or contact support.",
            context=context
        )
        
        return ErrorNotification(
            id=str(uuid.uuid4()),
            user_id=user_id or "system",
            error_details=error_details,
            recovery_options=[
                RecoveryOption(
                    action=RecoveryAction.CONTACT_SUPPORT,
                    label="Contact Support",
                    description="Get help from our support team",
                    icon="fas fa-headset",
                    color="warning",
                    requires_user_confirmation=True
                )
            ],
            created_at=datetime.now()
        )

    async def get_error_analytics(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get error analytics and patterns"""
        try:
            user_errors = [
                error for error in self.error_history.values()
                if user_id is None or error.user_id == user_id
            ]
            
            # Error type distribution
            error_type_counts = {}
            for error in user_errors:
                error_type = error.error_details.error_type.value
                error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1
            
            # Resolution success rate
            resolved_errors = [e for e in user_errors if e.resolved_at]
            resolution_rate = len(resolved_errors) / len(user_errors) if user_errors else 0
            
            # Common error patterns
            common_patterns = []
            for error in user_errors[-50:]:  # Last 50 errors
                pattern = {
                    "error_type": error.error_details.error_type.value,
                    "workflow_step": error.error_details.context.workflow_step,
                    "timestamp": error.created_at.isoformat()
                }
                common_patterns.append(pattern)
            
            return {
                "total_errors": len(user_errors),
                "resolved_errors": len(resolved_errors),
                "resolution_rate": resolution_rate,
                "error_type_distribution": error_type_counts,
                "recent_patterns": common_patterns[-10:],
                "active_recoveries": len(self.active_recoveries)
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return {}

    async def clear_error_history(self, user_id: Optional[str] = None, days: int = 30):
        """Clear old error history"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            if user_id:
                # Clear specific user's old errors
                keys_to_remove = [
                    key for key, error in self.error_history.items()
                    if error.user_id == user_id and error.created_at < cutoff_date
                ]
            else:
                # Clear all old errors
                keys_to_remove = [
                    key for key, error in self.error_history.items()
                    if error.created_at < cutoff_date
                ]
            
            for key in keys_to_remove:
                del self.error_history[key]
            
            logger.info(f"Cleared {len(keys_to_remove)} old error records")
            
        except Exception as e:
            logger.error(f"Error clearing history: {e}")


# Global error handler instance
error_handler = IntelligentErrorHandler() 