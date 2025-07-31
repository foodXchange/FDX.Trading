"""
Intelligent Error Handler
Main error handling service that coordinates all error functionality
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Type
from datetime import datetime

from .models import (
    ErrorDetails,
    ErrorContext,
    ErrorType,
    ErrorSeverity,
    RecoveryOption,
    ErrorNotification
)
from .error_analyzer import ErrorAnalyzer
from .recovery_manager import RecoveryManager
from .error_logger import ErrorLogger

logger = logging.getLogger(__name__)


class IntelligentErrorHandler:
    """
    Main error handling service coordinating all error functionality
    """
    
    def __init__(self):
        self.analyzer = ErrorAnalyzer()
        self.recovery_manager = RecoveryManager()
        self.error_logger = ErrorLogger()
        
        # Error handling configuration
        self.config = {
            "auto_recovery_enabled": True,
            "notification_enabled": True,
            "max_recovery_attempts": 3,
            "critical_error_threshold": 5,  # Critical errors in 5 minutes
            "error_rate_limit": 100  # Max errors per minute
        }
        
        # Track error rates
        self.error_rate_tracker: Dict[str, List[datetime]] = {}
    
    async def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        request_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle an error with intelligent recovery"""
        try:
            # Create error context
            error_context = self._create_error_context(user_id, request_context)
            
            # Analyze error
            error_details = self.analyzer.analyze_error(error, context)
            error_details.context = error_context
            
            # Check error rate limiting
            if self._is_rate_limited(error_details.type):
                logger.warning(f"Error rate limit exceeded for {error_details.type.value}")
                return {
                    "error_id": error_details.error_id,
                    "handled": False,
                    "reason": "Rate limit exceeded"
                }
            
            # Log error
            self.error_logger.log_error(error_details, context)
            
            # Get recovery options
            recovery_options = self.analyzer.get_recovery_options(error_details)
            
            # Attempt recovery if enabled
            recovery_result = None
            if self.config["auto_recovery_enabled"] and recovery_options:
                recovery_result = await self._attempt_recovery(
                    error_details,
                    recovery_options,
                    context
                )
            
            # Send notifications if needed
            if self._should_notify(error_details):
                await self._send_error_notification(error_details, recovery_result)
            
            # Check for critical error patterns
            self._check_critical_patterns(error_details)
            
            # Return handling result
            return {
                "error_id": error_details.error_id,
                "handled": True,
                "error_type": error_details.type.value,
                "severity": error_details.severity.value,
                "user_message": error_details.message,
                "recovery_attempted": recovery_result is not None,
                "recovery_success": recovery_result.get("success") if recovery_result else False,
                "recovery_result": recovery_result,
                "support_code": error_details.error_id[:8]
            }
            
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            return {
                "error_id": "HANDLER_ERROR",
                "handled": False,
                "reason": "Error handler failure",
                "original_error": str(error)
            }
    
    async def handle_error_with_fallback(
        self,
        primary_func,
        fallback_func,
        context: Optional[Dict[str, Any]] = None
    ):
        """Execute function with automatic fallback on error"""
        try:
            return await primary_func()
        except Exception as e:
            # Handle error
            error_result = await self.handle_error(
                e,
                context={
                    **(context or {}),
                    "fallback_function": fallback_func
                }
            )
            
            # If recovery succeeded, return result
            if error_result.get("recovery_success"):
                recovery_result = error_result.get("recovery_result", {})
                if "result" in recovery_result:
                    return recovery_result["result"]
            
            # Otherwise, execute fallback directly
            return await fallback_func()
    
    async def _attempt_recovery(
        self,
        error_details: ErrorDetails,
        recovery_options: List[RecoveryOption],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Attempt error recovery"""
        # Sort recovery options by success probability
        sorted_options = sorted(
            recovery_options,
            key=lambda x: x.success_probability,
            reverse=True
        )
        
        # Try each recovery option
        for option in sorted_options:
            logger.info(f"Attempting recovery: {option.action.value}")
            
            result = await self.recovery_manager.execute_recovery(
                error_details,
                option,
                context
            )
            
            if result.get("success"):
                # Log successful recovery
                self.error_logger.log_error(
                    error_details,
                    context,
                    recovered=True,
                    resolution_time=result.get("recovery_time")
                )
                return result
        
        return None
    
    def _create_error_context(
        self,
        user_id: Optional[str],
        request_context: Optional[Dict[str, Any]]
    ) -> ErrorContext:
        """Create error context from request"""
        context = ErrorContext(user_id=user_id)
        
        if request_context:
            context.session_id = request_context.get("session_id")
            context.request_id = request_context.get("request_id")
            context.endpoint = request_context.get("endpoint")
            context.method = request_context.get("method")
            context.ip_address = request_context.get("ip_address")
            context.user_agent = request_context.get("user_agent")
            context.additional_data = request_context.get("additional_data", {})
        
        return context
    
    def _is_rate_limited(self, error_type: ErrorType) -> bool:
        """Check if error type is rate limited"""
        now = datetime.now()
        key = error_type.value
        
        # Initialize tracker
        if key not in self.error_rate_tracker:
            self.error_rate_tracker[key] = []
        
        # Remove old entries
        cutoff = now.timestamp() - 60  # 1 minute window
        self.error_rate_tracker[key] = [
            ts for ts in self.error_rate_tracker[key]
            if ts.timestamp() > cutoff
        ]
        
        # Check rate limit
        if len(self.error_rate_tracker[key]) >= self.config["error_rate_limit"]:
            return True
        
        # Add current error
        self.error_rate_tracker[key].append(now)
        return False
    
    def _should_notify(self, error_details: ErrorDetails) -> bool:
        """Determine if error should trigger notification"""
        if not self.config["notification_enabled"]:
            return False
        
        # Always notify for critical errors
        if error_details.severity == ErrorSeverity.CRITICAL:
            return True
        
        # Notify for high severity errors
        if error_details.severity == ErrorSeverity.HIGH:
            return True
        
        # Check specific error types
        notify_types = [
            ErrorType.AUTHENTICATION,
            ErrorType.AUTHORIZATION,
            ErrorType.DATABASE
        ]
        
        return error_details.type in notify_types
    
    async def _send_error_notification(
        self,
        error_details: ErrorDetails,
        recovery_result: Optional[Dict[str, Any]]
    ):
        """Send error notification"""
        try:
            notification = ErrorNotification(
                error_id=error_details.error_id,
                severity=error_details.severity,
                recipients=self._get_notification_recipients(error_details),
                channels=self._get_notification_channels(error_details),
                message=self._create_notification_message(error_details, recovery_result),
                error_details=error_details
            )
            
            if notification.should_notify():
                # In production, integrate with notification service
                logger.warning(
                    f"ERROR NOTIFICATION: {notification.message}",
                    extra={"notification": notification.__dict__}
                )
                notification.sent_at = datetime.now()
            
        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")
    
    def _get_notification_recipients(self, error_details: ErrorDetails) -> List[str]:
        """Get notification recipients based on error"""
        recipients = []
        
        # Add user if available
        if error_details.context and error_details.context.user_id:
            recipients.append(f"user:{error_details.context.user_id}")
        
        # Add support team for critical errors
        if error_details.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]:
            recipients.append("team:support")
        
        # Add specific teams based on error type
        if error_details.type == ErrorType.DATABASE:
            recipients.append("team:database")
        elif error_details.type == ErrorType.EXTERNAL_API:
            recipients.append("team:integrations")
        
        return recipients
    
    def _get_notification_channels(self, error_details: ErrorDetails) -> List[str]:
        """Get notification channels based on severity"""
        channels = ["in_app"]
        
        if error_details.severity == ErrorSeverity.CRITICAL:
            channels.extend(["email", "slack", "pagerduty"])
        elif error_details.severity == ErrorSeverity.HIGH:
            channels.extend(["email", "slack"])
        
        return channels
    
    def _create_notification_message(
        self,
        error_details: ErrorDetails,
        recovery_result: Optional[Dict[str, Any]]
    ) -> str:
        """Create notification message"""
        message = f"Error {error_details.error_id[:8]}: {error_details.type.value}\n"
        message += f"Severity: {error_details.severity.value}\n"
        message += f"Message: {error_details.technical_message}\n"
        
        if recovery_result:
            if recovery_result.get("success"):
                message += "Recovery: Successful\n"
            else:
                message += "Recovery: Failed\n"
        
        if error_details.context and error_details.context.endpoint:
            message += f"Endpoint: {error_details.context.endpoint}\n"
        
        return message
    
    def _check_critical_patterns(self, error_details: ErrorDetails):
        """Check for critical error patterns"""
        # Check for repeated critical errors
        recent_errors = self.error_logger.get_recent_errors(
            error_type=error_details.type,
            limit=10
        )
        
        critical_count = sum(
            1 for e in recent_errors
            if e["error_details"]["severity"] == ErrorSeverity.CRITICAL.value
        )
        
        if critical_count >= self.config["critical_error_threshold"]:
            logger.critical(
                f"CRITICAL PATTERN DETECTED: {critical_count} critical errors "
                f"of type {error_details.type.value} in recent history"
            )
            # Could trigger emergency protocols
    
    def get_error_summary(self, time_window=None) -> Dict[str, Any]:
        """Get error summary statistics"""
        return self.error_logger.get_error_summary(time_window)
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        return self.recovery_manager.get_recovery_stats()
    
    def export_error_report(self, format: str = "json") -> str:
        """Export comprehensive error report"""
        return self.error_logger.export_error_report(format)
    
    def configure(self, config: Dict[str, Any]):
        """Update error handler configuration"""
        self.config.update(config)
        logger.info(f"Error handler configuration updated: {config}")