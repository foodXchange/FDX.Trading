"""
Enhanced Error Handler with Support System Integration
Automatically logs errors and creates support tickets for critical issues
"""

import logging
import traceback
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import Request
from sqlalchemy.orm import Session

from foodxchange.services.support_service import support_service
from foodxchange.models.support import ErrorSeverity, TicketCategory, TicketPriority
from foodxchange.database import get_db

logger = logging.getLogger(__name__)


class EnhancedErrorHandler:
    """Enhanced error handler with support system integration"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.error_patterns = {
            "authentication": [
                "authentication", "auth", "login", "password", "token", "jwt", "session"
            ],
            "rfq_processing": [
                "rfq", "request", "quote", "processing", "import", "data"
            ],
            "supplier_management": [
                "supplier", "vendor", "contact", "management"
            ],
            "email_intelligence": [
                "email", "mail", "intelligence", "ai", "analysis"
            ],
            "payment_transaction": [
                "payment", "transaction", "billing", "invoice", "money"
            ],
            "ui_ux_issue": [
                "ui", "ux", "interface", "frontend", "display", "render"
            ],
            "system_error": [
                "system", "server", "database", "connection", "timeout"
            ]
        }
    
    def generate_error_id(self) -> str:
        """Generate unique error ID"""
        return f"ERR-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:4].upper()}"
    
    def categorize_error(self, error_message: str, error_type: str) -> Optional[TicketCategory]:
        """Categorize error based on message and type"""
        error_text = f"{error_message} {error_type}".lower()
        
        for category, patterns in self.error_patterns.items():
            for pattern in patterns:
                if pattern.lower() in error_text:
                    return TicketCategory(category)
        
        return TicketCategory.SYSTEM_ERROR
    
    def determine_severity(
        self,
        error_type: str,
        status_code: Optional[int] = None,
        error_message: str = ""
    ) -> ErrorSeverity:
        """Determine error severity based on type and context"""
        error_text = f"{error_type} {error_message}".lower()
        
        # Critical errors
        if any(keyword in error_text for keyword in [
            "database", "connection", "timeout", "memory", "disk", "critical"
        ]):
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        if any(keyword in error_text for keyword in [
            "authentication", "authorization", "payment", "transaction", "data loss"
        ]):
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        if any(keyword in error_text for keyword in [
            "validation", "format", "parsing", "processing"
        ]):
            return ErrorSeverity.MEDIUM
        
        # Default to medium for unknown errors
        return ErrorSeverity.MEDIUM
    
    def extract_browser_info(self, request: Request) -> Dict[str, Any]:
        """Extract browser and device information from request"""
        try:
            user_agent = request.headers.get("user-agent", "")
            accept_language = request.headers.get("accept-language", "")
            accept_encoding = request.headers.get("accept-encoding", "")
            
            return {
                "user_agent": user_agent,
                "accept_language": accept_language,
                "accept_encoding": accept_encoding,
                "headers": dict(request.headers)
            }
        except Exception as e:
            self.logger.warning(f"Failed to extract browser info: {e}")
            return {}
    
    def should_create_ticket(
        self,
        severity: ErrorSeverity,
        error_type: str,
        user_id: Optional[int] = None
    ) -> bool:
        """Determine if a support ticket should be created"""
        # Always create tickets for critical errors
        if severity == ErrorSeverity.CRITICAL:
            return True
        
        # Create tickets for high severity errors
        if severity == ErrorSeverity.HIGH:
            return True
        
        # Create tickets for authentication errors
        if "auth" in error_type.lower() or "login" in error_type.lower():
            return True
        
        # Create tickets for payment/transaction errors
        if "payment" in error_type.lower() or "transaction" in error_type.lower():
            return True
        
        # Don't create tickets for medium/low severity errors unless user is authenticated
        if user_id and severity == ErrorSeverity.MEDIUM:
            return True
        
        return False
    
    async def handle_error(
        self,
        error: Exception,
        request: Request,
        user_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle an error with support system integration"""
        try:
            # Generate error ID
            error_id = self.generate_error_id()
            
            # Extract error information
            error_type = type(error).__name__
            error_message = str(error)
            stack_trace = traceback.format_exc()
            
            # Determine severity and category
            severity = self.determine_severity(error_type, None, error_message)
            category = self.categorize_error(error_message, error_type)
            
            # Extract request information
            url_path = str(request.url.path)
            http_method = request.method
            browser_info = self.extract_browser_info(request)
            request_id = getattr(request.state, 'request_id', None)
            
            # Get database session
            db = next(get_db())
            
            try:
                # Log the error
                error_log = support_service.log_error(
                    db=db,
                    error_id=error_id,
                    error_type=error_type,
                    error_message=error_message,
                    user_id=user_id,
                    request_id=request_id,
                    stack_trace=stack_trace,
                    severity=severity,
                    category=category,
                    url_path=url_path,
                    http_method=http_method,
                    browser_info=browser_info,
                    context_data=context
                )
                
                # Determine if we should create a support ticket
                should_create_ticket = self.should_create_ticket(severity, error_type, user_id)
                ticket_id = None
                
                if should_create_ticket:
                    # Create support ticket
                    ticket_title = f"System Error: {error_type}"
                    ticket_description = f"""
Error Type: {error_type}
Error Message: {error_message}
URL: {url_path}
Method: {http_method}
Severity: {severity.value}
Category: {category.value}

Stack Trace:
{stack_trace}

Context: {context or 'No additional context'}
                    """.strip()
                    
                    ticket = support_service.create_ticket(
                        db=db,
                        user_id=user_id or 1,  # Default to admin if no user
                        title=ticket_title,
                        description=ticket_description,
                        category=category,
                        priority=TicketPriority.HIGH if severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH] else TicketPriority.MEDIUM,
                        error_id=error_id,
                        browser_info=browser_info,
                        device_info={},  # Could be enhanced with device detection
                        steps_to_reproduce="Error occurred during normal operation",
                        expected_behavior="System should function normally",
                        actual_behavior=f"System encountered {error_type}: {error_message}"
                    )
                    ticket_id = ticket.ticket_id
                    
                    # Link error log to ticket
                    error_log.ticket_id = ticket.id
                    db.commit()
                    
                    self.logger.info(f"Created support ticket {ticket_id} for error {error_id}")
                
                return {
                    "error_id": error_id,
                    "ticket_id": ticket_id,
                    "severity": severity.value,
                    "category": category.value,
                    "logged": True,
                    "ticket_created": should_create_ticket
                }
                
            finally:
                db.close()
                
        except Exception as e:
            self.logger.error(f"Error in enhanced error handler: {e}")
            return {
                "error_id": error_id if 'error_id' in locals() else "UNKNOWN",
                "ticket_id": None,
                "severity": "unknown",
                "category": "unknown",
                "logged": False,
                "ticket_created": False,
                "handler_error": str(e)
            }
    
    def get_user_friendly_message(
        self,
        error_type: str,
        severity: ErrorSeverity,
        category: TicketCategory
    ) -> Dict[str, str]:
        """Get user-friendly error messages"""
        messages = {
            "authentication": {
                "title": "Authentication Issue",
                "message": "We're having trouble verifying your identity. Please try logging in again.",
                "action": "Try logging in again or contact support if the problem persists."
            },
            "rfq_processing": {
                "title": "Request Processing Issue",
                "message": "We encountered an issue while processing your request. Your data is safe.",
                "action": "Please try again in a few moments or contact support if the problem continues."
            },
            "supplier_management": {
                "title": "Supplier Management Issue",
                "message": "There was a problem with the supplier management system.",
                "action": "Please try again or contact support for assistance."
            },
            "email_intelligence": {
                "title": "Email Analysis Issue",
                "message": "We're having trouble analyzing your email content.",
                "action": "Please try again or contact support if you need immediate assistance."
            },
            "payment_transaction": {
                "title": "Payment Issue",
                "message": "We encountered a problem with your payment transaction.",
                "action": "Please check your payment method and try again, or contact support immediately."
            },
            "ui_ux_issue": {
                "title": "Interface Issue",
                "message": "There's a display issue with the interface.",
                "action": "Please refresh the page or try again later."
            },
            "system_error": {
                "title": "System Issue",
                "message": "We're experiencing a technical issue. Our team has been notified.",
                "action": "Please try again in a few moments or contact support if the problem persists."
            }
        }
        
        category_key = category.value
        if category_key in messages:
            return messages[category_key]
        
        # Default message
        return {
            "title": "Unexpected Error",
            "message": "An unexpected error occurred. Our team has been notified.",
            "action": "Please try again or contact support if the problem persists."
        }
    
    def get_recovery_suggestions(
        self,
        error_type: str,
        category: TicketCategory
    ) -> List[str]:
        """Get recovery suggestions based on error type and category"""
        suggestions = {
            "authentication": [
                "Clear your browser cache and cookies",
                "Try logging in with a different browser",
                "Check if your session has expired",
                "Verify your login credentials"
            ],
            "rfq_processing": [
                "Check your internet connection",
                "Try refreshing the page",
                "Verify your input data is correct",
                "Try again in a few moments"
            ],
            "supplier_management": [
                "Refresh the page",
                "Check your input data",
                "Try again later",
                "Contact support if urgent"
            ],
            "email_intelligence": [
                "Check your email format",
                "Try with a different email",
                "Verify file attachments",
                "Try again in a few moments"
            ],
            "payment_transaction": [
                "Check your payment method",
                "Verify billing information",
                "Try a different payment method",
                "Contact support immediately"
            ],
            "ui_ux_issue": [
                "Refresh the page",
                "Clear browser cache",
                "Try a different browser",
                "Check your internet connection"
            ],
            "system_error": [
                "Try again in a few moments",
                "Refresh the page",
                "Check your internet connection",
                "Contact support if the problem persists"
            ]
        }
        
        category_key = category.value
        if category_key in suggestions:
            return suggestions[category_key]
        
        return [
            "Try refreshing the page",
            "Check your internet connection",
            "Try again in a few moments",
            "Contact support if the problem persists"
        ]


# Global instance
enhanced_error_handler = EnhancedErrorHandler() 