"""
Email Service for IMAP/Exchange Integration
Handles email fetching and sending for the FoodXchange platform
"""
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import asyncio
from dataclasses import dataclass

from foodxchange.config import get_settings
from foodxchange.database import get_db
from foodxchange.models.email import Email as EmailModel

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Email message data structure"""
    uid: str
    sender: str
    recipient: str
    subject: str
    body: str
    body_html: Optional[str] = None
    received_date: Optional[datetime] = None
    attachments: List[Dict[str, Any]] = None
    headers: Dict[str, str] = None
    
    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.headers is None:
            self.headers = {}


class EmailService:
    """Service for handling email operations"""
    
    def __init__(self):
        self.imap_server = settings.email_imap_server
        self.imap_port = settings.email_imap_port
        self.smtp_server = settings.email_smtp_server
        self.smtp_port = settings.email_smtp_port
        self.email_address = settings.email_address
        self.email_password = settings.email_password
        self.use_ssl = True
        
    async def fetch_unread_emails(self, folder: str = "INBOX", limit: int = 50) -> List[EmailMessage]:
        """Fetch unread emails from the specified folder"""
        emails = []
        
        try:
            # Connect to IMAP server
            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                mail = imaplib.IMAP4(self.imap_server, self.imap_port)
                
            mail.login(self.email_address, self.email_password)
            mail.select(folder)
            
            # Search for unread emails
            status, data = mail.search(None, 'UNSEEN')
            if status != 'OK':
                logger.error("Failed to search emails")
                return emails
                
            email_ids = data[0].split()
            
            # Limit the number of emails to fetch
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            for email_id in email_ids:
                try:
                    email_msg = await self._fetch_single_email(mail, email_id)
                    if email_msg:
                        emails.append(email_msg)
                except Exception as e:
                    logger.error(f"Error fetching email {email_id}: {str(e)}")
                    
            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"Email fetch error: {str(e)}")
            
        return emails
        
    async def _fetch_single_email(self, mail_connection, email_id: bytes) -> Optional[EmailMessage]:
        """Fetch a single email by ID"""
        try:
            # Fetch email data
            status, data = mail_connection.fetch(email_id, '(RFC822)')
            if status != 'OK':
                return None
                
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)
            
            # Extract email components
            sender = self._extract_email_address(msg['From'])
            recipient = self._extract_email_address(msg['To'])
            subject = msg['Subject'] or "No Subject"
            
            # Extract body
            body, body_html = self._extract_body(msg)
            
            # Parse date
            received_date = None
            if msg['Date']:
                try:
                    received_date = email.utils.parsedate_to_datetime(msg['Date'])
                except:
                    pass
                    
            # Extract attachments
            attachments = self._extract_attachments(msg)
            
            # Get headers
            headers = {key: value for key, value in msg.items()}
            
            return EmailMessage(
                uid=email_id.decode(),
                sender=sender,
                recipient=recipient,
                subject=subject,
                body=body,
                body_html=body_html,
                received_date=received_date,
                attachments=attachments,
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Error parsing email: {str(e)}")
            return None
            
    def _extract_email_address(self, email_str: str) -> str:
        """Extract email address from a string like 'Name <email@example.com>'"""
        if '<' in email_str and '>' in email_str:
            return email_str.split('<')[1].split('>')[0]
        return email_str
        
    def _extract_body(self, msg) -> tuple[str, Optional[str]]:
        """Extract plain text and HTML body from email"""
        body = ""
        body_html = None
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body = str(part.get_payload())
                        
                elif content_type == "text/html":
                    try:
                        body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body_html = str(part.get_payload())
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
                
        return body, body_html
        
    def _extract_attachments(self, msg) -> List[Dict[str, Any]]:
        """Extract attachment information from email"""
        attachments = []
        
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        attachments.append({
                            'filename': filename,
                            'content_type': part.get_content_type(),
                            'size': len(part.get_payload())
                        })
                        
        return attachments
        
    async def send_email(self, to: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send an email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_address
            msg['To'] = to
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
                
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
                
            logger.info(f"Email sent successfully to {to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
            
    async def mark_as_read(self, email_uids: List[str]) -> bool:
        """Mark emails as read"""
        try:
            if self.use_ssl:
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                mail = imaplib.IMAP4(self.imap_server, self.imap_port)
                
            mail.login(self.email_address, self.email_password)
            mail.select('INBOX')
            
            for uid in email_uids:
                mail.store(uid.encode(), '+FLAGS', '\\Seen')
                
            mail.close()
            mail.logout()
            return True
            
        except Exception as e:
            logger.error(f"Failed to mark emails as read: {str(e)}")
            return False
            
    async def save_to_database(self, email_msg: EmailMessage, email_type: str = "supplier") -> Optional[EmailModel]:
        """Save email to database"""
        try:
            db = next(get_db())
            
            db_email = EmailModel(
                sender_email=email_msg.sender,
                recipient_email=email_msg.recipient,
                subject=email_msg.subject,
                body=email_msg.body,
                body_html=email_msg.body_html,
                received_at=email_msg.received_date or datetime.utcnow(),
                email_type=email_type,
                processed=False,
                metadata={
                    "uid": email_msg.uid,
                    "attachments": email_msg.attachments,
                    "headers": email_msg.headers
                }
            )
            
            db.add(db_email)
            db.commit()
            db.refresh(db_email)
            
            return db_email
            
        except Exception as e:
            logger.error(f"Failed to save email to database: {str(e)}")
            if db:
                db.rollback()
            return None
        finally:
            if db:
                db.close()


# Exchange/Office 365 specific implementation
class ExchangeEmailService(EmailService):
    """Exchange/Office 365 specific email service"""
    
    def __init__(self):
        super().__init__()
        # Exchange specific configuration
        self.use_oauth = settings.email_use_oauth
        self.tenant_id = settings.azure_tenant_id
        self.client_id = settings.azure_client_id
        self.client_secret = settings.azure_client_secret
        
    async def authenticate_oauth(self):
        """Authenticate using OAuth2 for Office 365"""
        # Implementation would use MSAL or similar library
        # This is a placeholder for the OAuth flow
        pass
        
    async def fetch_unread_emails(self, folder: str = "INBOX", limit: int = 50) -> List[EmailMessage]:
        """Fetch emails using Exchange Web Services or Graph API"""
        # This would use Microsoft Graph API or EWS
        # For now, fallback to parent implementation
        return await super().fetch_unread_emails(folder, limit)


# Factory function to get appropriate email service
def get_email_service() -> EmailService:
    """Get appropriate email service based on configuration"""
    if settings.email_provider == "exchange":
        return ExchangeEmailService()
    else:
        return EmailService()


# Async email fetcher for the agent
async def fetch_supplier_emails(limit: int = 50) -> List[EmailModel]:
    """Fetch and save supplier emails to database"""
    email_service = get_email_service()
    
    # Fetch unread emails
    email_messages = await email_service.fetch_unread_emails(limit=limit)
    
    saved_emails = []
    for email_msg in email_messages:
        # Filter supplier emails (simple check - can be enhanced)
        if is_supplier_email(email_msg):
            db_email = await email_service.save_to_database(email_msg, "supplier")
            if db_email:
                saved_emails.append(db_email)
                
    # Mark emails as read
    if saved_emails:
        uids = [msg.uid for msg in email_messages]
        await email_service.mark_as_read(uids)
        
    return saved_emails


def is_supplier_email(email_msg: EmailMessage) -> bool:
    """Determine if an email is from a supplier"""
    # Simple heuristic - can be enhanced with ML
    supplier_keywords = ['quote', 'pricing', 'availability', 'supplier', 'vendor', 'wholesale']
    
    subject_lower = email_msg.subject.lower()
    body_lower = email_msg.body.lower()[:500]  # Check first 500 chars
    
    for keyword in supplier_keywords:
        if keyword in subject_lower or keyword in body_lower:
            return True
            
    # Check if sender is in supplier database
    # This would require a database lookup
    
    return False