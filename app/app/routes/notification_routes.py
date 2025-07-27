"""
Notification API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    MarkReadRequest,
    BulkMarkReadRequest
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])
notification_service = NotificationService()


@router.get("/", response_model=NotificationListResponse)
async def get_user_notifications(
    unread_only: bool = Query(False, description="Return only unread notifications"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Number of notifications to skip"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user notifications with pagination"""
    try:
        notifications = await notification_service.get_user_notifications(
            user_id=current_user.id,
            unread_only=unread_only,
            limit=limit,
            offset=offset,
            db=db
        )
        
        # Get total count for pagination
        total_query = db.query(Notification).filter_by(user_id=current_user.id)
        if unread_only:
            total_query = total_query.filter_by(is_read=False)
        
        # Filter out expired notifications
        total_query = total_query.filter(
            (Notification.expires_at.is_(None)) |
            (Notification.expires_at > datetime.utcnow())
        )
        
        total_count = total_query.count()
        unread_count = db.query(Notification).filter_by(
            user_id=current_user.id, 
            is_read=False
        ).filter(
            (Notification.expires_at.is_(None)) |
            (Notification.expires_at > datetime.utcnow())
        ).count()
        
        return NotificationListResponse(
            notifications=[
                NotificationResponse(
                    id=n.id,
                    type=n.type.value,
                    priority=n.priority.value,
                    title=n.title,
                    message=n.message,
                    action_url=n.action_url,
                    action_text=n.action_text,
                    entity_type=n.entity_type,
                    entity_id=n.entity_id,
                    additional_data=n.additional_data,
                    is_read=n.is_read,
                    created_at=n.created_at,
                    read_at=n.read_at
                ) for n in notifications
            ],
            total_count=total_count,
            unread_count=unread_count,
            has_more=offset + len(notifications) < total_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch notifications: {str(e)}")


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a single notification as read"""
    try:
        # Find the notification
        notification = db.query(Notification).filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        if not notification.is_read:
            notification.mark_as_read()
            db.commit()
        
        return {"message": "Notification marked as read", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")


@router.put("/mark-read")
async def mark_notifications_read(
    request: BulkMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark multiple notifications as read"""
    try:
        count = await notification_service.mark_notifications_as_read(
            user_id=current_user.id,
            notification_ids=request.notification_ids,
            db=db
        )
        
        return {
            "message": f"Marked {count} notifications as read",
            "count": count,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark notifications as read: {str(e)}")


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    try:
        # Find the notification
        notification = db.query(Notification).filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        db.delete(notification)
        db.commit()
        
        return {"message": "Notification deleted", "success": True}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    try:
        count = db.query(Notification).filter_by(
            user_id=current_user.id,
            is_read=False
        ).filter(
            (Notification.expires_at.is_(None)) |
            (Notification.expires_at > datetime.utcnow())
        ).count()
        
        return {"unread_count": count}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get unread count: {str(e)}")


@router.post("/cleanup-expired")
async def cleanup_expired_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clean up expired notifications (admin only for now)"""
    try:
        # TODO: Add admin role check
        count = await notification_service.cleanup_expired_notifications(db)
        
        return {
            "message": f"Cleaned up {count} expired notifications",
            "count": count,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup notifications: {str(e)}")