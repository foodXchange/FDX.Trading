#!/usr/bin/env python3
"""
Integrated Email Service for FoodXchange
Combines AI writing, tracking, and response management
"""

import os
import json
import uuid
import smtplib
import imaplib
import email as email_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class EmailService:
    """Complete email service with AI, tracking, and analytics"""
    
    def __init__(self):
        # Database connection
        self.db_url = os.getenv('DATABASE_URL')
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', 'noreply@fdx.trading')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        
        # IMAP configuration for reading responses
        self.imap_server = os.getenv('IMAP_SERVER', 'imap.gmail.com')
        self.imap_port = int(os.getenv('IMAP_PORT', '993'))
        
        # Azure OpenAI
        self.ai_client = OpenAI(
            api_key=os.getenv('AZURE_OPENAI_KEY'),
            base_url=f"{os.getenv('AZURE_OPENAI_ENDPOINT')}openai/deployments/{os.getenv('AZURE_OPENAI_DEPLOYMENT')}/",
            api_version="2024-02-15-preview"
        )
        
        # Application URL for tracking
        self.app_url = os.getenv('APP_URL', 'https://fdx.trading')
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def generate_tracking_id(self):
        """Generate unique tracking ID"""
        return str(uuid.uuid4())
    
    def create_campaign(self, name: str, subject: str, template: str, 
                       template_type: str = 'custom') -> int:
        """Create new email campaign"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO email_campaigns 
                (name, subject, template_body, template_type, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING id
            """, (name, subject, template, template_type))
            
            campaign_id = cur.fetchone()[0]
            conn.commit()
            return campaign_id
            
        finally:
            cur.close()
            conn.close()
    
    def generate_ai_email(self, template_type: str, recipient_name: str, 
                         company_name: str, product_details: str = '', 
                         custom_notes: str = '') -> Dict:
        """Generate AI-powered email content"""
        
        templates = {
            'inquiry': f"""Write a professional business inquiry email for FDX.trading.
Recipient: {recipient_name} at {company_name}
Product Interest: {product_details or 'food products'}
Notes: {custom_notes}

Create a compelling email that:
1. Introduces FDX.trading as a premium B2B food trading platform
2. Shows genuine interest in their specific products
3. Requests pricing, MOQ, and certifications
4. Suggests concrete next steps
5. Maintains professional yet personable tone""",
            
            'follow_up': f"""Write a follow-up email for FDX.trading.
Recipient: {recipient_name} at {company_name}
Context: {custom_notes or 'Previous inquiry about products'}

Create a polite follow-up that:
1. References our previous communication
2. Reiterates specific interest
3. Offers to address any concerns
4. Provides clear value proposition
5. Includes gentle call-to-action""",
            
            'response_to_interest': f"""Write a response to an interested supplier.
Recipient: {recipient_name} at {company_name}
Their Interest: {custom_notes}

Create an engaging response that:
1. Thanks them for their interest
2. Addresses their specific points
3. Provides next steps for partnership
4. Builds excitement about collaboration
5. Includes specific action items"""
        }
        
        prompt = templates.get(template_type, templates['inquiry'])
        
        try:
            response = self.ai_client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are a professional B2B email writer for FDX.trading. Write compelling, concise business emails."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            return {
                'content': response.choices[0].message.content.strip(),
                'template_type': template_type,
                'generated': True
            }
            
        except Exception as e:
            # Fallback template
            return {
                'content': f"""Dear {recipient_name},

I hope this message finds you well. I'm reaching out from FDX.trading regarding potential partnership opportunities.

We're interested in learning more about your products and exploring how we might work together.

Best regards,
FDX.trading Team""",
                'template_type': template_type,
                'generated': False,
                'error': str(e)
            }
    
    def send_bulk_emails(self, campaign_id: int, suppliers: List[Dict], 
                        user_email: str = 'partnerships@fdx.trading') -> Dict:
        """Send emails to multiple suppliers with tracking"""
        
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get campaign details
        cur.execute("SELECT * FROM email_campaigns WHERE id = %s", (campaign_id,))
        campaign = cur.fetchone()
        
        if not campaign:
            return {'success': False, 'error': 'Campaign not found'}
        
        sent_count = 0
        failed = []
        
        for supplier in suppliers:
            try:
                # Generate tracking ID
                tracking_id = self.generate_tracking_id()
                
                # Personalize content
                if campaign['template_type'] == 'ai_generated':
                    ai_content = self.generate_ai_email(
                        'inquiry',
                        supplier.get('contact_person', supplier['name']),
                        supplier['name'],
                        supplier.get('products', ''),
                        supplier.get('notes', '')
                    )
                    email_body = ai_content['content']
                else:
                    # Use template with variable replacement
                    email_body = campaign['template_body'].format(
                        supplier_name=supplier['name'],
                        contact_person=supplier.get('contact_person', 'Team'),
                        company_name=supplier['name'],
                        country=supplier.get('country', 'your region'),
                        tracking_id=tracking_id
                    )
                
                # Add tracking pixel
                tracking_pixel = f'<img src="{self.app_url}/api/email/track/{tracking_id}/pixel.png" width="1" height="1" />'
                
                # Add tracking links
                email_body = email_body.replace(
                    'partnerships@fdx.trading',
                    f'<a href="{self.app_url}/api/email/track/{tracking_id}/click?url=mailto:partnerships@fdx.trading">partnerships@fdx.trading</a>'
                )
                
                # Create email message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = campaign['subject']
                msg['From'] = f"FDX.trading <{self.smtp_username}>"
                msg['To'] = supplier['email']
                msg['Reply-To'] = user_email
                
                # Add unique message ID for tracking responses
                msg['Message-ID'] = f"<{tracking_id}@fdx.trading>"
                
                # Create HTML version with tracking
                html_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                {email_body.replace(chr(10), '<br>')}
                {tracking_pixel}
                </body>
                </html>
                """
                
                msg.attach(MIMEText(email_body, 'plain'))
                msg.attach(MIMEText(html_body, 'html'))
                
                # Send email
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    if self.smtp_password:
                        server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
                
                # Log sent email
                cur.execute("""
                    INSERT INTO sent_emails 
                    (campaign_id, supplier_id, supplier_email, tracking_id, 
                     sent_at, subject, content, status)
                    VALUES (%s, %s, %s, %s, NOW(), %s, %s, 'sent')
                    RETURNING id
                """, (
                    campaign_id, supplier['id'], supplier['email'], 
                    tracking_id, campaign['subject'], email_body
                ))
                
                sent_count += 1
                
            except Exception as e:
                failed.append({'email': supplier['email'], 'error': str(e)})
                
                # Log failed attempt
                cur.execute("""
                    INSERT INTO sent_emails 
                    (campaign_id, supplier_id, supplier_email, tracking_id, 
                     sent_at, subject, content, status, error_message)
                    VALUES (%s, %s, %s, %s, NOW(), %s, %s, 'failed', %s)
                """, (
                    campaign_id, supplier['id'], supplier['email'], 
                    tracking_id, campaign['subject'], '', str(e)
                ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'success': True,
            'sent_count': sent_count,
            'failed_count': len(failed),
            'failed': failed
        }
    
    def track_email_open(self, tracking_id: str):
        """Track when email is opened"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                UPDATE sent_emails 
                SET opened_at = COALESCE(opened_at, NOW()),
                    open_count = COALESCE(open_count, 0) + 1,
                    last_opened_at = NOW()
                WHERE tracking_id = %s
            """, (tracking_id,))
            
            conn.commit()
        finally:
            cur.close()
            conn.close()
    
    def track_email_click(self, tracking_id: str, url: str):
        """Track when link in email is clicked"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                UPDATE sent_emails 
                SET clicked_at = COALESCE(clicked_at, NOW()),
                    click_count = COALESCE(click_count, 0) + 1,
                    last_clicked_at = NOW()
                WHERE tracking_id = %s
            """, (tracking_id,))
            
            # Log specific click
            cur.execute("""
                INSERT INTO email_clicks 
                (sent_email_id, tracking_id, url, clicked_at)
                SELECT id, %s, %s, NOW() 
                FROM sent_emails WHERE tracking_id = %s
            """, (tracking_id, url, tracking_id))
            
            conn.commit()
        finally:
            cur.close()
            conn.close()
    
    def check_email_responses(self) -> List[Dict]:
        """Check IMAP for email responses"""
        if not self.smtp_password:
            return []
        
        responses = []
        
        try:
            # Connect to IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.smtp_username, self.smtp_password)
            mail.select('INBOX')
            
            # Search for unread emails
            _, data = mail.search(None, 'UNSEEN')
            
            for num in data[0].split():
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                msg = email_lib.message_from_bytes(email_body)
                
                # Extract details
                from_email = msg.get('From', '')
                subject = msg.get('Subject', '')
                in_reply_to = msg.get('In-Reply-To', '')
                
                # Extract body
                body = ''
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                
                # Try to match to sent email
                tracking_id = None
                if in_reply_to:
                    # Extract tracking ID from Message-ID
                    tracking_id = in_reply_to.strip('<>').split('@')[0]
                
                responses.append({
                    'from': from_email,
                    'subject': subject,
                    'body': body,
                    'tracking_id': tracking_id,
                    'received_at': datetime.now()
                })
                
                # Mark as read
                mail.store(num, '+FLAGS', '\\Seen')
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            print(f"Error checking emails: {e}")
        
        return responses
    
    def process_email_response(self, response: Dict) -> Dict:
        """Process and analyze email response with AI"""
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Find original sent email
            sent_email = None
            if response.get('tracking_id'):
                cur.execute("""
                    SELECT se.*, s.supplier_name, s.company_name 
                    FROM sent_emails se
                    JOIN suppliers s ON se.supplier_id = s.id
                    WHERE se.tracking_id = %s
                """, (response['tracking_id'],))
                sent_email = cur.fetchone()
            
            # AI analysis
            ai_analysis = self.analyze_email_with_ai(
                response['body'],
                sent_email['supplier_name'] if sent_email else None
            )
            
            # Store response
            cur.execute("""
                INSERT INTO email_responses 
                (sent_email_id, from_email, subject, body, received_at,
                 ai_summary, ai_category, interest_level, priority_score,
                 next_action, follow_up_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                sent_email['id'] if sent_email else None,
                response['from'],
                response['subject'],
                response['body'],
                response['received_at'],
                ai_analysis['summary'],
                ai_analysis['category'],
                ai_analysis['interest_level'],
                ai_analysis['priority_score'],
                ai_analysis['next_action'],
                ai_analysis.get('follow_up_date')
            ))
            
            response_id = cur.fetchone()['id']
            
            # Create tasks based on AI analysis
            if ai_analysis['next_action'] != 'no_action':
                self.create_task_from_response(
                    response_id,
                    sent_email['supplier_id'] if sent_email else None,
                    ai_analysis
                )
            
            conn.commit()
            
            return {
                'success': True,
                'response_id': response_id,
                'analysis': ai_analysis
            }
            
        finally:
            cur.close()
            conn.close()
    
    def analyze_email_with_ai(self, email_body: str, supplier_name: str = None) -> Dict:
        """Analyze email content with AI"""
        prompt = f"""
Analyze this supplier email response and extract key information.
Supplier: {supplier_name or 'Unknown'}

Email Content:
{email_body}

Return a JSON object with:
{{
    "interest_level": "high|medium|low|none",
    "priority_score": 0-100,
    "category": "interested|needs_info|not_interested|pricing_provided|sample_offered",
    "summary": "2-3 sentence summary",
    "key_points": ["point1", "point2"],
    "next_action": "send_quote|schedule_call|send_info|follow_up|no_action",
    "follow_up_date": "YYYY-MM-DD or null",
    "sentiment": "positive|neutral|negative"
}}
"""
        
        try:
            response = self.ai_client.chat.completions.create(
                model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing B2B email responses. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            # Fallback analysis
            return {
                "interest_level": "medium",
                "priority_score": 50,
                "category": "needs_review",
                "summary": "Email requires manual review",
                "key_points": ["Failed to analyze automatically"],
                "next_action": "follow_up",
                "follow_up_date": None,
                "sentiment": "neutral",
                "error": str(e)
            }
    
    def create_task_from_response(self, response_id: int, supplier_id: int, 
                                 ai_analysis: Dict):
        """Create task based on AI analysis"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            task_mapping = {
                'send_quote': {
                    'title': 'Send price quotation',
                    'priority': 'high',
                    'due_days': 1
                },
                'schedule_call': {
                    'title': 'Schedule call with supplier',
                    'priority': 'high',
                    'due_days': 2
                },
                'send_info': {
                    'title': 'Send requested information',
                    'priority': 'medium',
                    'due_days': 1
                },
                'follow_up': {
                    'title': 'Follow up on inquiry',
                    'priority': 'medium',
                    'due_days': 3
                }
            }
            
            task_info = task_mapping.get(ai_analysis['next_action'])
            if task_info:
                due_date = datetime.now() + timedelta(days=task_info['due_days'])
                if ai_analysis.get('follow_up_date'):
                    due_date = datetime.strptime(ai_analysis['follow_up_date'], '%Y-%m-%d')
                
                cur.execute("""
                    INSERT INTO tasks 
                    (supplier_id, email_response_id, title, description, 
                     priority, due_date, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, 'pending', NOW())
                """, (
                    supplier_id,
                    response_id,
                    task_info['title'],
                    ai_analysis['summary'],
                    task_info['priority'],
                    due_date
                ))
                
                conn.commit()
                
        finally:
            cur.close()
            conn.close()
    
    def get_email_analytics(self, days: int = 30) -> Dict:
        """Get email performance analytics"""
        conn = self.get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Overall stats
            cur.execute("""
                SELECT 
                    COUNT(*) as total_sent,
                    COUNT(CASE WHEN opened_at IS NOT NULL THEN 1 END) as total_opened,
                    COUNT(CASE WHEN clicked_at IS NOT NULL THEN 1 END) as total_clicked,
                    COUNT(DISTINCT er.id) as total_responses
                FROM sent_emails se
                LEFT JOIN email_responses er ON se.id = er.sent_email_id
                WHERE se.sent_at >= NOW() - INTERVAL '%s days'
            """, (days,))
            
            overall = cur.fetchone()
            
            # Campaign performance
            cur.execute("""
                SELECT 
                    ec.id, ec.name, ec.subject,
                    COUNT(se.id) as sent_count,
                    COUNT(CASE WHEN se.opened_at IS NOT NULL THEN 1 END) as open_count,
                    COUNT(CASE WHEN se.clicked_at IS NOT NULL THEN 1 END) as click_count,
                    COUNT(DISTINCT er.id) as response_count
                FROM email_campaigns ec
                LEFT JOIN sent_emails se ON ec.id = se.campaign_id
                LEFT JOIN email_responses er ON se.id = er.sent_email_id
                WHERE ec.created_at >= NOW() - INTERVAL '%s days'
                GROUP BY ec.id, ec.name, ec.subject
                ORDER BY ec.created_at DESC
            """, (days,))
            
            campaigns = cur.fetchall()
            
            # Response analysis
            cur.execute("""
                SELECT 
                    interest_level,
                    COUNT(*) as count
                FROM email_responses
                WHERE received_at >= NOW() - INTERVAL '%s days'
                GROUP BY interest_level
            """, (days,))
            
            interest_levels = cur.fetchall()
            
            # Calculate rates
            if overall['total_sent'] > 0:
                overall['open_rate'] = (overall['total_opened'] / overall['total_sent']) * 100
                overall['click_rate'] = (overall['total_clicked'] / overall['total_sent']) * 100
                overall['response_rate'] = (overall['total_responses'] / overall['total_sent']) * 100
            else:
                overall['open_rate'] = 0
                overall['click_rate'] = 0
                overall['response_rate'] = 0
            
            return {
                'overall': overall,
                'campaigns': campaigns,
                'interest_levels': interest_levels,
                'period_days': days
            }
            
        finally:
            cur.close()
            conn.close()

# Email tracking service singleton
email_service = EmailService()