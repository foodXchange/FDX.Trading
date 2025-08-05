"""
Optimized Email Service for Microsoft Founders Hub
Includes caching, batching, and cost controls
"""

import os
import smtplib
import hashlib
import json
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from functools import lru_cache
import threading
from queue import Queue

class OptimizedEmailService:
    """Email service optimized for Azure credits usage"""
    
    def __init__(self):
        # Azure PostgreSQL
        self.db_url = os.getenv('DATABASE_URL')
        
        # Azure OpenAI configuration (older library)
        openai.api_type = 'azure'
        openai.api_key = os.getenv('AZURE_OPENAI_KEY')
        openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
        openai.api_version = '2023-05-15'
        
        self.ai_model = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')
        self.max_tokens = int(os.getenv('AZURE_OPENAI_MAX_TOKENS', '500'))
        self.temperature = float(os.getenv('AZURE_OPENAI_TEMPERATURE', '0.7'))
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USERNAME')
        self.smtp_pass = os.getenv('SMTP_PASSWORD')
        self.email_from = os.getenv('EMAIL_FROM', 'FDX Trading <noreply@fdx.trading>')
        
        # Caching
        self.cache_enabled = os.getenv('ENABLE_AI_CACHE', 'true').lower() == 'true'
        self.cache_ttl = int(os.getenv('AI_CACHE_TTL', '3600'))
        self._cache = {}
        
        # Batch processing
        self.email_queue = Queue()
        self.batch_size = 10
        self._start_batch_processor()
        
        # Cost tracking
        self.token_usage = {
            'daily': 0,
            'monthly': 0,
            'last_reset': datetime.now()
        }
    
    def _get_cache_key(self, supplier: Dict, template_type: str) -> str:
        """Generate cache key for AI responses"""
        data = f"{supplier.get('name')}_{supplier.get('country')}_{template_type}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[str]:
        """Get cached AI response if valid"""
        if not self.cache_enabled:
            return None
            
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if time.time() - entry['timestamp'] < self.cache_ttl:
                return entry['content']
        return None
    
    def _save_to_cache(self, cache_key: str, content: str):
        """Save AI response to cache"""
        if self.cache_enabled:
            self._cache[cache_key] = {
                'content': content,
                'timestamp': time.time()
            }
    
    def generate_email_optimized(self, supplier: Dict, template_type: str = 'inquiry') -> Tuple[str, int]:
        """Generate email with caching and token optimization"""
        
        # Check cache first
        cache_key = self._get_cache_key(supplier, template_type)
        cached_content = self._get_from_cache(cache_key)
        if cached_content:
            return cached_content, 0  # No tokens used
        
        # Optimized prompts
        prompts = {
            'inquiry': f"Write a 100-word email to {supplier['name']} requesting {supplier.get('products', 'products')}. Be professional.",
            'follow_up': f"Write a 50-word follow-up to {supplier['name']}. Be brief.",
            'introduction': f"Write a 75-word intro email to {supplier['name']} about sourcing."
        }
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.ai_model,
                messages=[
                    {"role": "system", "content": "You are a concise business email writer."},
                    {"role": "user", "content": prompts.get(template_type, prompts['inquiry'])}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Update token tracking
            self._track_tokens(tokens_used)
            
            # Cache the response
            self._save_to_cache(cache_key, content)
            
            return content, tokens_used
            
        except Exception as e:
            # Fallback template if AI fails
            fallback = self._get_fallback_template(supplier, template_type)
            return fallback, 0
    
    def _get_fallback_template(self, supplier: Dict, template_type: str) -> str:
        """Fallback templates when AI is unavailable"""
        templates = {
            'inquiry': f"""Dear {supplier.get('name', 'Supplier')},

We are interested in sourcing {supplier.get('products', 'your products')} for our platform.

Could you please provide:
- Product catalog
- Pricing information
- Minimum order quantities

Best regards,
FDX Trading Team""",
            
            'follow_up': f"""Dear {supplier.get('name', 'Supplier')},

Following up on our previous inquiry about {supplier.get('products', 'your products')}.

Looking forward to your response.

Best regards,
FDX Trading Team"""
        }
        
        return templates.get(template_type, templates['inquiry'])
    
    def send_email_smtp(self, to_email: str, subject: str, body: str) -> bool:
        """Send email via SMTP with retry logic"""
        if not all([self.smtp_server, self.smtp_user, self.smtp_pass]):
            print("SMTP not configured - email would be sent to:", to_email)
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect with timeout
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    def queue_email(self, supplier: Dict, template_type: str = 'inquiry'):
        """Add email to batch queue"""
        self.email_queue.put({
            'supplier': supplier,
            'template_type': template_type,
            'timestamp': datetime.now()
        })
    
    def _start_batch_processor(self):
        """Start background thread for batch processing"""
        def process_batch():
            while True:
                batch = []
                # Collect batch
                while len(batch) < self.batch_size:
                    try:
                        item = self.email_queue.get(timeout=5)
                        batch.append(item)
                    except:
                        break
                
                # Process batch
                if batch:
                    self._process_email_batch(batch)
                
                time.sleep(1)
        
        thread = threading.Thread(target=process_batch, daemon=True)
        thread.start()
    
    def _process_email_batch(self, batch: List[Dict]):
        """Process a batch of emails efficiently"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        
        for item in batch:
            supplier = item['supplier']
            template_type = item['template_type']
            
            # Generate email with caching
            content, tokens = self.generate_email_optimized(supplier, template_type)
            
            # Send email
            subject = f"Partnership Opportunity - {supplier.get('products', 'Products')[:50]}"
            success = self.send_email_smtp(
                supplier.get('email', supplier.get('company_email')),
                subject,
                content
            )
            
            # Log to database
            cur.execute("""
                INSERT INTO email_log (supplier_id, supplier_email, subject, content, sent_at, status, tokens_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                supplier.get('id'),
                supplier.get('email', supplier.get('company_email')),
                subject,
                content,
                datetime.now(),
                'sent' if success else 'failed',
                tokens
            ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def _track_tokens(self, tokens: int):
        """Track token usage for cost monitoring"""
        self.token_usage['daily'] += tokens
        self.token_usage['monthly'] += tokens
        
        # Reset daily counter
        if datetime.now().date() > self.token_usage['last_reset'].date():
            self.token_usage['daily'] = tokens
            self.token_usage['last_reset'] = datetime.now()
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        # Approximate costs (gpt-4o-mini pricing)
        cost_per_1k_tokens = 0.00015  # $0.15 per 1M tokens
        
        return {
            'tokens': {
                'daily': self.token_usage['daily'],
                'monthly': self.token_usage['monthly'],
                'daily_cost': f"${self.token_usage['daily'] * cost_per_1k_tokens / 1000:.4f}",
                'monthly_cost': f"${self.token_usage['monthly'] * cost_per_1k_tokens / 1000:.4f}"
            },
            'cache': {
                'enabled': self.cache_enabled,
                'entries': len(self._cache),
                'hit_rate': 'Calculate based on logs'
            },
            'email_queue': self.email_queue.qsize()
        }
    
    @lru_cache(maxsize=1000)
    def analyze_supplier_priority(self, supplier_type: str, country: str) -> int:
        """Cache supplier priority analysis"""
        # Priority scoring based on business rules
        priority = 50  # Base score
        
        # Country bonuses
        priority_countries = ['Italy', 'Spain', 'Germany', 'USA', 'France']
        if country in priority_countries:
            priority += 20
        
        # Type bonuses
        if 'manufacturer' in supplier_type.lower():
            priority += 15
        if 'organic' in supplier_type.lower():
            priority += 10
        
        return priority


# Singleton instance
_email_service = None

def get_email_service() -> OptimizedEmailService:
    """Get singleton email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = OptimizedEmailService()
    return _email_service