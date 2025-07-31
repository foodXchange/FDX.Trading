"""
Error Handling Routes for FoodXchange Platform
Provides API endpoints for intelligent error handling and notifications integration
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

from foodxchange.services.error_handling_service import (
    IntelligentErrorHandler, ErrorContext, ErrorType, ErrorSeverity
)

# Initialize the error handler
error_handler = IntelligentErrorHandler()
# Temporarily commented out to avoid circular imports
# from foodxchange.models.user import User
# from foodxchange.auth import get_current_user

# Mock user for now
class User:
    id: int = 1
    email: str = "admin@foodxchange.com"

def get_current_user():
    """Mock function to avoid circular import"""
    return User()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/errors", tags=["errors"])


class ErrorReportRequest(BaseModel):
    """Error report request model"""
    error_id: str
    analysis: Dict[str, Any]
    context: Dict[str, Any]
    recovery_options: list


class ErrorRecoveryRequest(BaseModel):
    """Error recovery request model"""
    error_id: str
    recovery_action: str
    user_feedback: Optional[str] = None


class ErrorResolutionRequest(BaseModel):
    """Error resolution request model"""
    error_id: str
    resolution_method: str
    user_feedback: Optional[str] = None


@router.post("/")
async def report_error(request: ErrorReportRequest, current_user: User = Depends(get_current_user)):
    """
    Report an error for intelligent handling and notifications
    """
    try:
        # Create error context
        context = ErrorContext(
            user_id=str(current_user.id),
            timestamp=datetime.now(),
            workflow_step=request.context.get("workflow_step"),
            related_entity_type=request.context.get("related_entity_type"),
            related_entity_id=request.context.get("related_entity_id"),
            system_state=request.context.get("system_state")
        )

        # Create a mock exception for the error handler
        class MockError(Exception):
            def __init__(self, message):
                self.message = message
                super().__init__(message)

        error = MockError(request.analysis.get("technical_message", "Unknown error"))

        # Handle error through the intelligent error handler
        error_notification = await error_handler.handle_error(
            error=error,
            user_id=str(current_user.id),
            context=context,
            workflow_step=request.context.get("workflow_step")
        )

        return JSONResponse(content={
            "success": True,
            "error_id": error_notification.id,
            "notification_id": error_notification.notification_id,
            "recovery_options": [
                {
                    "action": option.action.value,
                    "label": option.label,
                    "description": option.description,
                    "icon": option.icon,
                    "color": option.color,
                    "automatic": option.automatic
                }
                for option in error_notification.recovery_options
            ],
            "message": "Error reported and handled successfully"
        })

    except Exception as e:
        logger.error(f"Error reporting error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to report error: {str(e)}")


@router.post("/recovery")
async def execute_recovery(request: ErrorRecoveryRequest, current_user: User = Depends(get_current_user)):
    """
    Execute a recovery action for an error
    """
    try:
        # Find the error notification
        error_notification = None
        for error in error_handler.error_history.values():
            if error.id == request.error_id and error.user_id == str(current_user.id):
                error_notification = error
                break

        if not error_notification:
            raise HTTPException(status_code=404, detail="Error not found")

        # Execute recovery action
        success = await error_handler._execute_recovery_action(error_notification, request.recovery_action)

        # Update user feedback if provided
        if request.user_feedback:
            error_notification.user_feedback = request.user_feedback

        return JSONResponse(content={
            "success": success,
            "error_id": request.error_id,
            "recovery_action": request.recovery_action,
            "message": "Recovery action executed successfully" if success else "Recovery action failed"
        })

    except Exception as e:
        logger.error(f"Error executing recovery: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute recovery: {str(e)}")


@router.post("/resolve")
async def resolve_error(request: ErrorResolutionRequest, current_user: User = Depends(get_current_user)):
    """
    Mark an error as resolved
    """
    try:
        # Find the error notification
        error_notification = None
        for error in error_handler.error_history.values():
            if error.id == request.error_id and error.user_id == str(current_user.id):
                error_notification = error
                break

        if not error_notification:
            raise HTTPException(status_code=404, detail="Error not found")

        # Mark as resolved
        await error_handler._mark_error_resolved(error_notification, request.resolution_method)

        # Update user feedback if provided
        if request.user_feedback:
            error_notification.user_feedback = request.user_feedback

        return JSONResponse(content={
            "success": True,
            "error_id": request.error_id,
            "resolution_method": request.resolution_method,
            "message": "Error marked as resolved"
        })

    except Exception as e:
        logger.error(f"Error resolving error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to resolve error: {str(e)}")


@router.get("/analytics")
async def get_error_analytics(current_user: User = Depends(get_current_user)):
    """
    Get error analytics for the current user
    """
    try:
        analytics = await error_handler.get_error_analytics(user_id=str(current_user.id))

        return JSONResponse(content={
            "analytics": analytics,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.get("/history")
async def get_error_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Get user's error history
    """
    try:
        user_errors = [
            {
                "id": error.id,
                "error_type": error.error_details.error_type.value,
                "severity": error.error_details.severity.value,
                "error_code": error.error_details.error_code,
                "user_message": error.error_details.user_friendly_message,
                "created_at": error.created_at.isoformat(),
                "resolved_at": error.resolved_at.isoformat() if error.resolved_at else None,
                "resolution_method": error.resolution_method,
                "status": "resolved" if error.resolved_at else "active"
            }
            for error in error_handler.error_history.values()
            if error.user_id == str(current_user.id)
        ]

        # Sort by creation date (newest first)
        user_errors.sort(key=lambda x: x["created_at"], reverse=True)

        # Apply pagination
        paginated_errors = user_errors[offset:offset + limit]

        return JSONResponse(content={
            "errors": paginated_errors,
            "total": len(user_errors),
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get error history: {str(e)}")


@router.delete("/history")
async def clear_error_history(
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """
    Clear old error history
    """
    try:
        await error_handler.clear_error_history(user_id=str(current_user.id), days=days)

        return JSONResponse(content={
            "success": True,
            "message": f"Cleared error history older than {days} days"
        })

    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear error history: {str(e)}")


@router.get("/patterns")
async def get_error_patterns(current_user: User = Depends(get_current_user)):
    """
    Get common error patterns and suggestions
    """
    try:
        user_errors = [
            error for error in error_handler.error_history.values()
            if error.user_id == str(current_user.id)
        ]

        # Analyze patterns
        error_type_counts = {}
        workflow_step_counts = {}
        time_patterns = {}

        for error in user_errors:
            # Error type distribution
            error_type = error.error_details.error_type.value
            error_type_counts[error_type] = error_type_counts.get(error_type, 0) + 1

            # Workflow step distribution
            workflow_step = error.error_details.context.workflow_step
            if workflow_step:
                workflow_step_counts[workflow_step] = workflow_step_counts.get(workflow_step, 0) + 1

            # Time patterns (hour of day)
            hour = error.created_at.hour
            time_patterns[hour] = time_patterns.get(hour, 0) + 1

        # Generate suggestions
        suggestions = []
        
        # Most common error type
        if error_type_counts:
            most_common_error = max(error_type_counts.items(), key=lambda x: x[1])
            if most_common_error[1] > 3:  # More than 3 occurrences
                suggestions.append({
                    "type": "frequent_error",
                    "title": f"Frequent {most_common_error[0].replace('_', ' ').title()} Errors",
                    "description": f"You've encountered {most_common_error[0].replace('_', ' ')} errors {most_common_error[1]} times",
                    "recommendation": f"Consider reviewing your workflow to prevent {most_common_error[0].replace('_', ' ')} issues"
                })

        # Time-based patterns
        if time_patterns:
            peak_hour = max(time_patterns.items(), key=lambda x: x[1])
            if peak_hour[1] > 2:  # More than 2 errors at this hour
                suggestions.append({
                    "type": "time_pattern",
                    "title": "Peak Error Time",
                    "description": f"Most errors occur around {peak_hour[0]}:00",
                    "recommendation": "Consider scheduling important tasks during off-peak hours"
                })

        return JSONResponse(content={
            "patterns": {
                "error_type_distribution": error_type_counts,
                "workflow_step_distribution": workflow_step_counts,
                "time_patterns": time_patterns
            },
            "suggestions": suggestions,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get error patterns: {str(e)}")


@router.get("/health")
async def error_handler_health_check():
    """
    Health check for error handling service
    """
    try:
        return JSONResponse(content={
            "status": "healthy",
            "service": "intelligent_error_handler",
            "active_errors": len(error_handler.active_recoveries),
            "total_errors": len(error_handler.error_history),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error handler health check failed: {e}")
        raise HTTPException(status_code=503, detail="Error handler service unhealthy")


# Web routes for error handling interface
@router.get("/")
async def error_handling_page():
    """
    Render error handling page
    """
    return {"message": "Error handling page - use POST /api/errors/ for error reporting"} 