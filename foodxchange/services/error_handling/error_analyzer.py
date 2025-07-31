"""
Error Analyzer Module
Analyzes errors to determine type, severity, and recovery options
"""

import logging
import re
import traceback
from typing import Dict, List, Optional, Any, Type
from datetime import datetime

from .models import (
    ErrorType,
    ErrorSeverity,
    RecoveryAction,
    ErrorDetails,
    RecoveryOption,
    ErrorPattern
)

logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """
    Analyzes errors to extract insights and recommend recovery actions
    """
    
    def __init__(self):
        self.error_patterns = self._load_error_patterns()
        self.severity_rules = self._load_severity_rules()
    
    def _load_error_patterns(self) -> List[ErrorPattern]:
        """Load error detection patterns"""
        return [
            ErrorPattern(
                pattern_id="auth_failed",
                name="Authentication Failed",
                description="User authentication failure",
                error_types=[ErrorType.AUTHENTICATION],
                keywords=["unauthorized", "authentication failed", "invalid credentials"],
                regex_patterns=[r"401\s+unauthorized", r"auth.*fail"],
                severity_override=ErrorSeverity.MEDIUM,
                recovery_actions=[RecoveryAction.NOTIFY]
            ),
            ErrorPattern(
                pattern_id="db_connection",
                name="Database Connection Error",
                description="Database connection failure",
                error_types=[ErrorType.DATABASE],
                keywords=["connection refused", "database error", "connection timeout"],
                regex_patterns=[r"psycopg2.*OperationalError", r"sqlite3.*OperationalError"],
                severity_override=ErrorSeverity.HIGH,
                recovery_actions=[RecoveryAction.RETRY, RecoveryAction.ESCALATE]
            ),
            ErrorPattern(
                pattern_id="api_timeout",
                name="API Timeout",
                description="External API timeout",
                error_types=[ErrorType.EXTERNAL_API, ErrorType.NETWORK],
                keywords=["timeout", "timed out", "connection timeout"],
                regex_patterns=[r"timeout.*exceeded", r"read\s+timeout"],
                severity_override=ErrorSeverity.MEDIUM,
                recovery_actions=[RecoveryAction.RETRY, RecoveryAction.FALLBACK]
            ),
            ErrorPattern(
                pattern_id="file_not_found",
                name="File Not Found",
                description="File system resource not found",
                error_types=[ErrorType.FILE_SYSTEM],
                keywords=["file not found", "no such file", "path does not exist"],
                regex_patterns=[r"FileNotFoundError", r"ENOENT"],
                severity_override=ErrorSeverity.LOW,
                recovery_actions=[RecoveryAction.FALLBACK]
            ),
            ErrorPattern(
                pattern_id="validation_error",
                name="Validation Error",
                description="Data validation failure",
                error_types=[ErrorType.VALIDATION],
                keywords=["validation error", "invalid data", "constraint violation"],
                regex_patterns=[r"ValidationError", r"constraint.*violated"],
                severity_override=ErrorSeverity.LOW,
                recovery_actions=[RecoveryAction.NOTIFY]
            )
        ]
    
    def _load_severity_rules(self) -> Dict[str, Any]:
        """Load severity determination rules"""
        return {
            "keywords": {
                ErrorSeverity.CRITICAL: ["critical", "fatal", "emergency", "system failure"],
                ErrorSeverity.HIGH: ["error", "failure", "unavailable", "down"],
                ErrorSeverity.MEDIUM: ["warning", "degraded", "slow", "timeout"],
                ErrorSeverity.LOW: ["info", "notice", "minor", "recoverable"]
            },
            "http_status": {
                ErrorSeverity.CRITICAL: [500, 503],
                ErrorSeverity.HIGH: [502, 504],
                ErrorSeverity.MEDIUM: [400, 401, 403, 404, 429],
                ErrorSeverity.LOW: [409, 422]
            }
        }
    
    def analyze_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorDetails:
        """Analyze an exception to create detailed error information"""
        try:
            # Extract basic information
            error_message = str(error)
            error_type_name = type(error).__name__
            stack_trace = traceback.format_exc()
            
            # Extract source information
            tb = traceback.extract_tb(error.__traceback__)
            if tb:
                last_frame = tb[-1]
                source_file = last_frame.filename
                source_line = last_frame.lineno
            else:
                source_file = None
                source_line = None
            
            # Determine error type
            error_type = self._determine_error_type(error, error_message)
            
            # Determine severity
            severity = self._determine_severity(error, error_message, error_type)
            
            # Create error details
            error_details = ErrorDetails(
                error_id=self._generate_error_id(),
                type=error_type,
                severity=severity,
                message=self._create_user_message(error_type, error_message),
                technical_message=error_message,
                stack_trace=stack_trace,
                error_code=self._extract_error_code(error),
                http_status=self._extract_http_status(error),
                source_file=source_file,
                source_line=source_line,
                metadata={
                    "exception_type": error_type_name,
                    "context": context or {}
                }
            )
            
            return error_details
            
        except Exception as e:
            logger.error(f"Error analyzing error: {e}")
            # Return a basic error details object
            return ErrorDetails(
                error_id=self._generate_error_id(),
                type=ErrorType.UNKNOWN,
                severity=ErrorSeverity.MEDIUM,
                message="An unexpected error occurred",
                technical_message=str(error)
            )
    
    def _determine_error_type(self, error: Exception, message: str) -> ErrorType:
        """Determine the type of error"""
        # Check error patterns
        for pattern in self.error_patterns:
            if self._matches_pattern(error, message, pattern):
                return pattern.error_types[0]
        
        # Check exception type
        error_type_name = type(error).__name__.lower()
        
        if "validation" in error_type_name:
            return ErrorType.VALIDATION
        elif "auth" in error_type_name:
            return ErrorType.AUTHENTICATION
        elif "permission" in error_type_name or "forbidden" in error_type_name:
            return ErrorType.AUTHORIZATION
        elif "database" in error_type_name or "sql" in error_type_name:
            return ErrorType.DATABASE
        elif "connection" in error_type_name or "timeout" in error_type_name:
            return ErrorType.NETWORK
        elif "file" in error_type_name or "io" in error_type_name:
            return ErrorType.FILE_SYSTEM
        elif "api" in error_type_name or "request" in error_type_name:
            return ErrorType.EXTERNAL_API
        
        return ErrorType.UNKNOWN
    
    def _determine_severity(
        self,
        error: Exception,
        message: str,
        error_type: ErrorType
    ) -> ErrorSeverity:
        """Determine error severity"""
        # Check patterns for severity override
        for pattern in self.error_patterns:
            if self._matches_pattern(error, message, pattern) and pattern.severity_override:
                return pattern.severity_override
        
        # Check keywords
        message_lower = message.lower()
        for severity, keywords in self.severity_rules["keywords"].items():
            if any(keyword in message_lower for keyword in keywords):
                return severity
        
        # Check HTTP status if available
        http_status = self._extract_http_status(error)
        if http_status:
            for severity, statuses in self.severity_rules["http_status"].items():
                if http_status in statuses:
                    return severity
        
        # Default severity by error type
        type_severity = {
            ErrorType.VALIDATION: ErrorSeverity.LOW,
            ErrorType.AUTHENTICATION: ErrorSeverity.MEDIUM,
            ErrorType.AUTHORIZATION: ErrorSeverity.MEDIUM,
            ErrorType.DATABASE: ErrorSeverity.HIGH,
            ErrorType.NETWORK: ErrorSeverity.MEDIUM,
            ErrorType.FILE_SYSTEM: ErrorSeverity.LOW,
            ErrorType.EXTERNAL_API: ErrorSeverity.MEDIUM,
            ErrorType.BUSINESS_LOGIC: ErrorSeverity.MEDIUM,
            ErrorType.SYSTEM: ErrorSeverity.HIGH,
            ErrorType.UNKNOWN: ErrorSeverity.MEDIUM
        }
        
        return type_severity.get(error_type, ErrorSeverity.MEDIUM)
    
    def get_recovery_options(self, error_details: ErrorDetails) -> List[RecoveryOption]:
        """Get recovery options for an error"""
        recovery_options = []
        
        # Check patterns for recovery actions
        for pattern in self.error_patterns:
            if any(error_type == error_details.type for error_type in pattern.error_types):
                for action in pattern.recovery_actions:
                    option = self._create_recovery_option(action, error_details)
                    if option:
                        recovery_options.append(option)
        
        # Add default recovery options based on error type
        if not recovery_options:
            recovery_options = self._get_default_recovery_options(error_details)
        
        return recovery_options
    
    def _create_recovery_option(
        self,
        action: RecoveryAction,
        error_details: ErrorDetails
    ) -> Optional[RecoveryOption]:
        """Create a recovery option"""
        if action == RecoveryAction.RETRY:
            return RecoveryOption(
                action=action,
                description="Retry the operation",
                success_probability=0.7,
                estimated_time=5,
                parameters={"max_attempts": 3, "delay": 2}
            )
        elif action == RecoveryAction.FALLBACK:
            return RecoveryOption(
                action=action,
                description="Use fallback mechanism",
                success_probability=0.9,
                estimated_time=1
            )
        elif action == RecoveryAction.NOTIFY:
            return RecoveryOption(
                action=action,
                description="Notify user of the error",
                success_probability=1.0,
                estimated_time=0
            )
        elif action == RecoveryAction.ESCALATE:
            return RecoveryOption(
                action=action,
                description="Escalate to support team",
                success_probability=0.95,
                estimated_time=60
            )
        
        return None
    
    def _get_default_recovery_options(self, error_details: ErrorDetails) -> List[RecoveryOption]:
        """Get default recovery options based on error type"""
        options = []
        
        if error_details.type in [ErrorType.NETWORK, ErrorType.EXTERNAL_API]:
            options.append(RecoveryOption(
                action=RecoveryAction.RETRY,
                description="Retry the request",
                success_probability=0.6,
                estimated_time=10
            ))
        
        if error_details.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            options.append(RecoveryOption(
                action=RecoveryAction.ESCALATE,
                description="Alert support team",
                success_probability=1.0,
                estimated_time=300
            ))
        
        # Always add notify option
        options.append(RecoveryOption(
            action=RecoveryAction.NOTIFY,
            description="Inform user about the error",
            success_probability=1.0,
            estimated_time=0
        ))
        
        return options
    
    def _matches_pattern(self, error: Exception, message: str, pattern: ErrorPattern) -> bool:
        """Check if error matches a pattern"""
        message_lower = message.lower()
        
        # Check keywords
        if any(keyword in message_lower for keyword in pattern.keywords):
            return True
        
        # Check regex patterns
        for regex in pattern.regex_patterns:
            if re.search(regex, message, re.IGNORECASE):
                return True
        
        return False
    
    def _create_user_message(self, error_type: ErrorType, technical_message: str) -> str:
        """Create user-friendly error message"""
        user_messages = {
            ErrorType.VALIDATION: "The information provided is invalid. Please check and try again.",
            ErrorType.AUTHENTICATION: "Authentication failed. Please check your credentials.",
            ErrorType.AUTHORIZATION: "You don't have permission to perform this action.",
            ErrorType.DATABASE: "We're experiencing database issues. Please try again later.",
            ErrorType.NETWORK: "Network connection error. Please check your internet connection.",
            ErrorType.FILE_SYSTEM: "The requested file could not be found.",
            ErrorType.EXTERNAL_API: "External service is unavailable. Please try again later.",
            ErrorType.BUSINESS_LOGIC: "The operation could not be completed due to business rules.",
            ErrorType.SYSTEM: "A system error occurred. Please contact support if this persists.",
            ErrorType.UNKNOWN: "An unexpected error occurred. Please try again."
        }
        
        return user_messages.get(error_type, "An error occurred. Please try again.")
    
    def _extract_error_code(self, error: Exception) -> Optional[str]:
        """Extract error code from exception"""
        if hasattr(error, 'code'):
            return str(error.code)
        elif hasattr(error, 'errno'):
            return f"E{error.errno}"
        return None
    
    def _extract_http_status(self, error: Exception) -> Optional[int]:
        """Extract HTTP status code from exception"""
        if hasattr(error, 'status_code'):
            return error.status_code
        elif hasattr(error, 'status'):
            return error.status
        elif hasattr(error, 'response') and hasattr(error.response, 'status_code'):
            return error.response.status_code
        return None
    
    def _generate_error_id(self) -> str:
        """Generate unique error ID"""
        import uuid
        return str(uuid.uuid4())