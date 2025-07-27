"""
Notification schemas for API requests/responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class NotificationResponse(BaseModel):
    """Response schema for notification"""
    id: int
    type: str
    priority: str
    title: str
    message: str
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Response schema for notification list"""
    notifications: List[NotificationResponse]
    total_count: int
    unread_count: int
    has_more: bool


class MarkReadRequest(BaseModel):
    """Request schema for marking notification as read"""
    pass  # No additional fields needed, notification ID comes from URL


class BulkMarkReadRequest(BaseModel):
    """Request schema for bulk marking notifications as read"""
    notification_ids: List[int] = Field(..., description="List of notification IDs to mark as read")


class NotificationCreate(BaseModel):
    """Schema for creating notifications"""
    user_id: int
    type: str
    priority: str = "normal"
    title: str
    message: str
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    additional_data: Optional[Dict[str, Any]] = None
    channels: Optional[List[str]] = None
    expires_at: Optional[datetime] = None


class NotificationUpdate(BaseModel):
    """Schema for updating notifications"""
    title: Optional[str] = None
    message: Optional[str] = None
    is_read: Optional[bool] = None