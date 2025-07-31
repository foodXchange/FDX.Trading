"""
Notification Manager Module
Handles notification creation, storage, and retrieval
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from collections import defaultdict

from .models import (
    Notification,
    NotificationType,
    NotificationCategory,
    NotificationPriority,
    NotificationStatus,
    NotificationAction,
    NotificationPreferences
)

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Manages notification lifecycle and storage
    """
    
    def __init__(self):
        # In-memory storage (replace with database in production)
        self.notifications: Dict[str, List[Notification]] = defaultdict(list)
        self.preferences: Dict[str, NotificationPreferences] = {}
        self.notification_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        category: NotificationCategory = NotificationCategory.SYSTEM,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        actions: Optional[List[NotificationAction]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        expires_in: Optional[int] = None
    ) -> Notification:
        """Create a new notification"""
        try:
            # Check user preferences
            prefs = self.get_preferences(user_id)
            if not prefs.is_category_enabled(category):
                logger.info(f"Category {category.value} disabled for user {user_id}")
                return None
            
            # Check frequency limit
            if self._check_frequency_limit(user_id, prefs):
                logger.warning(f"Frequency limit reached for user {user_id}")
                return None
            
            # Create notification
            now = datetime.now()
            notification = Notification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                title=title,
                message=message,
                type=type,
                category=category,
                priority=priority,
                status=NotificationStatus.PENDING,
                created_at=now,
                updated_at=now,
                actions=actions or [],
                metadata=metadata or {},
                context=context or {},
                expires_at=now + timedelta(minutes=expires_in) if expires_in else None
            )
            
            # Store notification
            self.notifications[user_id].append(notification)
            self.notification_counts[user_id][now.date().isoformat()] += 1
            
            # Limit stored notifications per user
            if len(self.notifications[user_id]) > 100:
                self.notifications[user_id] = self.notifications[user_id][-100:]
            
            logger.info(f"Created notification {notification.id} for user {user_id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return None
    
    def get_notification(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """Get a specific notification"""
        for notification in self.notifications.get(user_id, []):
            if notification.id == notification_id:
                return notification
        return None
    
    def get_user_notifications(
        self,
        user_id: str,
        status: Optional[NotificationStatus] = None,
        category: Optional[NotificationCategory] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user"""
        try:
            user_notifications = self.notifications.get(user_id, [])
            
            # Filter by status
            if status:
                user_notifications = [n for n in user_notifications if n.status == status]
            
            # Filter by category
            if category:
                user_notifications = [n for n in user_notifications if n.category == category]
            
            # Remove expired notifications
            user_notifications = [n for n in user_notifications if not n.is_expired()]
            
            # Sort by priority and created date
            user_notifications.sort(
                key=lambda n: (
                    -self._priority_value(n.priority),
                    -n.created_at.timestamp()
                )
            )
            
            # Apply pagination
            return user_notifications[offset:offset + limit]
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            notification = self.get_notification(notification_id, user_id)
            if notification and notification.status != NotificationStatus.READ:
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.now()
                notification.updated_at = datetime.now()
                logger.info(f"Marked notification {notification_id} as read")
                return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read for a user"""
        count = 0
        try:
            for notification in self.notifications.get(user_id, []):
                if notification.status != NotificationStatus.READ:
                    notification.status = NotificationStatus.READ
                    notification.read_at = datetime.now()
                    notification.updated_at = datetime.now()
                    count += 1
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
        except Exception as e:
            logger.error(f"Error marking all as read: {e}")
            return 0
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        try:
            user_notifications = self.notifications.get(user_id, [])
            for i, notification in enumerate(user_notifications):
                if notification.id == notification_id:
                    del user_notifications[i]
                    logger.info(f"Deleted notification {notification_id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            return False
    
    def get_unread_count(self, user_id: str) -> int:
        """Get count of unread notifications"""
        try:
            count = sum(
                1 for n in self.notifications.get(user_id, [])
                if n.status != NotificationStatus.READ and not n.is_expired()
            )
            return count
        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            return 0
    
    def get_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences"""
        if user_id not in self.preferences:
            # Create default preferences
            self.preferences[user_id] = NotificationPreferences(user_id=user_id)
        return self.preferences[user_id]
    
    def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> NotificationPreferences:
        """Update user notification preferences"""
        try:
            prefs = self.get_preferences(user_id)
            
            # Update fields
            for key, value in preferences.items():
                if hasattr(prefs, key):
                    setattr(prefs, key, value)
            
            logger.info(f"Updated preferences for user {user_id}")
            return prefs
            
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return self.get_preferences(user_id)
    
    def _check_frequency_limit(self, user_id: str, prefs: NotificationPreferences) -> bool:
        """Check if user has reached frequency limit"""
        today = datetime.now().date().isoformat()
        count = self.notification_counts[user_id][today]
        return count >= prefs.frequency_limit
    
    def _priority_value(self, priority: NotificationPriority) -> int:
        """Get numeric value for priority"""
        priority_values = {
            NotificationPriority.LOW: 1,
            NotificationPriority.NORMAL: 2,
            NotificationPriority.HIGH: 3,
            NotificationPriority.URGENT: 4
        }
        return priority_values.get(priority, 2)
    
    def cleanup_old_notifications(self, days: int = 30):
        """Clean up old notifications"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            for user_id in list(self.notifications.keys()):
                user_notifications = self.notifications[user_id]
                # Keep only recent notifications
                self.notifications[user_id] = [
                    n for n in user_notifications
                    if n.created_at > cutoff_date
                ]
                
                # Remove user entry if no notifications left
                if not self.notifications[user_id]:
                    del self.notifications[user_id]
            
            logger.info(f"Cleaned up notifications older than {days} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {e}")