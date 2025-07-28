"""
Email Notification Service for FoodXchange
Handles sending notification emails with templates
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
import logging
from datetime import datetime
from jinja2 import Template

from app.config import get_settings

logger = logging.getLogger(__name__)

# Azure Communication Services imports
try:
    from azure.communication.email import EmailClient
    from azure.communication.email.models import EmailAddress, EmailContent, EmailMessage, EmailRecipients
    AZURE_EMAIL_AVAILABLE = True
except ImportError:
    AZURE_EMAIL_AVAILABLE = False
    logger.warning("Azure Communication Services Email not available. Install with: pip install azure-communication-email")


class EmailNotificationService:
    """Service for sending notification emails"""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Azure Communication Services configuration
        self.azure_email_connection_string = os.getenv("AZURE_EMAIL_CONNECTION_STRING")
        self.azure_email_sender = os.getenv("AZURE_EMAIL_SENDER", "DoNotReply@foodxchange.com")
        self.use_azure = bool(self.azure_email_connection_string) and AZURE_EMAIL_AVAILABLE
        
        # SMTP configuration
        self.smtp_host = self.settings.smtp_host or "smtp.gmail.com"
        self.smtp_port = self.settings.smtp_port or 587
        self.smtp_username = self.settings.smtp_username
        self.smtp_password = self.settings.smtp_password
        self.from_email = self.smtp_username or self.azure_email_sender or "noreply@foodxchange.com"
        self.from_name = "FoodXchange"
        
        # Initialize Azure Email Client if available
        self.azure_email_client = None
        if self.use_azure:
            try:
                self.azure_email_client = EmailClient.from_connection_string(self.azure_email_connection_string)
                logger.info("Azure Communication Services Email client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Email Client: {e}")
                self.use_azure = False
        
        # Check if email is configured
        self.is_configured = self.use_azure or bool(self.smtp_username and self.smtp_password)
        
        if not self.is_configured:
            logger.warning("Email service not configured. Set either Azure Communication Services or SMTP credentials in .env")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send an email"""
        if not self.is_configured:
            logger.warning(f"Email not sent (not configured): {subject} to {to_email}")
            return False
        
        try:
            # Use Azure Communication Services if available
            if self.use_azure and self.azure_email_client:
                return await self._send_azure_email(to_email, subject, body_text, body_html, cc, bcc)
            else:
                return await self._send_smtp_email(to_email, subject, body_text, body_html, cc, bcc)
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    async def _send_azure_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send email using Azure Communication Services"""
        try:
            # Create email content
            email_content = EmailContent(
                subject=subject,
                plain_text=body_text
            )
            
            if body_html:
                email_content.html = body_html
            
            # Create recipients
            to_recipients = [EmailAddress(address=to_email)]
            cc_recipients = [EmailAddress(address=email) for email in (cc or [])]
            bcc_recipients = [EmailAddress(address=email) for email in (bcc or [])]
            
            email_recipients = EmailRecipients(
                to=to_recipients,
                cc=cc_recipients if cc_recipients else None,
                bcc=bcc_recipients if bcc_recipients else None
            )
            
            # Create message
            message = EmailMessage(
                sender_address=self.azure_email_sender,
                recipients=email_recipients,
                content=email_content
            )
            
            # Send email
            poller = self.azure_email_client.begin_send(message)
            result = poller.result()
            
            logger.info(f"Azure email sent successfully: {subject} to {to_email}, Message ID: {result.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Azure email: {str(e)}")
            return False
    
    async def _send_smtp_email(
        self,
        to_email: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Add text part
            text_part = MIMEText(body_text, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if body_html:
                html_part = MIMEText(body_html, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                
                # Combine all recipients
                all_recipients = [to_email]
                if cc:
                    all_recipients.extend(cc)
                if bcc:
                    all_recipients.extend(bcc)
                
                server.send_message(msg, to_addrs=all_recipients)
            
            logger.info(f"SMTP email sent successfully: {subject} to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMTP email: {str(e)}")
            return False
    
    async def send_order_confirmation(
        self,
        to_email: str,
        order_data: Dict
    ) -> bool:
        """Send order confirmation email"""
        subject = f"Order Confirmation - #{order_data['order_number']}"
        
        # Text version
        body_text = f"""
Order Confirmation

Thank you for your order!

Order Number: {order_data['order_number']}
Date: {order_data['order_date']}
Total: ${order_data['total_amount']:.2f}

Items:
"""
        for item in order_data.get('items', []):
            body_text += f"- {item['name']} (Qty: {item['quantity']}) - ${item['price']:.2f}\n"
        
        body_text += f"""
Delivery Address:
{order_data.get('delivery_address', 'Not specified')}

Expected Delivery: {order_data.get('expected_delivery', 'TBD')}

You can track your order at: {order_data.get('tracking_url', 'N/A')}

Thank you for choosing FoodXchange!
"""
        
        # HTML version
        body_html = self._render_order_confirmation_html(order_data)
        
        return await self.send_email(to_email, subject, body_text, body_html)
    
    async def send_rfq_notification(
        self,
        to_email: str,
        rfq_data: Dict
    ) -> bool:
        """Send RFQ notification to suppliers"""
        subject = f"New RFQ: {rfq_data['product_name']}"
        
        body_text = f"""
New Request for Quote

A buyer is looking for {rfq_data['product_name']}.

RFQ Details:
- Product: {rfq_data['product_name']}
- Quantity: {rfq_data['quantity']}
- Delivery Date: {rfq_data.get('delivery_date', 'ASAP')}
- Location: {rfq_data.get('location', 'Not specified')}

{rfq_data.get('additional_requirements', '')}

To submit a quote, please visit:
{rfq_data['quote_url']}

This RFQ expires on: {rfq_data.get('expiry_date', 'Not specified')}

Best regards,
FoodXchange Team
"""
        
        body_html = self._render_rfq_notification_html(rfq_data)
        
        return await self.send_email(to_email, subject, body_text, body_html)
    
    async def send_quote_received(
        self,
        to_email: str,
        quote_data: Dict
    ) -> bool:
        """Send notification when quote is received"""
        subject = f"New Quote Received for {quote_data['product_name']}"
        
        body_text = f"""
New Quote Received

A supplier has submitted a quote for your RFQ.

Quote Details:
- Supplier: {quote_data['supplier_name']}
- Product: {quote_data['product_name']}
- Price: ${quote_data['price']:.2f} per {quote_data.get('unit', 'unit')}
- Total: ${quote_data['total_price']:.2f}
- Delivery Time: {quote_data.get('delivery_time', 'Not specified')}

To view and compare all quotes:
{quote_data['comparison_url']}

Best regards,
FoodXchange Team
"""
        
        body_html = self._render_quote_received_html(quote_data)
        
        return await self.send_email(to_email, subject, body_text, body_html)
    
    async def send_password_reset(
        self,
        to_email: str,
        reset_data: Dict
    ) -> bool:
        """Send password reset email"""
        subject = "Password Reset Request - FoodXchange"
        
        body_text = f"""
Password Reset Request

We received a request to reset your password.

To reset your password, click the link below:
{reset_data['reset_url']}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
FoodXchange Security Team
"""
        
        body_html = self._render_password_reset_html(reset_data)
        
        return await self.send_email(to_email, subject, body_text, body_html)
    
    async def send_welcome_email(
        self,
        to_email: str,
        user_data: Dict
    ) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to FoodXchange!"
        
        body_text = f"""
Welcome to FoodXchange!

Hi {user_data.get('name', 'there')},

Thank you for joining FoodXchange, your trusted B2B food marketplace.

Get started by:
1. Completing your company profile
2. Browsing available products
3. Creating your first RFQ

Need help? Visit our help center or contact support.

Best regards,
The FoodXchange Team
"""
        
        body_html = self._render_welcome_email_html(user_data)
        
        return await self.send_email(to_email, subject, body_text, body_html)
    
    def _render_order_confirmation_html(self, data: Dict) -> str:
        """Render HTML template for order confirmation"""
        template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f9f9f9; padding: 20px; margin-top: 20px; }
        .order-details { background-color: white; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        .button { background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Order Confirmation</h1>
            <p>Thank you for your order!</p>
        </div>
        
        <div class="content">
            <div class="order-details">
                <h2>Order #{{ order_number }}</h2>
                <p><strong>Date:</strong> {{ order_date }}</p>
                <p><strong>Total:</strong> ${{ "%.2f"|format(total_amount) }}</p>
                
                <h3>Items Ordered:</h3>
                <table>
                    <tr>
                        <th>Product</th>
                        <th>Quantity</th>
                        <th>Price</th>
                    </tr>
                    {% for item in items %}
                    <tr>
                        <td>{{ item.name }}</td>
                        <td>{{ item.quantity }}</td>
                        <td>${{ "%.2f"|format(item.price) }}</td>
                    </tr>
                    {% endfor %}
                </table>
                
                <p><strong>Delivery Address:</strong><br>{{ delivery_address }}</p>
                <p><strong>Expected Delivery:</strong> {{ expected_delivery }}</p>
                
                {% if tracking_url %}
                <a href="{{ tracking_url }}" class="button">Track Order</a>
                {% endif %}
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 FoodXchange. All rights reserved.</p>
            <p>Questions? Contact us at support@foodxchange.com</p>
        </div>
    </div>
</body>
</html>
"""
        template_obj = Template(template)
        return template_obj.render(**data)
    
    def _render_rfq_notification_html(self, data: Dict) -> str:
        """Render HTML template for RFQ notification"""
        template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #27ae60; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f9f9f9; padding: 20px; margin-top: 20px; }
        .rfq-details { background-color: white; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .button { background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New RFQ Opportunity</h1>
        </div>
        
        <div class="content">
            <p>A buyer is looking for <strong>{{ product_name }}</strong></p>
            
            <div class="rfq-details">
                <h3>RFQ Details:</h3>
                <p><strong>Product:</strong> {{ product_name }}</p>
                <p><strong>Quantity:</strong> {{ quantity }}</p>
                <p><strong>Delivery Date:</strong> {{ delivery_date }}</p>
                <p><strong>Location:</strong> {{ location }}</p>
                
                {% if additional_requirements %}
                <p><strong>Additional Requirements:</strong><br>{{ additional_requirements }}</p>
                {% endif %}
                
                <p><strong>Expires:</strong> {{ expiry_date }}</p>
                
                <center>
                    <a href="{{ quote_url }}" class="button">Submit Quote</a>
                </center>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 FoodXchange. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        template_obj = Template(template)
        return template_obj.render(**data)
    
    def _render_quote_received_html(self, data: Dict) -> str:
        """Render HTML template for quote received notification"""
        template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #3498db; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f9f9f9; padding: 20px; margin-top: 20px; }
        .quote-details { background-color: white; padding: 15px; border-radius: 5px; margin-top: 20px; }
        .highlight { background-color: #e8f4f8; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .button { background-color: #27ae60; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Quote Received</h1>
        </div>
        
        <div class="content">
            <p>You've received a new quote for <strong>{{ product_name }}</strong></p>
            
            <div class="quote-details">
                <h3>Quote Details:</h3>
                <p><strong>Supplier:</strong> {{ supplier_name }}</p>
                <p><strong>Product:</strong> {{ product_name }}</p>
                
                <div class="highlight">
                    <p><strong>Unit Price:</strong> ${{ "%.2f"|format(price) }} per {{ unit }}</p>
                    <p><strong>Total Price:</strong> ${{ "%.2f"|format(total_price) }}</p>
                </div>
                
                <p><strong>Delivery Time:</strong> {{ delivery_time }}</p>
                
                <center>
                    <a href="{{ comparison_url }}" class="button">Compare All Quotes</a>
                </center>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 FoodXchange. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        template_obj = Template(template)
        return template_obj.render(**data)
    
    def _render_password_reset_html(self, data: Dict) -> str:
        """Render HTML template for password reset"""
        template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #e74c3c; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f9f9f9; padding: 20px; margin-top: 20px; }
        .button { background-color: #e74c3c; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>
        
        <div class="content">
            <p>We received a request to reset your password.</p>
            
            <p>To reset your password, click the button below:</p>
            
            <center>
                <a href="{{ reset_url }}" class="button">Reset Password</a>
            </center>
            
            <p><small>This link will expire in 1 hour.</small></p>
            
            <p>If you didn't request this password reset, please ignore this email. Your password won't be changed.</p>
        </div>
        
        <div class="footer">
            <p>© 2025 FoodXchange Security Team</p>
        </div>
    </div>
</body>
</html>
"""
        template_obj = Template(template)
        return template_obj.render(**data)
    
    def _render_welcome_email_html(self, data: Dict) -> str:
        """Render HTML template for welcome email"""
        template = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #2c3e50; color: white; padding: 30px; text-align: center; }
        .content { background-color: #f9f9f9; padding: 30px; margin-top: 20px; }
        .steps { background-color: white; padding: 20px; border-radius: 5px; margin-top: 20px; }
        .step { margin: 15px 0; padding-left: 20px; }
        .button { background-color: #3498db; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 20px; }
        .footer { text-align: center; margin-top: 30px; color: #666; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to FoodXchange!</h1>
        </div>
        
        <div class="content">
            <p>Hi {{ name }},</p>
            
            <p>Thank you for joining FoodXchange, your trusted B2B food marketplace.</p>
            
            <div class="steps">
                <h3>Get Started in 3 Easy Steps:</h3>
                <div class="step">✅ Complete your company profile</div>
                <div class="step">🔍 Browse available products</div>
                <div class="step">📝 Create your first RFQ</div>
            </div>
            
            <center>
                <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
            </center>
            
            <p>Need help? Our support team is here for you!</p>
        </div>
        
        <div class="footer">
            <p>© 2025 FoodXchange. All rights reserved.</p>
            <p>Questions? Contact us at support@foodxchange.com</p>
        </div>
    </div>
</body>
</html>
"""
        template_obj = Template(template)
        return template_obj.render(**data)


# Singleton instance
email_notification_service = EmailNotificationService()