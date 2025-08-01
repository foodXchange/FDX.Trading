"""
Error Tracking Routes
API endpoints for error management dashboard
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse, HTMLResponse
from typing import Optional
import logging
from foodxchange.models.error_tracking import error_tracker
from foodxchange.core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["error-tracking"])


@router.get("/tracking")
async def error_tracking_dashboard(request: Request):
    """Display the error tracking dashboard"""
    from fastapi.templating import Jinja2Templates
    from pathlib import Path
    
    # Get templates directory
    BASE_DIR = Path(__file__).resolve().parent.parent
    templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
    
    # Check authentication - Admin only
    user = get_current_user(request)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    if not user.is_admin:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/dashboard?error=unauthorized", status_code=303)
    
    return templates.TemplateResponse("pages/error_tracking.html", {
        "request": request,
        "current_user": {
            "id": user.user_id,
            "email": user.email,
            "role": user.role,
            "is_admin": user.is_admin
        }
    })


@router.get("/api/errors/list")
async def list_errors(
    request: Request,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    page: Optional[str] = None,
    date_from: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get list of errors with optional filters"""
    try:
        # Check authentication
        user = get_current_user(request)
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        errors = error_tracker.get_errors(
            status=status,
            severity=severity,
            page=page,
            date_from=date_from,
            limit=limit,
            offset=offset
        )
        
        return JSONResponse(content={
            "success": True,
            "errors": errors
        })
        
    except Exception as e:
        logger.error(f"Error listing errors: {e}")
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@router.get("/api/errors/{error_id}")
async def get_error(request: Request, error_id: int):
    """Get specific error details"""
    try:
        # Check authentication
        user = get_current_user(request)
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        error = error_tracker.get_error_by_id(error_id)
        
        if not error:
            raise HTTPException(status_code=404, detail="Error not found")
        
        return JSONResponse(content={
            "success": True,
            "error": error
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting error details: {e}")
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@router.put("/api/errors/{error_id}/status")
async def update_error_status(request: Request, error_id: int):
    """Update error status"""
    try:
        # Check authentication
        user = get_current_user(request)
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        data = await request.json()
        new_status = data.get('status')
        
        if new_status not in ['new', 'in_progress', 'solved']:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        success = error_tracker.update_status(error_id, new_status, user.email)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update status")
        
        return JSONResponse(content={
            "success": True,
            "message": "Status updated successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@router.post("/api/errors/{error_id}/note")
async def add_error_note(request: Request, error_id: int):
    """Add a note to an error"""
    try:
        # Check authentication
        user = get_current_user(request)
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        data = await request.json()
        note = data.get('note')
        
        if not note:
            raise HTTPException(status_code=400, detail="Note is required")
        
        # Add user info to note
        full_note = f"[{user.email}] {note}"
        success = error_tracker.add_note(error_id, full_note)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add note")
        
        return JSONResponse(content={
            "success": True,
            "message": "Note added successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@router.delete("/api/errors/{error_id}")
async def delete_error(request: Request, error_id: int):
    """Delete an error"""
    try:
        # Check authentication
        user = get_current_user(request)
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        success = error_tracker.delete_error(error_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete error")
        
        return JSONResponse(content={
            "success": True,
            "message": "Error deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting: {e}")
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@router.get("/api/errors/stats")
async def get_error_statistics(request: Request):
    """Get error statistics"""
    try:
        # Check authentication
        user = get_current_user(request)
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        stats = error_tracker.get_statistics()
        
        return JSONResponse(content={
            "success": True,
            "statistics": stats
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@router.post("/api/errors/log")
async def log_client_error(request: Request):
    """Log an error from the client side"""
    try:
        data = await request.json()
        
        # Get user info if authenticated
        user = get_current_user(request)
        
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "")
        
        # Extract browser and OS from user agent (simplified)
        browser = "Unknown"
        os = "Unknown"
        if "Chrome" in user_agent:
            browser = "Chrome"
        elif "Firefox" in user_agent:
            browser = "Firefox"
        elif "Safari" in user_agent:
            browser = "Safari"
        elif "Edge" in user_agent:
            browser = "Edge"
            
        if "Windows" in user_agent:
            os = "Windows"
        elif "Mac" in user_agent:
            os = "MacOS"
        elif "Linux" in user_agent:
            os = "Linux"
        elif "Android" in user_agent:
            os = "Android"
        elif "iOS" in user_agent:
            os = "iOS"
        
        # Log the error
        error_id = error_tracker.log_error(
            page=data.get('page', request.url.path),
            error_message=data.get('message', 'Unknown error'),
            stack_trace=data.get('stack'),
            user_email=user.email if user else None,
            user_id=user.user_id if user else None,
            severity=data.get('severity', 'medium'),
            browser=browser,
            os=os,
            ip_address=client_ip,
            request_id=getattr(request.state, 'request_id', None),
            error_type=data.get('type', 'JavaScript Error'),
            additional_data=data.get('additional_data')
        )
        
        return JSONResponse(content={
            "success": True,
            "error_id": error_id
        })
        
    except Exception as e:
        logger.error(f"Error logging client error: {e}")
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)


@router.post("/api/errors/cleanup")
async def cleanup_old_errors(request: Request, days: int = 30):
    """Clean up old resolved errors"""
    try:
        # Check authentication
        user = get_current_user(request)
        if not user or not user.is_admin:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        deleted = error_tracker.cleanup_old_errors(days)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Deleted {deleted} old resolved errors"
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up: {e}")
        return JSONResponse(content={
            "success": False,
            "message": str(e)
        }, status_code=500)