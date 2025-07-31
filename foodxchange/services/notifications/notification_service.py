"""
Intelligent Notification Service
Main notification service that coordinates all notification functionality
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .models import (
    Notification,
    NotificationType,
    NotificationCategory,
    NotificationPriority,
    NotificationStatus,
    NotificationAction,
    NotificationPreferences
)
from .notification_manager import NotificationManager
from .template_engine import TemplateEngine
from .delivery_service import DeliveryService

logger = logging.getLogger(__name__)


class IntelligentNotificationService:
    """
    Main notification service coordinating all notification functionality
    """
    
    def __init__(self):
        self.manager = NotificationManager()
        self.template_engine = TemplateEngine()
        self.delivery_service = DeliveryService()
        
        # Track active notification streams
        self.active_streams: Dict[str, Any] = {}
    
    async def send_notification(
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
        expires_in: Optional[int] = None,
        channels: Optional[List[str]] = None
    ) -> Optional[Notification]:
        """Send a notification to a user"""
        try:
            # Create notification
            notification = self.manager.create_notification(
                user_id=user_id,
                title=title,
                message=message,
                type=type,
                category=category,
                priority=priority,
                actions=actions,
                metadata=metadata,
                context=context,
                expires_in=expires_in
            )
            
            if not notification:
                return None
            
            # Deliver notification
            delivery_results = await self.delivery_service.deliver_notification(
                notification,
                channels
            )
            
            logger.info(f"Notification {notification.id} delivery results: {delivery_results}")
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return None
    
    async def send_templated_notification(
        self,
        user_id: str,
        template_id: str,
        context: Dict[str, Any],
        channels: Optional[List[str]] = None
    ) -> Optional[Notification]:
        """Send a notification using a template"""
        try:
            # Render notification from template
            rendered = self.template_engine.render_notification(template_id, context)
            
            if not rendered:
                logger.error(f"Failed to render template {template_id}")
                return None
            
            # Send notification
            return await self.send_notification(
                user_id=user_id,
                title=rendered["title"],
                message=rendered["message"],
                type=rendered["type"],
                category=rendered["category"],
                priority=rendered["priority"],
                actions=rendered.get("actions"),
                metadata=rendered.get("metadata"),
                context=context,
                channels=channels
            )
            
        except Exception as e:
            logger.error(f"Error sending templated notification: {e}")
            return None
    
    async def broadcast_notification(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        category: NotificationCategory = NotificationCategory.SYSTEM,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        actions: Optional[List[NotificationAction]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, bool]:
        """Broadcast notification to multiple users"""
        results = {}
        
        try:
            # Create tasks for parallel sending
            tasks = []
            for user_id in user_ids:
                task = self.send_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    type=type,
                    category=category,
                    priority=priority,
                    actions=actions,
                    metadata=metadata
                )
                tasks.append(task)
            
            # Wait for all notifications
            notifications = await asyncio.gather(*tasks)
            
            # Collect results
            for user_id, notification in zip(user_ids, notifications):
                results[user_id] = notification is not None
            
            logger.info(f"Broadcast to {len(user_ids)} users, {sum(results.values())} successful")
            
        except Exception as e:
            logger.error(f"Error broadcasting notification: {e}")
        
        return results
    
    def get_notifications(
        self,
        user_id: str,
        status: Optional[NotificationStatus] = None,
        category: Optional[NotificationCategory] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user"""
        return self.manager.get_user_notifications(
            user_id=user_id,
            status=status,
            category=category,
            limit=limit,
            offset=offset
        )
    
    def get_notification(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """Get a specific notification"""
        return self.manager.get_notification(notification_id, user_id)
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        return self.manager.mark_as_read(notification_id, user_id)
    
    def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read"""
        return self.manager.mark_all_as_read(user_id)
    
    def delete_notification(self, notification_id: str, user_id: str) -> bool:
        """Delete a notification"""
        return self.manager.delete_notification(notification_id, user_id)
    
    def get_unread_count(self, user_id: str) -> int:
        """Get unread notification count"""
        return self.manager.get_unread_count(user_id)
    
    def get_preferences(self, user_id: str) -> NotificationPreferences:
        """Get user notification preferences"""
        return self.manager.get_preferences(user_id)
    
    def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> NotificationPreferences:
        """Update user notification preferences"""
        return self.manager.update_preferences(user_id, preferences)
    
    async def send_ai_analysis_notification(
        self,
        user_id: str,
        analysis_type: str,
        item_name: str,
        analysis_id: str,
        summary: str
    ) -> Optional[Notification]:
        """Send AI analysis completion notification"""
        return await self.send_templated_notification(
            user_id=user_id,
            template_id="ai_analysis_complete",
            context={
                "analysis_type": analysis_type,
                "item_name": item_name,
                "analysis_id": analysis_id,
                "summary": summary
            }
        )
    
    async def send_supplier_match_notification(
        self,
        user_id: str,
        supplier_name: str,
        supplier_id: str,
        product_category: str,
        certifications: str
    ) -> Optional[Notification]:
        """Send supplier match notification"""
        return await self.send_templated_notification(
            user_id=user_id,
            template_id="new_supplier_match",
            context={
                "supplier_name": supplier_name,
                "supplier_id": supplier_id,
                "product_category": product_category,
                "certifications": certifications
            }
        )
    
    async def send_project_update_notification(
        self,
        user_id: str,
        project_name: str,
        project_id: str,
        update_message: str
    ) -> Optional[Notification]:
        """Send project update notification"""
        return await self.send_templated_notification(
            user_id=user_id,
            template_id="project_update",
            context={
                "project_name": project_name,
                "project_id": project_id,
                "update_message": update_message
            }
        )
    
    async def send_security_alert(
        self,
        user_id: str,
        alert_type: str,
        alert_message: str,
        alert_id: str
    ) -> Optional[Notification]:
        """Send security alert notification"""
        return await self.send_templated_notification(
            user_id=user_id,
            template_id="security_alert",
            context={
                "alert_type": alert_type,
                "alert_message": alert_message,
                "alert_id": alert_id
            },
            channels=["in_app", "email", "push"]  # Ensure all channels for security
        )
    
    def register_websocket(self, user_id: str, connection: Any):
        """Register WebSocket connection for real-time notifications"""
        self.delivery_service.register_websocket(user_id, connection)
        self.active_streams[user_id] = connection
    
    def unregister_websocket(self, user_id: str):
        """Unregister WebSocket connection"""
        self.delivery_service.unregister_websocket(user_id)
        if user_id in self.active_streams:
            del self.active_streams[user_id]
    
    def register_push_token(self, user_id: str, token: str):
        """Register push notification token"""
        self.delivery_service.register_push_token(user_id, token)
    
    async def cleanup(self):
        """Cleanup old notifications and process queues"""
        try:
            # Clean up old notifications
            self.manager.cleanup_old_notifications(days=30)
            
            # Process any queued deliveries
            await self.delivery_service.process_queues()
            
            logger.info("Notification cleanup completed")
            
        except Exception as e:
            logger.error(f"Error in notification cleanup: {e}")
    
    def get_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """Get notification statistics for a user"""
        try:
            notifications = self.manager.notifications.get(user_id, [])
            
            stats = {
                "total": len(notifications),
                "unread": self.get_unread_count(user_id),
                "by_category": {},
                "by_type": {},
                "by_priority": {}
            }
            
            # Count by category
            for notification in notifications:
                cat = notification.category.value
                stats["by_category"][cat] = stats["by_category"].get(cat, 0) + 1
                
                typ = notification.type.value
                stats["by_type"][typ] = stats["by_type"].get(typ, 0) + 1
                
                pri = notification.priority.value
                stats["by_priority"][pri] = stats["by_priority"].get(pri, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {}