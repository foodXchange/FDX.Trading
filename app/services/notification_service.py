"""
Notification service for sending alerts and messages
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.order import Order, OrderStatus
from app.models.user import User
from app.models.company import Company
from app.models.rfq import RFQ
from app.models.quote import Quote


logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        from app.services.email_notification_service import email_notification_service
        self.email_service = email_notification_service
        self.sms_service = None    # TODO: Initialize SMS service
        self.push_service = None   # TODO: Initialize push notification service
    
    async def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        company_id: Optional[int] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        action_url: Optional[str] = None,
        action_text: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        channels: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
        db: Session = None
    ) -> Notification:
        """Create a new notification"""
        if channels is None:
            channels = ["in_app"]
        
        if expires_at is None and notification_type in [
            NotificationType.RFQ_EXPIRED,
            NotificationType.QUOTE_EXPIRED,
            NotificationType.PASSWORD_RESET
        ]:
            expires_at = datetime.utcnow() + timedelta(days=30)
        
        notification = Notification(
            user_id=user_id,
            company_id=company_id,
            type=notification_type,
            priority=priority,
            title=title,
            message=message,
            action_url=action_url,
            action_text=action_text,
            entity_type=entity_type,
            entity_id=entity_id,
            additional_data=additional_data or {},
            channels=channels,
            expires_at=expires_at
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Send to external channels
        await self._send_to_channels(notification, db)
        
        return notification
    
    async def send_order_created_notification(self, order: Order, db: Session):
        """Send notification when order is created"""
        try:
            # Get supplier users
            supplier_users = db.query(User).filter_by(
                company_id=order.supplier_company_id,
                is_active=True
            ).all()
            
            # Get buyer company name
            buyer_company = db.query(Company).filter_by(id=order.buyer_company_id).first()
            buyer_name = buyer_company.name if buyer_company else "Unknown Buyer"
            
            for user in supplier_users:
                await self.create_notification(
                    user_id=user.id,
                    company_id=order.supplier_company_id,
                    notification_type=NotificationType.ORDER_PLACED,
                    priority=NotificationPriority.HIGH,
                    title=f"New Order #{order.order_number}",
                    message=f"You have received a new order from {buyer_name} worth ${order.total_amount / 100:.2f}",
                    action_url=f"/orders/{order.id}",
                    action_text="View Order",
                    entity_type="order",
                    entity_id=order.id,
                    additional_data={
                        "order_number": order.order_number,
                        "buyer_company": buyer_name,
                        "total_amount": order.total_amount / 100,
                        "currency": order.currency
                    },
                    channels=["in_app", "email"],
                    db=db
                )
        except Exception as e:
            logger.error(f"Failed to send order created notification: {e}")
    
    async def send_order_status_notification(self, order: Order, old_status: OrderStatus, db: Session):
        """Send notification when order status changes"""
        try:
            # Determine notification type and recipients
            notification_type = self._get_order_status_notification_type(order.status)
            if not notification_type:
                return
            
            # Get company info
            buyer_company = db.query(Company).filter_by(id=order.buyer_company_id).first()
            supplier_company = db.query(Company).filter_by(id=order.supplier_company_id).first()
            
            # Send to buyer
            buyer_users = db.query(User).filter_by(
                company_id=order.buyer_company_id,
                is_active=True
            ).all()
            
            for user in buyer_users:
                title, message = self._get_order_status_message(
                    order, old_status, "buyer", supplier_company.name if supplier_company else "Supplier"
                )
                
                await self.create_notification(
                    user_id=user.id,
                    company_id=order.buyer_company_id,
                    notification_type=notification_type,
                    priority=NotificationPriority.NORMAL,
                    title=title,
                    message=message,
                    action_url=f"/orders/{order.id}",
                    action_text="View Order",
                    entity_type="order",
                    entity_id=order.id,
                    additional_data={
                        "order_number": order.order_number,
                        "old_status": old_status.value,
                        "new_status": order.status.value
                    },
                    channels=["in_app", "email"],
                    db=db
                )
            
            # Send to supplier (except for buyer-only actions)
            if order.status not in [OrderStatus.DELIVERED, OrderStatus.COMPLETED]:
                supplier_users = db.query(User).filter_by(
                    company_id=order.supplier_company_id,
                    is_active=True
                ).all()
                
                for user in supplier_users:
                    title, message = self._get_order_status_message(
                        order, old_status, "supplier", buyer_company.name if buyer_company else "Buyer"
                    )
                    
                    await self.create_notification(
                        user_id=user.id,
                        company_id=order.supplier_company_id,
                        notification_type=notification_type,
                        priority=NotificationPriority.NORMAL,
                        title=title,
                        message=message,
                        action_url=f"/orders/{order.id}",
                        action_text="View Order",
                        entity_type="order",
                        entity_id=order.id,
                        additional_data={
                            "order_number": order.order_number,
                            "old_status": old_status.value,
                            "new_status": order.status.value
                        },
                        channels=["in_app"],
                        db=db
                    )
        except Exception as e:
            logger.error(f"Failed to send order status notification: {e}")
    
    async def send_rfq_notification(self, rfq: RFQ, db: Session):
        """Send notification when RFQ is created"""
        try:
            # Get relevant suppliers based on category
            # TODO: Implement supplier matching logic based on RFQ category
            
            # For now, send to all suppliers
            supplier_users = db.query(User).filter_by(role="supplier", is_active=True).all()
            
            # Get buyer company name
            buyer_company = db.query(Company).filter_by(id=rfq.company_id).first() if rfq.company_id else None
            buyer_name = buyer_company.name if buyer_company else "Unknown Buyer"
            
            for user in supplier_users:
                await self.create_notification(
                    user_id=user.id,
                    company_id=user.company_id,
                    notification_type=NotificationType.NEW_RFQ,
                    priority=NotificationPriority.HIGH,
                    title=f"New RFQ: {rfq.product_name}",
                    message=f"{buyer_name} is looking for {rfq.product_name}. Quantity: {rfq.quantity}",
                    action_url=f"/rfqs/{rfq.id}",
                    action_text="View RFQ",
                    entity_type="rfq",
                    entity_id=rfq.id,
                    additional_data={
                        "rfq_number": rfq.rfq_number,
                        "product_name": rfq.product_name,
                        "quantity": rfq.quantity,
                        "buyer_company": buyer_name
                    },
                    channels=["in_app", "email"],
                    db=db
                )
        except Exception as e:
            logger.error(f"Failed to send RFQ notification: {e}")
    
    async def send_quote_notification(self, quote: Quote, db: Session):
        """Send notification when quote is submitted"""
        try:
            # Get RFQ and buyer info
            rfq = db.query(RFQ).filter_by(id=quote.rfq_id).first()
            if not rfq:
                return
            
            # Get buyer users
            buyer_users = db.query(User).filter_by(
                company_id=rfq.company_id,
                is_active=True
            ).all()
            
            # Get supplier company name  
            from app.models.supplier import Supplier
            supplier = db.query(Supplier).filter_by(id=quote.supplier_id).first()
            supplier_name = supplier.company_name if supplier else "Supplier"
            
            for user in buyer_users:
                await self.create_notification(
                    user_id=user.id,
                    company_id=rfq.company_id,
                    notification_type=NotificationType.NEW_QUOTE,
                    priority=NotificationPriority.HIGH,
                    title=f"New Quote for {rfq.product_name}",
                    message=f"{supplier_name} has submitted a quote for ${quote.total_price:.2f}",
                    action_url=f"/quotes/{quote.id}",
                    action_text="View Quote",
                    entity_type="quote",
                    entity_id=quote.id,
                    additional_data={
                        "rfq_number": rfq.rfq_number,
                        "supplier_name": supplier_name,
                        "quote_price": quote.total_price,
                        "delivery_time": quote.delivery_time
                    },
                    channels=["in_app", "email"],
                    db=db
                )
        except Exception as e:
            logger.error(f"Failed to send quote notification: {e}")
    
    async def send_payment_overdue_notification(self, invoice_id: int, db: Session):
        """Send notification for overdue payments"""
        # TODO: Implement payment overdue notifications
        pass
    
    async def mark_notifications_as_read(self, user_id: int, notification_ids: List[int], db: Session):
        """Mark multiple notifications as read"""
        notifications = db.query(Notification).filter(
            Notification.id.in_(notification_ids),
            Notification.user_id == user_id,
            Notification.is_read == False
        ).all()
        
        for notification in notifications:
            notification.mark_as_read()
        
        db.commit()
        return len(notifications)
    
    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
        db: Session = None
    ) -> List[Notification]:
        """Get notifications for a user"""
        query = db.query(Notification).filter_by(user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        # Filter out expired notifications
        query = query.filter(
            (Notification.expires_at.is_(None)) |
            (Notification.expires_at > datetime.utcnow())
        )
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return notifications
    
    async def cleanup_expired_notifications(self, db: Session):
        """Remove expired notifications"""
        expired_count = db.query(Notification).filter(
            Notification.expires_at < datetime.utcnow()
        ).delete()
        
        db.commit()
        logger.info(f"Cleaned up {expired_count} expired notifications")
        return expired_count
    
    def _get_order_status_notification_type(self, status: OrderStatus) -> Optional[NotificationType]:
        """Get notification type for order status"""
        status_map = {
            OrderStatus.CONFIRMED: NotificationType.ORDER_CONFIRMED,
            OrderStatus.SHIPPED: NotificationType.ORDER_SHIPPED,
            OrderStatus.DELIVERED: NotificationType.ORDER_DELIVERED,
            OrderStatus.CANCELLED: NotificationType.ORDER_CANCELLED,
            OrderStatus.COMPLETED: NotificationType.ORDER_DELIVERED
        }
        return status_map.get(status)
    
    def _get_order_status_message(
        self,
        order: Order,
        old_status: OrderStatus,
        recipient_role: str,
        other_company_name: str
    ) -> tuple:
        """Get title and message for order status notification"""
        status = order.status
        order_num = order.order_number
        
        if status == OrderStatus.CONFIRMED:
            if recipient_role == "buyer":
                title = f"Order {order_num} Confirmed"
                message = f"{other_company_name} has confirmed your order and will begin processing it"
            else:
                title = f"Order {order_num} Confirmed"
                message = f"You have confirmed order {order_num} from {other_company_name}"
        
        elif status == OrderStatus.SHIPPED:
            if recipient_role == "buyer":
                title = f"Order {order_num} Shipped"
                message = f"Your order has been shipped by {other_company_name}"
                if order.tracking_number:
                    message += f". Tracking: {order.tracking_number}"
            else:
                title = f"Order {order_num} Shipped"
                message = f"You have marked order {order_num} as shipped"
        
        elif status == OrderStatus.DELIVERED:
            if recipient_role == "buyer":
                title = f"Order {order_num} Delivered"
                message = f"You have marked order {order_num} as delivered"
            else:
                title = f"Order {order_num} Delivered"
                message = f"{other_company_name} has confirmed delivery of order {order_num}"
        
        elif status == OrderStatus.CANCELLED:
            title = f"Order {order_num} Cancelled"
            message = f"Order {order_num} has been cancelled"
        
        else:
            title = f"Order {order_num} Updated"
            message = f"Order {order_num} status changed to {status.value}"
        
        return title, message
    
    async def _send_to_channels(self, notification: Notification, db: Session):
        """Send notification to external channels"""
        channels = notification.channels or []
        
        if "email" in channels:
            await self._send_email_notification(notification, db)
        
        if "sms" in channels:
            await self._send_sms_notification(notification, db)
        
        if "push" in channels:
            await self._send_push_notification(notification, db)
    
    async def _send_email_notification(self, notification: Notification, db: Session):
        """Send email notification"""
        try:
            # Get user email
            user = db.query(User).filter_by(id=notification.user_id).first()
            if not user or not user.email:
                return
            
            # Prepare email data based on notification type
            email_sent = False
            
            if notification.type == NotificationType.ORDER_PLACED:
                order_data = notification.additional_data
                order_data['order_number'] = order_data.get('order_number', 'N/A')
                order_data['order_date'] = datetime.utcnow().strftime('%Y-%m-%d')
                order_data['total_amount'] = order_data.get('total_amount', 0)
                order_data['tracking_url'] = f"{notification.action_url}"
                
                email_sent = await self.email_service.send_order_confirmation(
                    user.email,
                    order_data
                )
            
            elif notification.type == NotificationType.NEW_RFQ:
                rfq_data = notification.additional_data
                rfq_data['quote_url'] = notification.action_url
                
                email_sent = await self.email_service.send_rfq_notification(
                    user.email,
                    rfq_data
                )
            
            elif notification.type == NotificationType.NEW_QUOTE:
                quote_data = notification.additional_data
                quote_data['comparison_url'] = notification.action_url
                
                email_sent = await self.email_service.send_quote_received(
                    user.email,
                    quote_data
                )
            
            else:
                # Generic notification email
                email_sent = await self.email_service.send_email(
                    user.email,
                    notification.title,
                    notification.message,
                    self._create_generic_html_email(notification)
                )
            
            if email_sent:
                notification.mark_email_sent()
                db.commit()
                logger.info(f"Email notification sent to {user.email}: {notification.title}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    async def _send_sms_notification(self, notification: Notification, db: Session):
        """Send SMS notification"""
        try:
            # TODO: Implement SMS sending logic
            notification.sms_sent = True
            notification.sms_sent_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"SMS notification sent for: {notification.title}")
        except Exception as e:
            logger.error(f"Failed to send SMS notification: {e}")
    
    async def _send_push_notification(self, notification: Notification, db: Session):
        """Send push notification"""
        try:
            # TODO: Implement push notification logic
            notification.push_sent = True
            notification.push_sent_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"Push notification sent for: {notification.title}")
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
    
    def _create_generic_html_email(self, notification: Notification) -> str:
        """Create generic HTML email template"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .content {{ background-color: #f9f9f9; padding: 20px; margin-top: 20px; }}
        .button {{ background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }}
        .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{notification.title}</h1>
        </div>
        
        <div class="content">
            <p>{notification.message}</p>
            
            {f'<center><a href="{notification.action_url}" class="button">{notification.action_text or "View Details"}</a></center>' if notification.action_url else ''}
        </div>
        
        <div class="footer">
            <p>© 2025 FoodXchange. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        return html