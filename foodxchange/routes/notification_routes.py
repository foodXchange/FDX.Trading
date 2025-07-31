"""
Notification Routes for FoodXchange Platform
Provides API endpoints for intelligent notification management
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

from foodxchange.services.notification_service import (
    notification_service, Notification, NotificationType, NotificationCategory,
    NotificationPriority, NotificationStatus, NotificationAction
)
from foodxchange.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationRequest(BaseModel):
    """Notification request model"""
    template_key: str
    context: Dict[str, Any]
    priority: Optional[str] = None
    expires_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationFilterRequest(BaseModel):
    """Notification filter request model"""
    status: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: int = 50
    offset: int = 0


class BulkActionRequest(BaseModel):
    """Bulk action request model"""
    action: str  # mark_read, delete, archive
    notification_ids: List[str]
    category: Optional[str] = None


class UserPreferencesRequest(BaseModel):
    """User preferences request model"""
    email_notifications: bool = True
    sms_notifications: bool = False
    push_notifications: bool = True
    do_not_disturb: bool = False
    do_not_disturb_hours: Dict[str, str] = {"start": "22:00", "end": "08:00"}
    categories: Dict[str, bool] = {
        "ai_analysis": True,
        "projects": True,
        "suppliers": True,
        "buyers": True,
        "system": True,
        "security": True,
        "collaboration": True
    }
    priorities: Dict[str, bool] = {
        "low": True,
        "normal": True,
        "high": True,
        "urgent": True
    }


@router.get("/")
async def get_notifications(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50),
    offset: int = Query(0),
    current_user = Depends(get_current_user)
):
    """
    Get user notifications with filtering
    """
    try:
        # Convert string parameters to enums
        notification_status = None
        if status:
            try:
                notification_status = NotificationStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        notification_category = None
        if category:
            try:
                notification_category = NotificationCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        notifications = await notification_service.get_user_notifications(
            user_id=str(current_user.id),
            status=notification_status,
            category=notification_category,
            limit=limit,
            offset=offset
        )
        
        # Convert to JSON-serializable format
        notification_data = []
        for notification in notifications:
            notification_dict = {
                "id": notification.id,
                "type": notification.type.value,
                "category": notification.category.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "status": notification.status.value,
                "created_at": notification.created_at.isoformat(),
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "expires_at": notification.expires_at.isoformat() if notification.expires_at else None,
                "metadata": notification.metadata,
                "is_urgent": notification.is_urgent,
                "requires_action": notification.requires_action,
                "related_entity_type": notification.related_entity_type,
                "related_entity_id": notification.related_entity_id
            }
            
            # Convert actions
            if notification.actions:
                notification_dict["actions"] = [
                    {
                        "label": action.label,
                        "action": action.action,
                        "url": action.url,
                        "method": action.method,
                        "data": action.data,
                        "icon": action.icon,
                        "color": action.color
                    }
                    for action in notification.actions
                ]
            
            notification_data.append(notification_dict)
        
        return JSONResponse(content={
            "notifications": notification_data,
            "total": len(notification_data),
            "limit": limit,
            "offset": offset
        })
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get notifications: {str(e)}")


@router.get("/counts")
async def get_notification_counts(current_user = Depends(get_current_user)):
    """
    Get notification counts for user
    """
    try:
        counts = await notification_service.get_notification_counts(str(current_user.id))
        
        return JSONResponse(content=counts)
        
    except Exception as e:
        logger.error(f"Error getting notification counts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get notification counts: {str(e)}")


@router.post("/mark-read/{notification_id}")
async def mark_notification_read(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """
    Mark notification as read
    """
    try:
        success = await notification_service.mark_as_read(
            user_id=str(current_user.id),
            notification_id=notification_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return JSONResponse(content={
            "success": True,
            "message": "Notification marked as read"
        })
        
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark notification as read: {str(e)}")


@router.post("/mark-all-read")
async def mark_all_notifications_read(
    category: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """
    Mark all notifications as read
    """
    try:
        notification_category = None
        if category:
            try:
                notification_category = NotificationCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        count = await notification_service.mark_all_as_read(
            user_id=str(current_user.id),
            category=notification_category
        )
        
        return JSONResponse(content={
            "success": True,
            "message": f"Marked {count} notifications as read",
            "count": count
        })
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mark notifications as read: {str(e)}")


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user = Depends(get_current_user)
):
    """
    Delete a notification
    """
    try:
        success = await notification_service.delete_notification(
            user_id=str(current_user.id),
            notification_id=notification_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return JSONResponse(content={
            "success": True,
            "message": "Notification deleted"
        })
        
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete notification: {str(e)}")


@router.post("/bulk-action")
async def bulk_notification_action(
    request: BulkActionRequest,
    current_user = Depends(get_current_user)
):
    """
    Perform bulk actions on notifications
    """
    try:
        if request.action == "mark_read":
            count = await notification_service.mark_all_as_read(
                user_id=str(current_user.id)
            )
            message = f"Marked {count} notifications as read"
            
        elif request.action == "delete":
            count = await notification_service.bulk_delete_notifications(
                user_id=str(current_user.id),
                notification_ids=request.notification_ids
            )
            message = f"Deleted {count} notifications"
            
        elif request.action == "archive":
            count = await notification_service.archive_notifications(
                user_id=str(current_user.id),
                notification_ids=request.notification_ids
            )
            message = f"Archived {count} notifications"
            
        else:
            raise HTTPException(status_code=400, detail=f"Invalid action: {request.action}")
        
        return JSONResponse(content={
            "success": True,
            "message": message,
            "count": count
        })
        
    except Exception as e:
        logger.error(f"Error performing bulk action: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to perform bulk action: {str(e)}")


@router.get("/search")
async def search_notifications(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user = Depends(get_current_user)
):
    """
    Search notifications
    """
    try:
        filters = {}
        if category:
            filters["category"] = category
        if priority:
            filters["priority"] = priority
        if status:
            filters["status"] = status
        if date_from:
            filters["date_from"] = date_from
        if date_to:
            filters["date_to"] = date_to
        
        notifications = await notification_service.search_notifications(
            user_id=str(current_user.id),
            query=q,
            filters=filters
        )
        
        # Convert to JSON-serializable format
        notification_data = []
        for notification in notifications:
            notification_dict = {
                "id": notification.id,
                "type": notification.type.value,
                "category": notification.category.value,
                "priority": notification.priority.value,
                "title": notification.title,
                "message": notification.message,
                "status": notification.status.value,
                "created_at": notification.created_at.isoformat(),
                "read_at": notification.read_at.isoformat() if notification.read_at else None,
                "metadata": notification.metadata
            }
            notification_data.append(notification_dict)
        
        return JSONResponse(content={
            "notifications": notification_data,
            "query": q,
            "filters": filters,
            "total": len(notification_data)
        })
        
    except Exception as e:
        logger.error(f"Error searching notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to search notifications: {str(e)}")


@router.get("/analytics")
async def get_notification_analytics(current_user = Depends(get_current_user)):
    """
    Get notification analytics for user
    """
    try:
        analytics = await notification_service.get_notification_analytics(str(current_user.id))
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"Error getting notification analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get notification analytics: {str(e)}")


@router.get("/preferences")
async def get_user_preferences(current_user = Depends(get_current_user)):
    """
    Get user notification preferences
    """
    try:
        preferences = await notification_service.get_user_preferences(str(current_user.id))
        
        return JSONResponse(content=preferences)
        
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user preferences: {str(e)}")


@router.post("/preferences")
async def set_user_preferences(
    request: UserPreferencesRequest,
    current_user = Depends(get_current_user)
):
    """
    Set user notification preferences
    """
    try:
        success = await notification_service.set_user_preferences(
            user_id=str(current_user.id),
            preferences=request.dict()
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save preferences")
        
        return JSONResponse(content={
            "success": True,
            "message": "Notification preferences updated"
        })
        
    except Exception as e:
        logger.error(f"Error setting user preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set user preferences: {str(e)}")


@router.post("/create")
async def create_notification(
    request: NotificationRequest,
    current_user = Depends(get_current_user)
):
    """
    Create a new notification (for testing purposes)
    """
    try:
        # Convert priority string to enum
        priority = None
        if request.priority:
            try:
                priority = NotificationPriority(request.priority)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid priority: {request.priority}")
        
        # Convert expires_at string to datetime
        expires_at = None
        if request.expires_at:
            try:
                expires_at = datetime.fromisoformat(request.expires_at)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid expires_at format: {request.expires_at}")
        
        notification = await notification_service.create_notification(
            user_id=str(current_user.id),
            template_key=request.template_key,
            context=request.context,
            priority=priority,
            expires_at=expires_at,
            metadata=request.metadata
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "Notification created",
            "notification_id": notification.id
        })
        
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create notification: {str(e)}")


@router.post("/system")
async def create_system_notification(
    title: str = Form(...),
    message: str = Form(...),
    notification_type: str = Form("info"),
    priority: str = Form("normal"),
    target_users: Optional[List[str]] = Form(None),
    current_user = Depends(get_current_user)
):
    """
    Create system-wide notification (admin only)
    """
    try:
        # Convert string parameters to enums
        try:
            notif_type = NotificationType(notification_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid notification type: {notification_type}")
        
        try:
            notif_priority = NotificationPriority(priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {priority}")
        
        notifications = await notification_service.create_system_notification(
            title=title,
            message=message,
            notification_type=notif_type,
            priority=notif_priority,
            target_users=target_users
        )
        
        return JSONResponse(content={
            "success": True,
            "message": f"System notification sent to {len(notifications)} users",
            "notification_count": len(notifications)
        })
        
    except Exception as e:
        logger.error(f"Error creating system notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create system notification: {str(e)}")


@router.get("/templates")
async def get_notification_templates():
    """
    Get available notification templates
    """
    try:
        templates = {}
        for key, template in notification_service.templates.items():
            templates[key] = {
                "title": template["title"],
                "message": template["message"],
                "type": template["type"].value,
                "category": template["category"].value,
                "priority": template["priority"].value,
                "actions": [
                    {
                        "label": action.label,
                        "action": action.action,
                        "url": action.url,
                        "method": action.method,
                        "icon": action.icon,
                        "color": action.color
                    }
                    for action in template.get("actions", [])
                ]
            }
        
        return JSONResponse(content={
            "templates": templates
        })
        
    except Exception as e:
        logger.error(f"Error getting notification templates: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get notification templates: {str(e)}")


@router.get("/health")
async def notification_health_check():
    """
    Health check for notification service
    """
    try:
        return JSONResponse(content={
            "status": "healthy",
            "service": "intelligent_notifications",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Notification health check failed: {e}")
        raise HTTPException(status_code=503, detail="Notification service unhealthy")


# WebSocket endpoint for real-time notifications
@router.websocket("/ws/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time notifications
    """
    await websocket.accept()
    
    try:
        # Subscribe to real-time notifications
        async def notification_callback(notification_data):
            await websocket.send_text(json.dumps({
                "type": "notification",
                "data": notification_data
            }))
        
        await notification_service.subscribe_to_real_time(user_id, notification_callback)
        
        # Send initial notification counts
        counts = await notification_service.get_notification_counts(user_id)
        await websocket.send_text(json.dumps({
            "type": "counts",
            "data": counts
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Unsubscribe from real-time notifications
        await notification_service.unsubscribe_from_real_time(user_id, notification_callback) 