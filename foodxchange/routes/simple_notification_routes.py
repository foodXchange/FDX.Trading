"""
Simple notification API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from foodxchange.database import get_db
from foodxchange.auth import get_current_user
from foodxchange.models.user import User
from foodxchange.models.notification import Notification
from foodxchange.services.simple_notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/")
async def get_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications"""
    notification_service = NotificationService(db)
    
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    unread_count = notification_service.get_unread_count(current_user.id)
    
    return {
        "notifications": [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
                "read_at": n.read_at.isoformat() if n.read_at else None,
                "entity_type": n.entity_type,
                "entity_id": n.entity_id
            }
            for n in notifications
        ],
        "unread_count": unread_count,
        "total": len(notifications)
    }


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    notification_service = NotificationService(db)
    
    success = notification_service.mark_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True, "message": "Notification marked as read"}


@router.put("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    notification_service = NotificationService(db)
    
    count = notification_service.mark_all_as_read(current_user.id)
    
    return {
        "success": True,
        "message": f"Marked {count} notifications as read",
        "count": count
    }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    notification_service = NotificationService(db)
    
    success = notification_service.delete_notification(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"success": True, "message": "Notification deleted"}


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    notification_service = NotificationService(db)
    
    count = notification_service.get_unread_count(current_user.id)
    
    return {"unread_count": count}


@router.post("/test")
async def create_test_notification(
    title: str = "Test Notification",
    message: str = "This is a test notification",
    type: str = "info",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a test notification (for development)"""
    notification_service = NotificationService(db)
    
    notification = notification_service.create_notification(
        user_id=current_user.id,
        title=title,
        message=message,
        type=type
    )
    
    return {
        "success": True,
        "notification_id": notification.id,
        "message": "Test notification created"
    }


def include_notification_routes(app):
    """Include notification routes in the main app"""
    app.include_router(router)