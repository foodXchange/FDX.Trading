"""
Recovery Manager Module
Handles error recovery strategies and execution
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import time

from .models import (
    ErrorDetails,
    RecoveryOption,
    RecoveryAction,
    ErrorSeverity
)

logger = logging.getLogger(__name__)


class RecoveryManager:
    """
    Manages error recovery strategies and execution
    """
    
    def __init__(self):
        self.recovery_handlers = self._register_recovery_handlers()
        self.recovery_history: Dict[str, List[Dict[str, Any]]] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
    
    def _register_recovery_handlers(self) -> Dict[RecoveryAction, Callable]:
        """Register recovery action handlers"""
        return {
            RecoveryAction.RETRY: self._handle_retry,
            RecoveryAction.FALLBACK: self._handle_fallback,
            RecoveryAction.NOTIFY: self._handle_notify,
            RecoveryAction.ESCALATE: self._handle_escalate,
            RecoveryAction.IGNORE: self._handle_ignore,
            RecoveryAction.MANUAL: self._handle_manual
        }
    
    async def execute_recovery(
        self,
        error_details: ErrorDetails,
        recovery_option: RecoveryOption,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a recovery action"""
        try:
            start_time = time.time()
            
            # Check circuit breaker
            if self._is_circuit_open(error_details.type.value):
                logger.warning(f"Circuit breaker open for {error_details.type.value}")
                return {
                    "success": False,
                    "reason": "Circuit breaker open",
                    "message": "Recovery temporarily disabled due to repeated failures"
                }
            
            # Get handler
            handler = self.recovery_handlers.get(recovery_option.action)
            if not handler:
                logger.error(f"No handler for recovery action: {recovery_option.action}")
                return {
                    "success": False,
                    "reason": "No handler available"
                }
            
            # Execute recovery
            result = await handler(error_details, recovery_option, context)
            
            # Record recovery attempt
            recovery_time = time.time() - start_time
            self._record_recovery_attempt(
                error_details,
                recovery_option,
                result["success"],
                recovery_time
            )
            
            # Update circuit breaker
            self._update_circuit_breaker(
                error_details.type.value,
                result["success"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing recovery: {e}")
            return {
                "success": False,
                "reason": "Recovery execution failed",
                "error": str(e)
            }
    
    async def _handle_retry(
        self,
        error_details: ErrorDetails,
        recovery_option: RecoveryOption,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle retry recovery action"""
        try:
            max_attempts = recovery_option.parameters.get("max_attempts", 3)
            delay = recovery_option.parameters.get("delay", 2)
            backoff_factor = recovery_option.parameters.get("backoff_factor", 2)
            
            # Get retry function from context
            retry_func = context.get("retry_function") if context else None
            if not retry_func:
                return {
                    "success": False,
                    "reason": "No retry function provided"
                }
            
            # Retry with exponential backoff
            for attempt in range(max_attempts):
                try:
                    logger.info(f"Retry attempt {attempt + 1}/{max_attempts}")
                    
                    # Execute retry
                    result = await retry_func()
                    
                    return {
                        "success": True,
                        "attempt": attempt + 1,
                        "result": result
                    }
                    
                except Exception as e:
                    if attempt < max_attempts - 1:
                        wait_time = delay * (backoff_factor ** attempt)
                        logger.info(f"Retry failed, waiting {wait_time}s before next attempt")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All retry attempts failed: {e}")
            
            return {
                "success": False,
                "reason": "All retry attempts exhausted",
                "attempts": max_attempts
            }
            
        except Exception as e:
            logger.error(f"Error in retry handler: {e}")
            return {
                "success": False,
                "reason": "Retry handler error",
                "error": str(e)
            }
    
    async def _handle_fallback(
        self,
        error_details: ErrorDetails,
        recovery_option: RecoveryOption,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle fallback recovery action"""
        try:
            # Get fallback function from context
            fallback_func = context.get("fallback_function") if context else None
            if not fallback_func:
                # Use default fallback based on error type
                return await self._get_default_fallback(error_details, context)
            
            # Execute fallback
            result = await fallback_func()
            
            return {
                "success": True,
                "fallback_used": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Error in fallback handler: {e}")
            return {
                "success": False,
                "reason": "Fallback handler error",
                "error": str(e)
            }
    
    async def _handle_notify(
        self,
        error_details: ErrorDetails,
        recovery_option: RecoveryOption,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle notify recovery action"""
        try:
            # Get notification service from context
            notification_service = context.get("notification_service") if context else None
            
            if notification_service:
                # Send notification
                user_id = context.get("user_id")
                if user_id:
                    await notification_service.send_notification(
                        user_id=user_id,
                        title="Error Occurred",
                        message=error_details.message,
                        type="error",
                        metadata={
                            "error_id": error_details.error_id,
                            "error_type": error_details.type.value
                        }
                    )
            
            return {
                "success": True,
                "notified": True,
                "message": "User has been notified"
            }
            
        except Exception as e:
            logger.error(f"Error in notify handler: {e}")
            return {
                "success": False,
                "reason": "Notify handler error",
                "error": str(e)
            }
    
    async def _handle_escalate(
        self,
        error_details: ErrorDetails,
        recovery_option: RecoveryOption,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle escalate recovery action"""
        try:
            # Log critical error for monitoring
            logger.critical(
                f"ESCALATED ERROR: {error_details.error_id}",
                extra={
                    "error_details": error_details.to_dict(),
                    "context": context
                }
            )
            
            # Send alert to support team
            # In production, this would integrate with PagerDuty, Slack, etc.
            alert_sent = await self._send_support_alert(error_details, context)
            
            return {
                "success": alert_sent,
                "escalated": True,
                "support_ticket": f"TICKET-{error_details.error_id[:8]}"
            }
            
        except Exception as e:
            logger.error(f"Error in escalate handler: {e}")
            return {
                "success": False,
                "reason": "Escalate handler error",
                "error": str(e)
            }
    
    async def _handle_ignore(
        self,
        error_details: ErrorDetails,
        recovery_option: RecoveryOption,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle ignore recovery action"""
        # Log that error was ignored
        logger.info(f"Error {error_details.error_id} ignored by recovery policy")
        
        return {
            "success": True,
            "ignored": True,
            "message": "Error ignored as per recovery policy"
        }
    
    async def _handle_manual(
        self,
        error_details: ErrorDetails,
        recovery_option: RecoveryOption,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle manual recovery action"""
        # Queue for manual intervention
        logger.warning(f"Error {error_details.error_id} requires manual intervention")
        
        return {
            "success": False,
            "manual_required": True,
            "message": "Manual intervention required",
            "instructions": recovery_option.parameters.get("instructions", "Contact system administrator")
        }
    
    async def _get_default_fallback(
        self,
        error_details: ErrorDetails,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get default fallback based on error type"""
        # Return cached data if available
        if context and "cached_data" in context:
            return {
                "success": True,
                "fallback_used": True,
                "cached": True,
                "result": context["cached_data"]
            }
        
        # Return default values
        return {
            "success": True,
            "fallback_used": True,
            "default": True,
            "result": context.get("default_value") if context else None
        }
    
    async def _send_support_alert(
        self,
        error_details: ErrorDetails,
        context: Optional[Dict[str, Any]]
    ) -> bool:
        """Send alert to support team"""
        try:
            # In production, integrate with alerting service
            # For now, just log
            logger.critical(
                f"SUPPORT ALERT: {error_details.error_id}",
                extra={
                    "error_details": error_details.to_dict(),
                    "context": context.__dict__ if hasattr(context, '__dict__') else context
                }
            )
            
            # In production, this would send to:
            # - PagerDuty
            # - Slack
            # - Email
            # - SMS
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send support alert: {e}")
            return False
    
    def _record_recovery_attempt(
        self,
        error_details: ErrorDetails,
        recovery_option: RecoveryOption,
        success: bool,
        recovery_time: float
    ):
        """Record recovery attempt for analysis"""
        error_key = f"{error_details.type.value}_{recovery_option.action.value}"
        
        if error_key not in self.recovery_history:
            self.recovery_history[error_key] = []
        
        self.recovery_history[error_key].append({
            "error_id": error_details.error_id,
            "timestamp": datetime.now(),
            "success": success,
            "recovery_time": recovery_time,
            "severity": error_details.severity.value
        })
        
        # Keep only recent history (last 100 attempts)
        if len(self.recovery_history[error_key]) > 100:
            self.recovery_history[error_key] = self.recovery_history[error_key][-100:]
    
    def _is_circuit_open(self, error_type: str) -> bool:
        """Check if circuit breaker is open for error type"""
        if error_type not in self.circuit_breakers:
            return False
        
        breaker = self.circuit_breakers[error_type]
        
        # Check if circuit is open
        if breaker["state"] == "open":
            # Check if enough time has passed to half-open
            if datetime.now() > breaker["open_until"]:
                breaker["state"] = "half-open"
                return False
            return True
        
        return False
    
    def _update_circuit_breaker(self, error_type: str, success: bool):
        """Update circuit breaker state"""
        if error_type not in self.circuit_breakers:
            self.circuit_breakers[error_type] = {
                "state": "closed",
                "failures": 0,
                "successes": 0,
                "last_failure": None
            }
        
        breaker = self.circuit_breakers[error_type]
        
        if success:
            breaker["successes"] += 1
            breaker["failures"] = 0
            
            # Close circuit if enough successes
            if breaker["state"] == "half-open" and breaker["successes"] >= 3:
                breaker["state"] = "closed"
        else:
            breaker["failures"] += 1
            breaker["successes"] = 0
            breaker["last_failure"] = datetime.now()
            
            # Open circuit if too many failures
            if breaker["failures"] >= 5:
                breaker["state"] = "open"
                breaker["open_until"] = datetime.now() + timedelta(minutes=5)
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery statistics"""
        stats = {}
        
        for key, attempts in self.recovery_history.items():
            success_count = sum(1 for a in attempts if a["success"])
            total_count = len(attempts)
            
            stats[key] = {
                "total_attempts": total_count,
                "success_rate": success_count / total_count if total_count > 0 else 0,
                "average_recovery_time": sum(a["recovery_time"] for a in attempts) / total_count if total_count > 0 else 0
            }
        
        return stats