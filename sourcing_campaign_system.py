"""
FoodXchange Intelligent Sourcing Campaign System
===============================================
Complete solution for product search, supplier matching, bulk email campaigns,
and AI-powered response analysis.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import uuid
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Load environment variables
load_dotenv()

class SourcingCampaignSystem:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def advanced_product_search(self, search_query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """
        Advanced product search with intelligent matching
        
        Args:
            search_query: Product search terms (e.g., "organic olive oil extra virgin")
            filters: Additional filters like country, certifications, minimum rating
            
        Returns:
            List of matching suppliers with relevance scores
        """
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Build search conditions
        search_terms = search_query.lower().split()
        
        # Base query with full-text search and keyword matching
        query = """
            WITH search_scores AS (
                SELECT 
                    s.*,
                    -- Calculate relevance score
                    (
                        -- Product match score
                        CASE 
                            WHEN LOWER(products) LIKE %s THEN 100
                            ELSE 0
                        END +
                        -- Individual term matches
                        %s +
                        -- Supplier name match
                        CASE 
                            WHEN LOWER(supplier_name) LIKE %s THEN 50
                            ELSE 0
                        END +
                        -- Country bonus for specific products
                        CASE 
                            WHEN %s AND country IN %s THEN 30
                            ELSE 0
                        END +
                        -- Certification bonus
                        CASE 
                            WHEN LOWER(products) LIKE '%%organic%%' AND %s THEN 20
                            WHEN LOWER(products) LIKE '%%certified%%' THEN 10
                            ELSE 0
                        END +
                        -- Verified supplier bonus
                        CASE WHEN verified = true THEN 15 ELSE 0 END
                    ) as relevance_score
                FROM suppliers s
                WHERE 
                    -- Must have products
                    products IS NOT NULL AND LENGTH(products) > 50
                    -- Product contains at least one search term
                    AND (%s)
            )
            SELECT 
                id,
                supplier_name,
                company_name,
                country,
                products,
                company_email,
                company_website,
                contact_person,
                phone,
                verified,
                rating,
                relevance_score,
                -- Extract key product matches
                ARRAY(
                    SELECT DISTINCT term 
                    FROM unnest(ARRAY%s) as term 
                    WHERE LOWER(products) LIKE '%%' || term || '%%'
                ) as matched_terms
            FROM search_scores
            WHERE relevance_score > 0
        """
        
        # Build parameters
        full_search = f"%{search_query.lower()}%"
        
        # Individual term scoring
        term_scoring = " + ".join([
            f"CASE WHEN LOWER(products) LIKE '%{term}%' THEN 20 ELSE 0 END"
            for term in search_terms
        ])
        
        # Country preferences based on product
        country_prefs = {
            'olive oil': ['Italy', 'Spain', 'Greece', 'Turkey'],
            'pasta': ['Italy'],
            'cheese': ['France', 'Italy', 'Netherlands', 'Switzerland'],
            'chocolate': ['Belgium', 'Switzerland', 'Germany'],
            'wine': ['France', 'Italy', 'Spain', 'Portugal'],
            'tea': ['China', 'India', 'Sri Lanka', 'Japan'],
            'coffee': ['Brazil', 'Colombia', 'Ethiopia', 'Vietnam']
        }
        
        preferred_countries = []
        for product, countries in country_prefs.items():
            if product in search_query.lower():
                preferred_countries.extend(countries)
        
        has_country_pref = len(preferred_countries) > 0
        country_tuple = tuple(preferred_countries) if preferred_countries else ('',)
        
        # Product term conditions
        term_conditions = " OR ".join([
            f"LOWER(products) LIKE '%{term}%'"
            for term in search_terms
        ])
        
        # Apply filters
        filter_conditions = []
        params = [
            full_search,
            term_scoring,
            full_search,
            has_country_pref,
            country_tuple,
            'organic' in search_query.lower(),
            term_conditions,
            search_terms
        ]
        
        if filters:
            if filters.get('countries'):
                filter_conditions.append("AND country IN %s")
                params.append(tuple(filters['countries']))
            
            if filters.get('verified_only'):
                filter_conditions.append("AND verified = true")
            
            if filters.get('min_rating'):
                filter_conditions.append("AND rating >= %s")
                params.append(filters['min_rating'])
            
            if filters.get('has_email'):
                filter_conditions.append("AND company_email IS NOT NULL AND company_email != ''")
        
        # Add filter conditions to query
        if filter_conditions:
            query = query.replace("WHERE relevance_score > 0", 
                                f"WHERE relevance_score > 0 {' '.join(filter_conditions)}")
        
        # Order by relevance
        query += " ORDER BY relevance_score DESC, rating DESC NULLS LAST, verified DESC"
        
        # Limit results
        limit = filters.get('limit', 100) if filters else 100
        query += f" LIMIT {limit}"
        
        # Execute query
        cur.execute(query, params)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return results
    
    def create_sourcing_project(self, project_name: str, search_query: str, 
                              supplier_ids: List[int], user_email: str) -> int:
        """Create a new sourcing project with selected suppliers"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            # Create project
            cur.execute("""
                INSERT INTO projects (project_name, description, created_at, user_email)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                project_name,
                f"Sourcing project for: {search_query}",
                datetime.now(),
                user_email
            ))
            
            project_id = cur.fetchone()['id']
            
            # Add suppliers to project
            for supplier_id in supplier_ids:
                cur.execute("""
                    INSERT INTO project_suppliers (project_id, supplier_id, added_at)
                    VALUES (%s, %s, %s)
                """, (project_id, supplier_id, datetime.now()))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return project_id
            
        except Exception as e:
            conn.rollback()
            raise e
    
    def create_email_campaign(self, project_id: int, email_template: Dict[str, str]) -> str:
        """Create an email campaign for a sourcing project"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        campaign_id = str(uuid.uuid4())
        
        try:
            # Create campaign
            cur.execute("""
                INSERT INTO email_campaigns 
                (id, project_id, subject, template_body, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                campaign_id,
                project_id,
                email_template['subject'],
                email_template['body'],
                'draft',
                datetime.now()
            ))
            
            # Get suppliers for this project
            cur.execute("""
                SELECT s.* 
                FROM suppliers s
                JOIN project_suppliers ps ON s.id = ps.supplier_id
                WHERE ps.project_id = %s
                AND s.company_email IS NOT NULL
                AND s.company_email != ''
            """, (project_id,))
            
            suppliers = cur.fetchall()
            
            # Create email queue entries
            for supplier in suppliers:
                tracking_id = str(uuid.uuid4())
                
                # Personalize email
                personalized_body = email_template['body'].format(
                    supplier_name=supplier['supplier_name'],
                    contact_person=supplier['contact_person'] or 'Sourcing Manager',
                    company_name=supplier['company_name'] or supplier['supplier_name'],
                    products=supplier['products'][:200] + '...' if len(supplier['products']) > 200 else supplier['products']
                )
                
                cur.execute("""
                    INSERT INTO email_queue
                    (campaign_id, supplier_id, supplier_email, subject, body, 
                     tracking_id, status, scheduled_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    campaign_id,
                    supplier['id'],
                    supplier['company_email'],
                    email_template['subject'],
                    personalized_body,
                    tracking_id,
                    'pending',
                    datetime.now()
                ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return campaign_id
            
        except Exception as e:
            conn.rollback()
            raise e
    
    def send_campaign_emails(self, campaign_id: str, batch_size: int = 50, 
                           delay_seconds: int = 2) -> Dict[str, int]:
        """Send emails for a campaign in batches"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        stats = {'sent': 0, 'failed': 0, 'skipped': 0}
        
        try:
            # Get pending emails
            cur.execute("""
                SELECT * FROM email_queue
                WHERE campaign_id = %s
                AND status = 'pending'
                ORDER BY scheduled_at
                LIMIT %s
            """, (campaign_id, batch_size))
            
            emails = cur.fetchall()
            
            # Set up SMTP connection
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                
                for email in emails:
                    try:
                        # Create message
                        msg = MIMEMultipart('alternative')
                        msg['Subject'] = email['subject']
                        msg['From'] = self.smtp_username
                        msg['To'] = email['supplier_email']
                        
                        # Add tracking pixel
                        tracking_url = f"https://yourdomain.com/track/{email['tracking_id']}"
                        html_body = f"""
                        <html>
                        <body>
                        {email['body'].replace('\n', '<br>')}
                        <img src="{tracking_url}" width="1" height="1" style="display:none;">
                        </body>
                        </html>
                        """
                        
                        # Add plain text and HTML parts
                        msg.attach(MIMEText(email['body'], 'plain'))
                        msg.attach(MIMEText(html_body, 'html'))
                        
                        # Send email
                        server.send_message(msg)
                        
                        # Update status
                        cur.execute("""
                            UPDATE email_queue
                            SET status = 'sent', sent_at = %s
                            WHERE id = %s
                        """, (datetime.now(), email['id']))
                        
                        # Log in email_log
                        cur.execute("""
                            INSERT INTO email_log
                            (supplier_id, supplier_email, project_id, campaign_id, 
                             sent_at, status, tracking_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            email['supplier_id'],
                            email['supplier_email'],
                            email['project_id'],
                            campaign_id,
                            datetime.now(),
                            'sent',
                            email['tracking_id']
                        ))
                        
                        stats['sent'] += 1
                        
                        # Delay between emails
                        time.sleep(delay_seconds)
                        
                    except Exception as e:
                        # Mark as failed
                        cur.execute("""
                            UPDATE email_queue
                            SET status = 'failed', error_message = %s
                            WHERE id = %s
                        """, (str(e), email['id']))
                        
                        stats['failed'] += 1
                
                conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
        
        return stats
    
    def track_email_response(self, tracking_id: str, response_type: str = 'opened'):
        """Track email opens and clicks"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            # Update email log
            cur.execute("""
                UPDATE email_log
                SET 
                    opened_at = CASE 
                        WHEN %s = 'opened' AND opened_at IS NULL 
                        THEN %s 
                        ELSE opened_at 
                    END,
                    clicked_at = CASE 
                        WHEN %s = 'clicked' AND clicked_at IS NULL 
                        THEN %s 
                        ELSE clicked_at 
                    END,
                    response_status = %s
                WHERE tracking_id = %s
            """, (
                response_type, datetime.now(),
                response_type, datetime.now(),
                response_type,
                tracking_id
            ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    def analyze_campaign_responses(self, campaign_id: str) -> Dict[str, Any]:
        """Analyze email campaign responses"""
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Get campaign statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total_sent,
                COUNT(CASE WHEN opened_at IS NOT NULL THEN 1 END) as opened,
                COUNT(CASE WHEN clicked_at IS NOT NULL THEN 1 END) as clicked,
                COUNT(CASE WHEN responded_at IS NOT NULL THEN 1 END) as responded,
                MIN(sent_at) as first_sent,
                MAX(sent_at) as last_sent
            FROM email_log
            WHERE campaign_id = %s
        """, (campaign_id,))
        
        stats = cur.fetchone()
        
        # Get response details by country
        cur.execute("""
            SELECT 
                s.country,
                COUNT(*) as sent,
                COUNT(CASE WHEN el.opened_at IS NOT NULL THEN 1 END) as opened,
                COUNT(CASE WHEN el.responded_at IS NOT NULL THEN 1 END) as responded
            FROM email_log el
            JOIN suppliers s ON el.supplier_id = s.id
            WHERE el.campaign_id = %s
            GROUP BY s.country
            ORDER BY responded DESC, opened DESC
        """, (campaign_id,))
        
        country_stats = cur.fetchall()
        
        # Get top responders
        cur.execute("""
            SELECT 
                s.supplier_name,
                s.country,
                s.company_email,
                el.opened_at,
                el.clicked_at,
                el.responded_at,
                er.response_text
            FROM email_log el
            JOIN suppliers s ON el.supplier_id = s.id
            LEFT JOIN email_responses er ON el.id = er.email_log_id
            WHERE el.campaign_id = %s
            AND (el.opened_at IS NOT NULL OR el.responded_at IS NOT NULL)
            ORDER BY el.responded_at DESC NULLS LAST, el.opened_at DESC
            LIMIT 20
        """, (campaign_id,))
        
        top_responders = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Calculate rates
        total = stats['total_sent'] or 1
        
        return {
            'summary': {
                'total_sent': stats['total_sent'],
                'opened': stats['opened'],
                'clicked': stats['clicked'],
                'responded': stats['responded'],
                'open_rate': round((stats['opened'] / total) * 100, 1),
                'click_rate': round((stats['clicked'] / total) * 100, 1),
                'response_rate': round((stats['responded'] / total) * 100, 1),
                'campaign_duration': str(stats['last_sent'] - stats['first_sent']) if stats['first_sent'] else None
            },
            'by_country': country_stats,
            'top_responders': top_responders
        }
    
    def ai_analyze_responses(self, campaign_id: str) -> Dict[str, Any]:
        """Use AI to analyze email responses and categorize suppliers"""
        # This would integrate with Azure OpenAI to:
        # 1. Analyze response sentiment
        # 2. Extract key information (pricing, MOQ, availability)
        # 3. Categorize suppliers (interested, not interested, need more info)
        # 4. Generate follow-up recommendations
        
        # Placeholder for AI integration
        return {
            'interested_suppliers': [],
            'need_followup': [],
            'not_interested': [],
            'key_insights': [],
            'recommended_actions': []
        }


# Example usage
if __name__ == "__main__":
    system = SourcingCampaignSystem()
    
    # 1. Search for products
    print("🔍 Searching for organic olive oil suppliers...")
    results = system.advanced_product_search(
        "organic olive oil extra virgin",
        filters={
            'countries': ['Italy', 'Spain', 'Greece'],
            'verified_only': True,
            'has_email': True,
            'limit': 50
        }
    )
    
    print(f"\n📊 Found {len(results)} matching suppliers:")
    for supplier in results[:5]:
        print(f"\n{supplier['supplier_name']} ({supplier['country']})")
        print(f"  Score: {supplier['relevance_score']}")
        print(f"  Matched terms: {', '.join(supplier['matched_terms'])}")
        print(f"  Products: {supplier['products'][:100]}...")
    
    # 2. Create sourcing project
    supplier_ids = [s['id'] for s in results[:20]]
    project_id = system.create_sourcing_project(
        "Organic Olive Oil Q1 2025",
        "organic olive oil extra virgin",
        supplier_ids,
        "buyer@foodxchange.com"
    )
    
    print(f"\n✅ Created sourcing project ID: {project_id}")
    
    # 3. Create email campaign
    email_template = {
        'subject': 'Partnership Opportunity - Organic Olive Oil Supply',
        'body': """Dear {contact_person},

I hope this email finds you well. I am reaching out from FoodXchange regarding a potential partnership opportunity.

We are currently sourcing high-quality organic extra virgin olive oil for our Q1 2025 requirements and came across {company_name} as a leading supplier in {products}.

We would be interested in discussing:
- Your current product range and certifications
- Minimum order quantities
- Pricing for bulk orders
- Delivery timelines to the USA

Could we schedule a brief call next week to discuss this opportunity further?

Best regards,
[Your Name]
FoodXchange Sourcing Team"""
    }
    
    campaign_id = system.create_email_campaign(project_id, email_template)
    print(f"\n📧 Created email campaign ID: {campaign_id}")
    
    # 4. Send emails (would be done in batches)
    # stats = system.send_campaign_emails(campaign_id)
    # print(f"\n📤 Sent {stats['sent']} emails")
    
    # 5. Analyze responses
    # analysis = system.analyze_campaign_responses(campaign_id)
    # print(f"\n📊 Campaign Analysis:")
    # print(f"  Open rate: {analysis['summary']['open_rate']}%")
    # print(f"  Response rate: {analysis['summary']['response_rate']}%")