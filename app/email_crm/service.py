"""
Lean Email CRM Service for FoodXchange
Using Azure PostgreSQL, Azure OpenAI, FastAPI
Optimized for Microsoft Founders Hub
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from app.email_crm.tracker import EmailTracker
from app.core.events import bus, Events
import hashlib
import time
import json

class EmailCRMService:
    """Complete email CRM service - lean and simple"""
    
    def __init__(self):
        # Azure PostgreSQL from env
        self.db_url = os.getenv('DATABASE_URL')
        
        # Azure OpenAI configuration (older library for compatibility)
        openai.api_type = 'azure'
        openai.api_key = os.getenv('AZURE_OPENAI_KEY')
        openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
        openai.api_version = '2023-05-15'
        
        self.ai_model = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')
        self.max_tokens = int(os.getenv('AZURE_OPENAI_MAX_TOKENS', '500'))
        self.temperature = float(os.getenv('AZURE_OPENAI_TEMPERATURE', '0.7'))
        
        # Email tracker
        self.tracker = EmailTracker(self.db_url)
        
        # SMTP settings
        self.smtp_server = os.getenv('SMTP_SERVER', '')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USERNAME', '')
        self.smtp_pass = os.getenv('SMTP_PASSWORD', '')
        
        # Caching
        self.cache_enabled = os.getenv('ENABLE_AI_CACHE', 'true').lower() == 'true'
        self.cache_ttl = int(os.getenv('AI_CACHE_TTL', '3600'))
        self._cache = {}
        
        # Cost tracking imports
        try:
            from services.cost_tracker import get_cost_tracker
            from services.azure_monitoring import get_monitoring_service
            self.cost_tracker = get_cost_tracker()
            self.monitoring = get_monitoring_service()
        except:
            self.cost_tracker = None
            self.monitoring = None
    
    def _get_cache_key(self, supplier: Dict, template_type: str) -> str:
        """Generate cache key for AI responses"""
        data = f"{supplier.get('name')}_{supplier.get('country')}_{template_type}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def generate_email(self, supplier: Dict, template_type: str = 'inquiry') -> str:
        """Generate email with Azure OpenAI - optimized with caching"""
        
        # Check cache first
        if self.cache_enabled:
            cache_key = self._get_cache_key(supplier, template_type)
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if time.time() - entry['timestamp'] < self.cache_ttl:
                    print(f"Cache hit for {supplier['name']}")
                    return entry['content']
        
        # Optimized prompts
        prompts = {
            'inquiry': f"""Write a brief, professional email to {supplier['name']} in {supplier['country']}.
We want to source: {supplier.get('products', 'food products')}
Keep under 100 words. Be friendly and clear.""",
            
            'follow_up': f"""Write a short follow-up to {supplier['name']}.
Reference our previous email about {supplier.get('products', 'products')}.
Keep under 100 words."""
        }
        
        try:
            response = self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": "Write concise business emails"},
                    {"role": "user", "content": prompts.get(template_type, prompts['inquiry'])}
                ],
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except:
            return f"Hi {supplier['name']},\n\nWe're interested in your products. Please share pricing and MOQ.\n\nBest,\nFDX Trading"
    
    def send_bulk_emails(self, supplier_ids: List[int], campaign_name: str = "Bulk Send") -> Dict:
        """Send emails to multiple suppliers"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get suppliers
        cur.execute("""
            SELECT id, supplier_name as name, company_email as email, 
                   country, products 
            FROM suppliers 
            WHERE id = ANY(%s) AND company_email IS NOT NULL
        """, (supplier_ids,))
        
        suppliers = cur.fetchall()
        sent = 0
        failed = []
        
        for supplier in suppliers:
            try:
                # Generate content
                content = self.generate_email(supplier)
                
                # Create tracking ID
                tracking_id = self.tracker.create_tracking_id()
                
                # Add tracking
                tracked_content = self.tracker.add_tracking(content, tracking_id)
                
                # Send email (or simulate)
                if self.smtp_server and self.smtp_user:
                    self._send_smtp(supplier['email'], "Partnership Opportunity - FDX Trading", tracked_content)
                
                # Log to database
                cur.execute("""
                    INSERT INTO email_log 
                    (supplier_id, supplier_email, supplier_name, email_content, 
                     tracking_id, campaign_name, sent_at)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (supplier['id'], supplier['email'], supplier['name'], 
                      content, tracking_id, campaign_name))
                
                sent += 1
                
                # Emit event
                bus.emit(Events.EMAIL_SENT, {
                    'supplier_id': supplier['id'],
                    'email': supplier['email'],
                    'tracking_id': tracking_id
                })
                
            except Exception as e:
                failed.append({'email': supplier['email'], 'error': str(e)})
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {'sent': sent, 'failed': len(failed), 'errors': failed}
    
    def analyze_response(self, email_text: str, from_email: str) -> Dict:
        """Analyze email response with AI"""
        
        prompt = f"""Analyze this supplier email response.
Email: {email_text}

Return JSON only:
{{"interested": true/false, "action": "quote|call|info|ignore", "summary": "1 line"}}"""
        
        try:
            response = self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": "Return only JSON"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Save to database
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO email_responses 
                (from_email, body, ai_analysis, interested, next_action, received_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                RETURNING id
            """, (from_email, email_text, json.dumps(result), 
                  result.get('interested', False), result.get('action', 'ignore')))
            
            response_id = cur.fetchone()[0]
            
            # Create task if needed
            if result.get('action') != 'ignore':
                cur.execute("""
                    INSERT INTO tasks 
                    (email_response_id, title, priority, due_date, status)
                    VALUES (%s, %s, %s, NOW() + INTERVAL '2 days', 'pending')
                """, (response_id, f"Follow up: {result.get('summary', 'Review response')}", 
                      'high' if result.get('interested') else 'medium'))
                
                bus.emit(Events.TASK_CREATED, {'response_id': response_id})
            
            conn.commit()
            cur.close()
            conn.close()
            
            bus.emit(Events.RESPONSE_RECEIVED, {
                'from': from_email,
                'interested': result.get('interested', False)
            })
            
            return result
            
        except Exception as e:
            return {'interested': False, 'action': 'ignore', 'summary': 'Error analyzing'}
    
    def get_email_stats(self, days: int = 7) -> Dict:
        """Get simple email statistics"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                COUNT(*) as sent,
                COUNT(CASE WHEN opened_at IS NOT NULL THEN 1 END) as opened,
                COUNT(CASE WHEN clicked_at IS NOT NULL THEN 1 END) as clicked
            FROM email_log
            WHERE sent_at >= NOW() - INTERVAL '%s days'
        """, (days,))
        
        stats = cur.fetchone()
        
        # Calculate rates
        if stats['sent'] > 0:
            stats['open_rate'] = round((stats['opened'] / stats['sent']) * 100, 1)
            stats['click_rate'] = round((stats['clicked'] / stats['sent']) * 100, 1)
        else:
            stats['open_rate'] = 0
            stats['click_rate'] = 0
        
        cur.close()
        conn.close()
        
        return stats
    
    def _send_smtp(self, to_email: str, subject: str, html_content: str):
        """Actually send email via SMTP"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"FDX Trading <{self.smtp_user}>"
        msg['To'] = to_email
        
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.smtp_user, self.smtp_pass)
            server.send_message(msg)

# Global instance
email_crm = EmailCRMService()