"""
Simple notification service for sending alerts and messages
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    """Simple service for managing notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        type: str = "info",
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            company_id=company_id,
            title=title,
            message=message,
            type=type,
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return notifications
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({
            "is_read": True,
            "read_at": datetime.utcnow()
        })
        
        self.db.commit()
        return count
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            self.db.delete(notification)
            self.db.commit()
            return True
        
        return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
    
    def create_rfq_notification(self, rfq: Any, supplier_ids: List[int]) -> int:
        """Create notifications for new RFQ"""
        count = 0
        for supplier_id in supplier_ids:
            # Get supplier users
            users = self.db.query(User).filter(
                User.company_id == supplier_id,
                User.is_active == True
            ).all()
            
            for user in users:
                self.create_notification(
                    user_id=user.id,
                    title="New RFQ Available",
                    message=f"New RFQ for {rfq.product_name} - Quantity: {rfq.quantity}",
                    type="rfq",
                    entity_type="rfq",
                    entity_id=rfq.id,
                    company_id=supplier_id
                )
                count += 1
        
        return count
    
    def create_quote_notification(self, quote: Any, rfq: Any) -> Notification:
        """Create notification for new quote"""
        return self.create_notification(
            user_id=rfq.user_id,
            title="New Quote Received",
            message=f"New quote for {rfq.product_name} - ${quote.total_price}",
            type="quote",
            entity_type="quote",
            entity_id=quote.id,
            company_id=rfq.company_id
        )
    
    def create_order_notification(self, order: Any, user_id: int, message: str) -> Notification:
        """Create notification for order update"""
        return self.create_notification(
            user_id=user_id,
            title=f"Order {order.order_number} Update",
            message=message,
            type="order",
            entity_type="order",
            entity_id=order.id
        )