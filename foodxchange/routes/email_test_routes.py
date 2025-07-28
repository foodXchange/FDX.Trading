"""Email Test Routes for testing email notifications"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime

from foodxchange.database import get_db
from foodxchange.services.email_notification_service import email_notification_service
from foodxchange.services.notification_service import NotificationService
from foodxchange.models.notification import NotificationType, NotificationPriority

router = APIRouter(prefix="/api/email-test", tags=["Email Test"])

class TestEmailRequest(BaseModel):
    to_email: EmailStr
    email_type: str = "welcome"  # welcome, order, rfq, quote, password_reset
    test_data: Optional[Dict] = None

@router.get("/status")
async def email_status():
    """Check email service status"""
    return {
        "email_configured": email_notification_service.is_configured,
        "email_provider": "Azure Communication Services" if email_notification_service.use_azure else "SMTP",
        "smtp_host": email_notification_service.smtp_host if not email_notification_service.use_azure else None,
        "smtp_port": email_notification_service.smtp_port if not email_notification_service.use_azure else None,
        "azure_configured": email_notification_service.use_azure,
        "from_email": email_notification_service.from_email
    }

@router.post("/send-test")
async def send_test_email(request: TestEmailRequest):
    """Send a test email"""
    try:
        success = False
        
        if request.email_type == "welcome":
            user_data = request.test_data or {
                "name": "Test User",
                "dashboard_url": "https://www.fdx.trading/dashboard"
            }
            success = await email_notification_service.send_welcome_email(
                request.to_email,
                user_data
            )
        
        elif request.email_type == "order":
            order_data = request.test_data or {
                "order_number": "ORD-2025-001",
                "order_date": datetime.now().strftime('%Y-%m-%d'),
                "total_amount": 1250.50,
                "items": [
                    {"name": "Organic Olive Oil", "quantity": 10, "price": 125.05}
                ],
                "delivery_address": "123 Food Street, Culinary City, CC 12345",
                "expected_delivery": "3-5 business days",
                "tracking_url": "https://www.fdx.trading/orders/ORD-2025-001"
            }
            success = await email_notification_service.send_order_confirmation(
                request.to_email,
                order_data
            )
        
        elif request.email_type == "rfq":
            rfq_data = request.test_data or {
                "product_name": "Premium Greek Olive Oil",
                "quantity": "500 kg",
                "delivery_date": "December 15, 2025",
                "location": "New York, USA",
                "additional_requirements": "Must be extra virgin, cold-pressed with organic certification",
                "quote_url": "https://www.fdx.trading/rfqs/123/quote",
                "expiry_date": "November 30, 2025"
            }
            success = await email_notification_service.send_rfq_notification(
                request.to_email,
                rfq_data
            )
        
        elif request.email_type == "quote":
            quote_data = request.test_data or {
                "supplier_name": "Mediterranean Suppliers Ltd",
                "product_name": "Premium Greek Olive Oil",
                "price": 25.50,
                "unit": "kg",
                "total_price": 12750.00,
                "delivery_time": "10-12 business days",
                "comparison_url": "https://www.fdx.trading/quotes/comparison?rfq=123"
            }
            success = await email_notification_service.send_quote_received(
                request.to_email,
                quote_data
            )
        
        elif request.email_type == "password_reset":
            reset_data = request.test_data or {
                "reset_url": "https://www.fdx.trading/reset-password?token=test-token-123"
            }
            success = await email_notification_service.send_password_reset(
                request.to_email,
                reset_data
            )
        
        else:
            # Generic test email
            success = await email_notification_service.send_email(
                request.to_email,
                "Test Email from FoodXchange",
                "This is a test email to verify email configuration.",
                "<h1>Test Email</h1><p>This is a test email with <strong>HTML</strong> content.</p>"
            )
        
        if success:
            return {"success": True, "message": f"Test {request.email_type} email sent to {request.to_email}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email. Check configuration.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-notification")
async def test_notification_email(
    request: TestEmailRequest,
    db: Session = Depends(get_db)
):
    """Test email notification through notification service"""
    try:
        # Create a test user ID (in real app, would get from database)
        test_user_id = 1
        
        notification_service = NotificationService()
        
        # Create a test notification
        notification = await notification_service.create_notification(
            user_id=test_user_id,
            notification_type=NotificationType.SYSTEM,
            title="Test Notification",
            message="This is a test notification from FoodXchange",
            priority=NotificationPriority.NORMAL,
            action_url="https://www.fdx.trading",
            action_text="Visit FoodXchange",
            channels=["in_app", "email"],
            db=db
        )
        
        return {
            "success": True,
            "notification_id": notification.id,
            "message": "Test notification created and email sent"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))