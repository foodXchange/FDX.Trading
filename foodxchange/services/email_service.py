"""
Azure Email Service for sending product briefs
Uses Azure Communication Services Email
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from azure.communication.email import EmailClient
from azure.core.exceptions import AzureError
import base64

logger = logging.getLogger(__name__)

class AzureEmailService:
    """Service for sending emails via Azure Communication Services"""
    
    def __init__(self):
        # Get Azure Email configuration from environment
        self.connection_string = os.getenv('AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING')
        self.sender_address = os.getenv('AZURE_EMAIL_SENDER_ADDRESS', 'DoNotReply@foodxchange.com')
        
        if self.connection_string:
            try:
                self.email_client = EmailClient.from_connection_string(self.connection_string)
                logger.info("Azure Email Service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Email Service: {e}")
                self.email_client = None
        else:
            logger.warning("Azure Email connection string not found in environment variables")
            self.email_client = None
    
    async def send_product_brief(
        self,
        recipient_emails: List[str],
        subject: str,
        body_html: str,
        body_text: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send product brief email with attachments
        
        Args:
            recipient_emails: List of recipient email addresses
            subject: Email subject
            body_html: HTML content of the email
            body_text: Plain text content of the email
            attachments: List of attachments with format:
                [{
                    'name': 'filename.docx',
                    'content': bytes_content,
                    'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                }]
            cc_emails: List of CC recipients
            bcc_emails: List of BCC recipients
            
        Returns:
            Dict with send result
        """
        
        if not self.email_client:
            logger.error("Email client not initialized")
            return {
                'success': False,
                'error': 'Email service not configured'
            }
        
        try:
            # Prepare email message
            message = {
                "senderAddress": self.sender_address,
                "recipients": {
                    "to": [{"address": email} for email in recipient_emails]
                },
                "content": {
                    "subject": subject,
                    "plainText": body_text,
                    "html": body_html
                }
            }
            
            # Add CC recipients if provided
            if cc_emails:
                message["recipients"]["cc"] = [{"address": email} for email in cc_emails]
            
            # Add BCC recipients if provided
            if bcc_emails:
                message["recipients"]["bcc"] = [{"address": email} for email in bcc_emails]
            
            # Add attachments if provided
            if attachments:
                message["attachments"] = []
                for attachment in attachments:
                    # Convert bytes to base64
                    content_base64 = base64.b64encode(attachment['content']).decode('utf-8')
                    
                    message["attachments"].append({
                        "name": attachment['name'],
                        "contentType": attachment.get('content_type', 'application/octet-stream'),
                        "contentInBase64": content_base64
                    })
            
            # Send email
            poller = self.email_client.begin_send(message)
            result = poller.result()
            
            logger.info(f"Email sent successfully to {recipient_emails}")
            
            return {
                'success': True,
                'message_id': result.id if hasattr(result, 'id') else None,
                'status': 'sent'
            }
            
        except AzureError as e:
            logger.error(f"Azure error sending email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_product_brief_email_html(
        self,
        recipient_name: str,
        product_name: str,
        brief_summary: str,
        sender_name: str = "FoodXchange Team"
    ) -> str:
        """Create HTML email template for product brief"""
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f8f9fa;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666;
                    font-size: 12px;
                }}
                .product-info {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>FoodXchange Product Brief</h1>
            </div>
            
            <div class="content">
                <p>Dear {recipient_name},</p>
                
                <p>Please find attached the product brief for <strong>{product_name}</strong> as requested.</p>
                
                <div class="product-info">
                    <h3>Brief Summary:</h3>
                    <p>{brief_summary}</p>
                </div>
                
                <p>The attached document contains:</p>
                <ul>
                    <li>Complete product specifications</li>
                    <li>Packaging and weight details</li>
                    <li>Certifications and compliance information</li>
                    <li>Storage and shelf life requirements</li>
                    <li>Related products information</li>
                    <li>Sourcing requirements</li>
                </ul>
                
                <p>Please review the attached brief and let us know if you need any additional information or have specific requirements.</p>
                
                <p>Best regards,<br>
                {sender_name}<br>
                FoodXchange AI-Powered Sourcing Platform</p>
            </div>
            
            <div class="footer">
                <p>This email was sent from FoodXchange - AI-Powered B2B Food Sourcing Platform</p>
                <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def create_product_brief_email_text(
        self,
        recipient_name: str,
        product_name: str,
        brief_summary: str,
        sender_name: str = "FoodXchange Team"
    ) -> str:
        """Create plain text email for product brief"""
        
        text_template = f"""
Dear {recipient_name},

Please find attached the product brief for {product_name} as requested.

Brief Summary:
{brief_summary}

The attached document contains:
- Complete product specifications
- Packaging and weight details
- Certifications and compliance information
- Storage and shelf life requirements
- Related products information
- Sourcing requirements

Please review the attached brief and let us know if you need any additional information or have specific requirements.

Best regards,
{sender_name}
FoodXchange AI-Powered Sourcing Platform

---
This email was sent from FoodXchange - AI-Powered B2B Food Sourcing Platform
Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
        """
        
        return text_template.strip()
    



# Singleton instance - lazy initialization
_azure_email_service = None

def get_azure_email_service():
    """Get or create the Azure Email Service instance"""
    global _azure_email_service
    if _azure_email_service is None:
        _azure_email_service = AzureEmailService()
    return _azure_email_service

# For backward compatibility
azure_email_service = get_azure_email_service()