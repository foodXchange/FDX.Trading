"""
Intelligent Notification Service for FoodXchange Platform
Provides advanced notification management with real-time delivery, categorization,
filtering, and AI-powered features for food industry professionals.
"""

import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from foodxchange.database import get_db
from foodxchange.models.user import User
from foodxchange.models.project import Project
from foodxchange.models.supplier import Supplier
from foodxchange.models.buyer import Buyer

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types"""
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    URGENT = "urgent"


class NotificationCategory(Enum):
    """Notification categories"""
    AI_ANALYSIS = "ai_analysis"
    PROJECTS = "projects"
    SUPPLIERS = "suppliers"
    BUYERS = "buyers"
    SYSTEM = "system"
    SECURITY = "security"
    COLLABORATION = "collaboration"


class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(Enum):
    """Notification status"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class NotificationAction:
    """Notification action configuration"""
    label: str
    action: str
    url: Optional[str] = None
    method: str = "GET"
    data: Optional[Dict[str, Any]] = None
    icon: Optional[str] = None
    color: Optional[str] = None


@dataclass
class Notification:
    """Notification data structure"""
    id: str
    user_id: str
    type: NotificationType
    category: NotificationCategory
    priority: NotificationPriority
    title: str
    message: str
    status: NotificationStatus
    created_at: datetime
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    actions: Optional[List[NotificationAction]] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    is_urgent: bool = False
    requires_action: bool = False
    group_id: Optional[str] = None
    parent_id: Optional[str] = None


class IntelligentNotificationService:
    """
    Intelligent notification service with advanced features
    """
    
    def __init__(self):
        self.notifications = {}  # In-memory storage for development
        self.user_preferences = {}
        self.notification_groups = {}
        self.real_time_subscribers = {}
        self.ai_models = {}
        
        # Notification templates
        self.templates = {
            "analysis_complete": {
                "title": "AI Analysis Complete",
                "message": "Analysis for {project_name} has been completed successfully.",
                "type": NotificationType.SUCCESS,
                "category": NotificationCategory.AI_ANALYSIS,
                "priority": NotificationPriority.NORMAL,
                "actions": [
                    NotificationAction("View Results", "view_results", "/projects/{project_id}"),
                    NotificationAction("Export Data", "export_data", "/projects/{project_id}/export")
                ]
            },
            "supplier_added": {
                "title": "New Supplier Added",
                "message": "Supplier {supplier_name} has been added to the platform.",
                "type": NotificationType.INFO,
                "category": NotificationCategory.SUPPLIERS,
                "priority": NotificationPriority.LOW,
                "actions": [
                    NotificationAction("View Supplier", "view_supplier", "/suppliers/{supplier_id}"),
                    NotificationAction("Contact", "contact_supplier", "/suppliers/{supplier_id}/contact")
                ]
            },
            "project_deadline": {
                "title": "Project Deadline Approaching",
                "message": "Project {project_name} deadline is approaching on {deadline}.",
                "type": NotificationType.WARNING,
                "category": NotificationCategory.PROJECTS,
                "priority": NotificationPriority.HIGH,
                "actions": [
                    NotificationAction("View Project", "view_project", "/projects/{project_id}"),
                    NotificationAction("Extend Deadline", "extend_deadline", "/projects/{project_id}/extend")
                ]
            },
            "system_maintenance": {
                "title": "System Maintenance",
                "message": "Scheduled maintenance will begin at {start_time}. Expected duration: {duration}.",
                "type": NotificationType.INFO,
                "category": NotificationCategory.SYSTEM,
                "priority": NotificationPriority.NORMAL,
                "actions": [
                    NotificationAction("View Details", "view_details", "/system/status")
                ]
            },
            "security_alert": {
                "title": "Security Alert",
                "message": "Unusual login activity detected from {location}.",
                "type": NotificationType.ERROR,
                "category": NotificationCategory.SECURITY,
                "priority": NotificationPriority.URGENT,
                "actions": [
                    NotificationAction("Review Activity", "review_activity", "/security/activity"),
                    NotificationAction("Change Password", "change_password", "/profile/security")
                ]
            }
        }

    async def create_notification(
        self,
        user_id: str,
        template_key: str,
        context: Dict[str, Any],
        priority: Optional[NotificationPriority] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """
        Create a new notification using templates
        """
        try:
            template = self.templates.get(template_key)
            if not template:
                raise ValueError(f"Unknown notification template: {template_key}")
            
            # Format message with context
            message = template["message"].format(**context)
            title = template["title"].format(**context) if "{project_name}" in template["title"] else template["title"]
            
            # Create notification
            notification = Notification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                type=priority or template["type"],
                category=template["category"],
                priority=priority or template["priority"],
                title=title,
                message=message,
                status=NotificationStatus.UNREAD,
                created_at=datetime.now(),
                expires_at=expires_at,
                metadata=metadata or {},
                actions=template.get("actions", []),
                related_entity_type=context.get("entity_type"),
                related_entity_id=context.get("entity_id"),
                is_urgent=priority == NotificationPriority.URGENT,
                requires_action=priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]
            )
            
            # Store notification
            if user_id not in self.notifications:
                self.notifications[user_id] = []
            self.notifications[user_id].append(notification)
            
            # Send real-time notification
            await self._send_real_time_notification(user_id, notification)
            
            # Update notification counts
            await self._update_notification_counts(user_id)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise

    async def get_user_notifications(
        self,
        user_id: str,
        status: Optional[NotificationStatus] = None,
        category: Optional[NotificationCategory] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """
        Get user notifications with filtering
        """
        try:
            if user_id not in self.notifications:
                return []
            
            notifications = self.notifications[user_id]
            
            # Apply filters
            if status:
                notifications = [n for n in notifications if n.status == status]
            
            if category:
                notifications = [n for n in notifications if n.category == category]
            
            # Remove expired notifications
            notifications = [n for n in notifications if not n.expires_at or n.expires_at > datetime.now()]
            
            # Sort by priority and creation date
            notifications.sort(key=lambda x: (
                x.priority.value if x.priority else "normal",
                x.created_at
            ), reverse=True)
            
            # Apply pagination
            return notifications[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return []

    async def mark_as_read(self, user_id: str, notification_id: str) -> bool:
        """
        Mark notification as read
        """
        try:
            if user_id not in self.notifications:
                return False
            
            for notification in self.notifications[user_id]:
                if notification.id == notification_id:
                    notification.status = NotificationStatus.READ
                    notification.read_at = datetime.now()
                    await self._update_notification_counts(user_id)
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

    async def mark_all_as_read(self, user_id: str, category: Optional[NotificationCategory] = None) -> int:
        """
        Mark all notifications as read
        """
        try:
            if user_id not in self.notifications:
                return 0
            
            count = 0
            for notification in self.notifications[user_id]:
                if notification.status == NotificationStatus.UNREAD:
                    if not category or notification.category == category:
                        notification.status = NotificationStatus.READ
                        notification.read_at = datetime.now()
                        count += 1
            
            await self._update_notification_counts(user_id)
            return count
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            return 0

    async def delete_notification(self, user_id: str, notification_id: str) -> bool:
        """
        Delete a notification
        """
        try:
            if user_id not in self.notifications:
                return False
            
            self.notifications[user_id] = [
                n for n in self.notifications[user_id] 
                if n.id != notification_id
            ]
            
            await self._update_notification_counts(user_id)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            return False

    async def bulk_delete_notifications(
        self,
        user_id: str,
        notification_ids: List[str]
    ) -> int:
        """
        Delete multiple notifications
        """
        try:
            if user_id not in self.notifications:
                return 0
            
            original_count = len(self.notifications[user_id])
            self.notifications[user_id] = [
                n for n in self.notifications[user_id] 
                if n.id not in notification_ids
            ]
            
            deleted_count = original_count - len(self.notifications[user_id])
            await self._update_notification_counts(user_id)
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error bulk deleting notifications: {e}")
            return 0

    async def archive_notifications(
        self,
        user_id: str,
        notification_ids: List[str]
    ) -> int:
        """
        Archive notifications
        """
        try:
            if user_id not in self.notifications:
                return 0
            
            archived_count = 0
            for notification in self.notifications[user_id]:
                if notification.id in notification_ids:
                    notification.status = NotificationStatus.ARCHIVED
                    archived_count += 1
            
            await self._update_notification_counts(user_id)
            return archived_count
            
        except Exception as e:
            logger.error(f"Error archiving notifications: {e}")
            return 0

    async def get_notification_counts(self, user_id: str) -> Dict[str, int]:
        """
        Get notification counts by status and category
        """
        try:
            if user_id not in self.notifications:
                return {
                    "total": 0,
                    "unread": 0,
                    "urgent": 0,
                    "by_category": {},
                    "by_priority": {}
                }
            
            notifications = self.notifications[user_id]
            
            counts = {
                "total": len(notifications),
                "unread": len([n for n in notifications if n.status == NotificationStatus.UNREAD]),
                "urgent": len([n for n in notifications if n.priority == NotificationPriority.URGENT]),
                "by_category": {},
                "by_priority": {}
            }
            
            # Count by category
            for category in NotificationCategory:
                counts["by_category"][category.value] = len([
                    n for n in notifications 
                    if n.category == category and n.status == NotificationStatus.UNREAD
                ])
            
            # Count by priority
            for priority in NotificationPriority:
                counts["by_priority"][priority.value] = len([
                    n for n in notifications 
                    if n.priority == priority and n.status == NotificationStatus.UNREAD
                ])
            
            return counts
            
        except Exception as e:
            logger.error(f"Error getting notification counts: {e}")
            return {"total": 0, "unread": 0, "urgent": 0, "by_category": {}, "by_priority": {}}

    async def search_notifications(
        self,
        user_id: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        """
        Search notifications with filters
        """
        try:
            if user_id not in self.notifications:
                return []
            
            notifications = self.notifications[user_id]
            
            # Apply text search
            if query:
                query_lower = query.lower()
                notifications = [
                    n for n in notifications
                    if query_lower in n.title.lower() or query_lower in n.message.lower()
                ]
            
            # Apply filters
            if filters:
                if filters.get("category"):
                    notifications = [n for n in notifications if n.category.value == filters["category"]]
                
                if filters.get("priority"):
                    notifications = [n for n in notifications if n.priority.value == filters["priority"]]
                
                if filters.get("status"):
                    notifications = [n for n in notifications if n.status.value == filters["status"]]
                
                if filters.get("date_from"):
                    date_from = datetime.fromisoformat(filters["date_from"])
                    notifications = [n for n in notifications if n.created_at >= date_from]
                
                if filters.get("date_to"):
                    date_to = datetime.fromisoformat(filters["date_to"])
                    notifications = [n for n in notifications if n.created_at <= date_to]
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error searching notifications: {e}")
            return []

    async def get_notification_analytics(self, user_id: str) -> Dict[str, Any]:
        """
        Get notification analytics for user
        """
        try:
            if user_id not in self.notifications:
                return {
                    "total_notifications": 0,
                    "read_rate": 0,
                    "response_time": 0,
                    "category_distribution": {},
                    "priority_distribution": {},
                    "engagement_trends": []
                }
            
            notifications = self.notifications[user_id]
            
            # Calculate read rate
            read_count = len([n for n in notifications if n.status == NotificationStatus.READ])
            read_rate = (read_count / len(notifications)) * 100 if notifications else 0
            
            # Calculate average response time
            response_times = []
            for notification in notifications:
                if notification.read_at and notification.requires_action:
                    response_time = (notification.read_at - notification.created_at).total_seconds()
                    response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Category distribution
            category_distribution = {}
            for category in NotificationCategory:
                category_distribution[category.value] = len([
                    n for n in notifications if n.category == category
                ])
            
            # Priority distribution
            priority_distribution = {}
            for priority in NotificationPriority:
                priority_distribution[priority.value] = len([
                    n for n in notifications if n.priority == priority
                ])
            
            return {
                "total_notifications": len(notifications),
                "read_rate": round(read_rate, 2),
                "response_time": round(avg_response_time, 2),
                "category_distribution": category_distribution,
                "priority_distribution": priority_distribution,
                "engagement_trends": await self._calculate_engagement_trends(user_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting notification analytics: {e}")
            return {}

    async def set_user_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> bool:
        """
        Set user notification preferences
        """
        try:
            self.user_preferences[user_id] = preferences
            return True
            
        except Exception as e:
            logger.error(f"Error setting user preferences: {e}")
            return False

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user notification preferences
        """
        try:
            return self.user_preferences.get(user_id, {
                "email_notifications": True,
                "sms_notifications": False,
                "push_notifications": True,
                "do_not_disturb": False,
                "do_not_disturb_hours": {"start": "22:00", "end": "08:00"},
                "categories": {
                    "ai_analysis": True,
                    "projects": True,
                    "suppliers": True,
                    "buyers": True,
                    "system": True,
                    "security": True,
                    "collaboration": True
                },
                "priorities": {
                    "low": True,
                    "normal": True,
                    "high": True,
                    "urgent": True
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}

    async def subscribe_to_real_time(self, user_id: str, callback) -> bool:
        """
        Subscribe user to real-time notifications
        """
        try:
            if user_id not in self.real_time_subscribers:
                self.real_time_subscribers[user_id] = []
            self.real_time_subscribers[user_id].append(callback)
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to real-time notifications: {e}")
            return False

    async def unsubscribe_from_real_time(self, user_id: str, callback) -> bool:
        """
        Unsubscribe user from real-time notifications
        """
        try:
            if user_id in self.real_time_subscribers:
                self.real_time_subscribers[user_id] = [
                    cb for cb in self.real_time_subscribers[user_id] if cb != callback
                ]
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing from real-time notifications: {e}")
            return False

    async def _send_real_time_notification(self, user_id: str, notification: Notification):
        """
        Send real-time notification to subscribed users
        """
        try:
            if user_id in self.real_time_subscribers:
                notification_data = asdict(notification)
                notification_data["type"] = notification.type.value
                notification_data["category"] = notification.category.value
                notification_data["priority"] = notification.priority.value
                notification_data["status"] = notification.status.value
                notification_data["created_at"] = notification.created_at.isoformat()
                
                for callback in self.real_time_subscribers[user_id]:
                    try:
                        await callback(notification_data)
                    except Exception as e:
                        logger.error(f"Error in real-time notification callback: {e}")
                        
        except Exception as e:
            logger.error(f"Error sending real-time notification: {e}")

    async def _update_notification_counts(self, user_id: str):
        """
        Update notification counts for user
        """
        try:
            counts = await self.get_notification_counts(user_id)
            # In a real implementation, this would update the UI or send to client
            logger.info(f"Updated notification counts for user {user_id}: {counts}")
            
        except Exception as e:
            logger.error(f"Error updating notification counts: {e}")

    async def _calculate_engagement_trends(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Calculate engagement trends for user
        """
        try:
            if user_id not in self.notifications:
                return []
            
            notifications = self.notifications[user_id]
            
            # Group by date and calculate engagement
            trends = []
            for i in range(7):  # Last 7 days
                date = datetime.now() - timedelta(days=i)
                day_notifications = [
                    n for n in notifications
                    if n.created_at.date() == date.date()
                ]
                
                read_count = len([n for n in day_notifications if n.status == NotificationStatus.READ])
                total_count = len(day_notifications)
                
                trends.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "total": total_count,
                    "read": read_count,
                    "engagement_rate": (read_count / total_count * 100) if total_count > 0 else 0
                })
            
            return trends[::-1]  # Reverse to show oldest first
            
        except Exception as e:
            logger.error(f"Error calculating engagement trends: {e}")
            return []

    async def create_system_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        target_users: Optional[List[str]] = None
    ) -> List[Notification]:
        """
        Create system-wide notification
        """
        try:
            notifications = []
            
            # If no target users specified, send to all users
            if not target_users:
                target_users = list(self.notifications.keys())
            
            for user_id in target_users:
                notification = Notification(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    type=notification_type,
                    category=NotificationCategory.SYSTEM,
                    priority=priority,
                    title=title,
                    message=message,
                    status=NotificationStatus.UNREAD,
                    created_at=datetime.now(),
                    is_urgent=priority == NotificationPriority.URGENT,
                    requires_action=priority in [NotificationPriority.HIGH, NotificationPriority.URGENT]
                )
                
                if user_id not in self.notifications:
                    self.notifications[user_id] = []
                self.notifications[user_id].append(notification)
                
                await self._send_real_time_notification(user_id, notification)
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error creating system notification: {e}")
            return []

    async def cleanup_expired_notifications(self) -> int:
        """
        Clean up expired notifications
        """
        try:
            total_cleaned = 0
            current_time = datetime.now()
            
            for user_id in self.notifications:
                original_count = len(self.notifications[user_id])
                self.notifications[user_id] = [
                    n for n in self.notifications[user_id]
                    if not n.expires_at or n.expires_at > current_time
                ]
                total_cleaned += original_count - len(self.notifications[user_id])
            
            return total_cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning up expired notifications: {e}")
            return 0


# Global notification service instance
notification_service = IntelligentNotificationService() 