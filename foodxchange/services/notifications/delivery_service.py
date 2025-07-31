"""
Delivery Service Module
Handles notification delivery through various channels
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from abc import ABC, abstractmethod

from .models import Notification, NotificationStatus, NotificationPriority

logger = logging.getLogger(__name__)


class DeliveryChannel(ABC):
    """Abstract base class for delivery channels"""
    
    @abstractmethod
    async def deliver(self, notification: Notification) -> bool:
        """Deliver notification through this channel"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if channel is available"""
        pass


class InAppDeliveryChannel(DeliveryChannel):
    """In-app notification delivery"""
    
    def __init__(self):
        self.websocket_connections: Dict[str, Any] = {}
    
    async def deliver(self, notification: Notification) -> bool:
        """Deliver notification in-app"""
        try:
            # In a real implementation, this would send via WebSocket
            user_id = notification.user_id
            
            if user_id in self.websocket_connections:
                # Simulate WebSocket send
                logger.info(f"Delivered notification {notification.id} via WebSocket to user {user_id}")
                return True
            else:
                # User not connected, notification will be seen on next login
                logger.info(f"User {user_id} not connected, notification queued")
                return True
                
        except Exception as e:
            logger.error(f"Error delivering in-app notification: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if in-app delivery is available"""
        return True
    
    def add_connection(self, user_id: str, connection: Any):
        """Add WebSocket connection"""
        self.websocket_connections[user_id] = connection
    
    def remove_connection(self, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id]


class EmailDeliveryChannel(DeliveryChannel):
    """Email notification delivery"""
    
    def __init__(self):
        self.email_queue: List[Dict[str, Any]] = []
    
    async def deliver(self, notification: Notification) -> bool:
        """Deliver notification via email"""
        try:
            # In a real implementation, this would send an email
            email_data = {
                "to": f"user_{notification.user_id}@example.com",  # Would fetch from user profile
                "subject": notification.title,
                "body": notification.message,
                "notification_id": notification.id,
                "timestamp": datetime.now()
            }
            
            # Queue email for sending
            self.email_queue.append(email_data)
            
            # Simulate async email sending
            await asyncio.sleep(0.1)
            
            logger.info(f"Queued email for notification {notification.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error delivering email notification: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if email delivery is available"""
        # Would check email service configuration
        return True
    
    async def process_email_queue(self):
        """Process queued emails"""
        while self.email_queue:
            email = self.email_queue.pop(0)
            # Send email via email service
            logger.info(f"Sent email: {email['subject']} to {email['to']}")


class PushDeliveryChannel(DeliveryChannel):
    """Push notification delivery"""
    
    def __init__(self):
        self.push_tokens: Dict[str, str] = {}
    
    async def deliver(self, notification: Notification) -> bool:
        """Deliver push notification"""
        try:
            user_id = notification.user_id
            
            if user_id not in self.push_tokens:
                logger.info(f"No push token for user {user_id}")
                return False
            
            # In a real implementation, this would send via push service
            push_data = {
                "token": self.push_tokens[user_id],
                "title": notification.title,
                "body": notification.message,
                "data": {
                    "notification_id": notification.id,
                    "category": notification.category.value
                }
            }
            
            # Simulate push notification sending
            await asyncio.sleep(0.05)
            
            logger.info(f"Sent push notification {notification.id} to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error delivering push notification: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if push delivery is available"""
        # Would check push service configuration
        return True
    
    def register_token(self, user_id: str, token: str):
        """Register push token for user"""
        self.push_tokens[user_id] = token


class DeliveryService:
    """
    Coordinates notification delivery across channels
    """
    
    def __init__(self):
        self.channels = {
            "in_app": InAppDeliveryChannel(),
            "email": EmailDeliveryChannel(),
            "push": PushDeliveryChannel()
        }
        self.delivery_rules = self._load_delivery_rules()
    
    def _load_delivery_rules(self) -> Dict[str, List[str]]:
        """Load delivery rules for different notification types"""
        return {
            NotificationPriority.URGENT: ["in_app", "email", "push"],
            NotificationPriority.HIGH: ["in_app", "push"],
            NotificationPriority.NORMAL: ["in_app"],
            NotificationPriority.LOW: ["in_app"]
        }
    
    async def deliver_notification(
        self,
        notification: Notification,
        channels: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """Deliver notification through specified channels"""
        try:
            # Determine channels based on priority if not specified
            if not channels:
                channels = self.delivery_rules.get(
                    notification.priority,
                    ["in_app"]
                )
            
            # Filter available channels
            available_channels = [
                ch for ch in channels
                if ch in self.channels and self.channels[ch].is_available()
            ]
            
            if not available_channels:
                logger.warning(f"No available channels for notification {notification.id}")
                notification.status = NotificationStatus.FAILED
                return {"error": "No available delivery channels"}
            
            # Deliver through each channel
            results = {}
            delivery_tasks = []
            
            for channel_name in available_channels:
                channel = self.channels[channel_name]
                task = self._deliver_to_channel(notification, channel_name, channel)
                delivery_tasks.append(task)
            
            # Wait for all deliveries
            delivery_results = await asyncio.gather(*delivery_tasks)
            
            for channel_name, success in zip(available_channels, delivery_results):
                results[channel_name] = success
            
            # Update notification status
            if any(results.values()):
                notification.status = NotificationStatus.SENT
                notification.updated_at = datetime.now()
            else:
                notification.status = NotificationStatus.FAILED
                notification.updated_at = datetime.now()
            
            return results
            
        except Exception as e:
            logger.error(f"Error in delivery service: {e}")
            notification.status = NotificationStatus.FAILED
            return {"error": str(e)}
    
    async def _deliver_to_channel(
        self,
        notification: Notification,
        channel_name: str,
        channel: DeliveryChannel
    ) -> bool:
        """Deliver to a specific channel"""
        try:
            logger.info(f"Delivering notification {notification.id} via {channel_name}")
            success = await channel.deliver(notification)
            
            if success:
                logger.info(f"Successfully delivered via {channel_name}")
            else:
                logger.warning(f"Failed to deliver via {channel_name}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error delivering via {channel_name}: {e}")
            return False
    
    def get_channel(self, channel_name: str) -> Optional[DeliveryChannel]:
        """Get a specific delivery channel"""
        return self.channels.get(channel_name)
    
    def register_websocket(self, user_id: str, connection: Any):
        """Register WebSocket connection for in-app delivery"""
        in_app_channel = self.channels.get("in_app")
        if isinstance(in_app_channel, InAppDeliveryChannel):
            in_app_channel.add_connection(user_id, connection)
    
    def unregister_websocket(self, user_id: str):
        """Unregister WebSocket connection"""
        in_app_channel = self.channels.get("in_app")
        if isinstance(in_app_channel, InAppDeliveryChannel):
            in_app_channel.remove_connection(user_id)
    
    def register_push_token(self, user_id: str, token: str):
        """Register push notification token"""
        push_channel = self.channels.get("push")
        if isinstance(push_channel, PushDeliveryChannel):
            push_channel.register_token(user_id, token)
    
    async def process_queues(self):
        """Process any queued deliveries"""
        # Process email queue
        email_channel = self.channels.get("email")
        if isinstance(email_channel, EmailDeliveryChannel):
            await email_channel.process_email_queue()