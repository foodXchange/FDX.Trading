"""
Email Response Analyzer with AI Categorization
=============================================
Analyzes supplier email responses and extracts key business data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json
import re
import sys
from typing import Dict, List, Any, Optional

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

class EmailResponseAnalyzer:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        
    def get_db_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def analyze_email_response(self, email_content: str, supplier_id: int, 
                             email_log_id: int) -> Dict[str, Any]:
        """
        Analyze email response and extract key business information
        """
        
        analysis = {
            'category': self._categorize_response(email_content),
            'extracted_data': self._extract_business_data(email_content),
            'sentiment': self._analyze_sentiment(email_content),
            'scores': self._calculate_response_scores(email_content),
            'follow_up_required': False,
            'next_action': None
        }
        
        # Determine follow-up actions
        if analysis['category'] == 'interested_need_info':
            analysis['follow_up_required'] = True
            analysis['next_action'] = 'Send detailed product specifications'
        elif analysis['category'] == 'interested_with_pricing':
            analysis['follow_up_required'] = True
            analysis['next_action'] = 'Review pricing and negotiate terms'
        
        # Save analysis to database
        self._save_analysis(email_log_id, supplier_id, analysis)
        
        return analysis
    
    def _categorize_response(self, email_content: str) -> str:
        """
        Categorize email response using pattern matching and keywords
        """
        
        content_lower = email_content.lower()
        
        # Category patterns
        patterns = {
            'interested_with_pricing': [
                r'price.*\$\d+',
                r'cost.*\d+.*per',
                r'quote.*attached',
                r'pricing.*follows',
                r'per\s+(unit|kg|ton|container)',
                r'fob\s+price',
                r'cif\s+price',
                r'our\s+prices?\s+are'
            ],
            'interested_need_info': [
                r'need\s+more\s+information',
                r'please\s+provide.*details',
                r'could\s+you.*specify',
                r'require.*specifications',
                r'send.*requirements',
                r'what.*quantity',
                r'interested.*know\s+more'
            ],
            'not_interested': [
                r'not\s+interested',
                r'unable\s+to\s+supply',
                r'cannot\s+provide',
                r'not\s+our\s+product',
                r'don\'t\s+manufacture',
                r'decline.*offer',
                r'not\s+in\s+our.*range'
            ],
            'out_of_stock': [
                r'out\s+of\s+stock',
                r'currently\s+unavailable',
                r'stock.*depleted',
                r'cannot\s+meet.*quantity',
                r'insufficient.*capacity',
                r'fully\s+booked',
                r'lead\s+time.*months'
            ]
        }
        
        # Check each category
        for category, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, content_lower):
                    return category
        
        # Default category if no patterns match
        if 'thank you' in content_lower and 'interest' in content_lower:
            return 'interested_need_info'
        
        return 'uncategorized'
    
    def _extract_business_data(self, email_content: str) -> Dict[str, Any]:
        """
        Extract key business data from email content
        """
        
        extracted = {
            'pricing': self._extract_pricing(email_content),
            'moq': self._extract_moq(email_content),
            'lead_time': self._extract_lead_time(email_content),
            'payment_terms': self._extract_payment_terms(email_content),
            'certifications': self._extract_certifications(email_content),
            'packaging_options': self._extract_packaging(email_content)
        }
        
        return extracted
    
    def _extract_pricing(self, content: str) -> Dict[str, Any]:
        """Extract pricing information"""
        
        pricing = {
            'currency': None,
            'prices': [],
            'price_basis': None  # FOB, CIF, EXW, etc.
        }
        
        # Currency patterns
        currency_match = re.search(r'(USD|EUR|GBP|CNY|INR|\$|€|£)', content)
        if currency_match:
            pricing['currency'] = currency_match.group(1)
        
        # Price patterns
        price_patterns = [
            r'(\$|USD|EUR|€|£)\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(USD|EUR|GBP|per|/)',
            r'price[:\s]+(\d+(?:,\d{3})*(?:\.\d{2})?)',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    price_str = match[1] if match[0] in ['$', 'USD', 'EUR', '€', '£'] else match[0]
                else:
                    price_str = match
                
                # Clean and convert price
                price_clean = price_str.replace(',', '')
                try:
                    price_value = float(price_clean)
                    
                    # Find unit if mentioned nearby
                    unit_match = re.search(
                        rf'{re.escape(price_str)}\s*(?:per|/)?\s*(\w+)', 
                        content, 
                        re.IGNORECASE
                    )
                    unit = unit_match.group(1) if unit_match else 'unit'
                    
                    pricing['prices'].append({
                        'value': price_value,
                        'unit': unit,
                        'context': content[max(0, content.find(price_str)-20):content.find(price_str)+50]
                    })
                except ValueError:
                    continue
        
        # Price basis (FOB, CIF, etc.)
        basis_match = re.search(r'(FOB|CIF|EXW|DDP|DAP|CFR)', content, re.IGNORECASE)
        if basis_match:
            pricing['price_basis'] = basis_match.group(1).upper()
        
        return pricing
    
    def _extract_moq(self, content: str) -> Dict[str, Any]:
        """Extract minimum order quantity"""
        
        moq = {
            'quantity': None,
            'unit': None,
            'flexible': False
        }
        
        # MOQ patterns
        moq_patterns = [
            r'(?:MOQ|minimum\s+order\s+quantity)[:\s]+(\d+(?:,\d{3})*)\s*(\w+)?',
            r'minimum[:\s]+(\d+(?:,\d{3})*)\s*(\w+)?',
            r'at\s+least\s+(\d+(?:,\d{3})*)\s*(\w+)?',
            r'(\d+(?:,\d{3})*)\s*(container|pallet|kg|ton|unit)s?\s+minimum'
        ]
        
        for pattern in moq_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                moq['quantity'] = int(match.group(1).replace(',', ''))
                if len(match.groups()) > 1 and match.group(2):
                    moq['unit'] = match.group(2).lower()
                break
        
        # Check for flexibility
        if re.search(r'negotiable|flexible|discuss', content, re.IGNORECASE):
            moq['flexible'] = True
        
        return moq
    
    def _extract_lead_time(self, content: str) -> Dict[str, Any]:
        """Extract lead time information"""
        
        lead_time = {
            'duration': None,
            'unit': None,
            'production_time': None,
            'shipping_time': None
        }
        
        # Lead time patterns
        patterns = [
            r'lead\s+time[:\s]+(\d+)\s*(days?|weeks?|months?)',
            r'delivery[:\s]+(\d+)\s*(days?|weeks?|months?)',
            r'(\d+)\s*(days?|weeks?|months?)\s+(?:for\s+)?delivery',
            r'ready\s+in\s+(\d+)\s*(days?|weeks?|months?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                lead_time['duration'] = int(match.group(1))
                lead_time['unit'] = match.group(2).rstrip('s')
                break
        
        # Production time
        prod_match = re.search(r'production[:\s]+(\d+)\s*(days?|weeks?)', content, re.IGNORECASE)
        if prod_match:
            lead_time['production_time'] = f"{prod_match.group(1)} {prod_match.group(2)}"
        
        # Shipping time
        ship_match = re.search(r'shipping[:\s]+(\d+)\s*(days?|weeks?)', content, re.IGNORECASE)
        if ship_match:
            lead_time['shipping_time'] = f"{ship_match.group(1)} {ship_match.group(2)}"
        
        return lead_time
    
    def _extract_payment_terms(self, content: str) -> List[str]:
        """Extract payment terms"""
        
        payment_terms = []
        
        # Common payment terms
        terms_patterns = [
            r'(T/T|L/C|D/P|D/A|CAD|COD)',
            r'(\d+)%\s*(?:advance|deposit|down\s*payment)',
            r'net\s*(\d+)\s*days?',
            r'payment.*?(advance|delivery|shipment)',
            r'(30|60|90)\s*days?\s*credit'
        ]
        
        for pattern in terms_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    term = ' '.join(match)
                else:
                    term = match
                payment_terms.append(term)
        
        return list(set(payment_terms))  # Remove duplicates
    
    def _extract_certifications(self, content: str) -> List[str]:
        """Extract mentioned certifications"""
        
        certs = []
        
        cert_patterns = [
            'ISO', 'HACCP', 'BRC', 'IFS', 'FDA', 'CE', 
            'Kosher', 'Halal', 'Organic', 'Fair Trade',
            'FSSC', 'GMP', 'GLOBALG.A.P', 'SQF'
        ]
        
        for cert in cert_patterns:
            if re.search(rf'\b{cert}\b', content, re.IGNORECASE):
                certs.append(cert)
        
        return certs
    
    def _extract_packaging(self, content: str) -> List[str]:
        """Extract packaging options"""
        
        packaging = []
        
        pack_patterns = [
            r'(\d+)\s*(kg|g|lb|oz)\s*(?:pack|bag|box)',
            r'bulk\s*packaging',
            r'private\s*label',
            r'custom\s*packaging',
            r'(\d+)\s*pieces?\s*per\s*(?:box|carton|case)'
        ]
        
        for pattern in pack_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    pack = ' '.join(match)
                else:
                    pack = match
                packaging.append(pack)
        
        return packaging
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze email sentiment and tone"""
        
        sentiment = {
            'overall': 'neutral',
            'enthusiasm_level': 0,
            'professionalism': 0,
            'urgency': 0
        }
        
        # Positive indicators
        positive_words = [
            'pleased', 'happy', 'excited', 'delighted', 'excellent',
            'great', 'wonderful', 'perfect', 'ideal', 'best'
        ]
        
        # Professional indicators
        professional_words = [
            'regarding', 'furthermore', 'therefore', 'kindly', 'sincerely',
            'professional', 'establish', 'partnership', 'cooperation'
        ]
        
        # Urgency indicators
        urgency_words = [
            'urgent', 'asap', 'immediately', 'quickly', 'soon',
            'priority', 'rush', 'expedite'
        ]
        
        content_lower = content.lower()
        
        # Calculate scores
        sentiment['enthusiasm_level'] = sum(1 for word in positive_words if word in content_lower)
        sentiment['professionalism'] = sum(1 for word in professional_words if word in content_lower)
        sentiment['urgency'] = sum(1 for word in urgency_words if word in content_lower)
        
        # Determine overall sentiment
        if sentiment['enthusiasm_level'] >= 3:
            sentiment['overall'] = 'very_positive'
        elif sentiment['enthusiasm_level'] >= 1:
            sentiment['overall'] = 'positive'
        elif 'unfortunately' in content_lower or 'sorry' in content_lower:
            sentiment['overall'] = 'negative'
        
        return sentiment
    
    def _calculate_response_scores(self, content: str) -> Dict[str, float]:
        """Calculate supplier quality scores based on response"""
        
        scores = {
            'response_quality': 0,
            'detail_level': 0,
            'clarity': 0,
            'completeness': 0
        }
        
        # Response quality (0-10)
        if len(content) > 500:
            scores['response_quality'] += 3
        elif len(content) > 200:
            scores['response_quality'] += 2
        else:
            scores['response_quality'] += 1
        
        # Check for business data
        if re.search(r'\$\d+|\d+\s*USD|price', content, re.IGNORECASE):
            scores['response_quality'] += 2
        if re.search(r'MOQ|minimum', content, re.IGNORECASE):
            scores['response_quality'] += 2
        if re.search(r'lead\s*time|delivery', content, re.IGNORECASE):
            scores['response_quality'] += 2
        if re.search(r'payment|terms', content, re.IGNORECASE):
            scores['response_quality'] += 1
        
        # Detail level (0-10)
        details_count = 0
        for pattern in [r'\d+', r'specification', r'description', r'include', r'feature']:
            details_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        scores['detail_level'] = min(10, details_count / 3)
        
        # Clarity (0-10)
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if 10 <= avg_sentence_length <= 20:
            scores['clarity'] = 8
        elif 5 <= avg_sentence_length <= 25:
            scores['clarity'] = 6
        else:
            scores['clarity'] = 4
        
        # Add points for structure
        if content.count('\n') > 3:
            scores['clarity'] += 2
        
        # Completeness (0-10)
        required_elements = ['price', 'moq', 'delivery', 'product', 'contact']
        found_elements = sum(1 for elem in required_elements if elem in content.lower())
        scores['completeness'] = (found_elements / len(required_elements)) * 10
        
        return scores
    
    def _save_analysis(self, email_log_id: int, supplier_id: int, 
                      analysis: Dict[str, Any]) -> None:
        """Save analysis results to database"""
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        try:
            # Update email_log with response analysis
            cur.execute("""
                UPDATE email_log
                SET 
                    response_category = %s,
                    response_analysis = %s,
                    response_score = %s,
                    analyzed_at = %s
                WHERE id = %s
            """, (
                analysis['category'],
                json.dumps(analysis),
                analysis['scores']['response_quality'],
                datetime.now(),
                email_log_id
            ))
            
            # Save extracted data for quick access
            if analysis['extracted_data']['pricing']['prices']:
                cur.execute("""
                    INSERT INTO supplier_pricing 
                    (supplier_id, product_info, price_data, extracted_from_email, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (supplier_id) DO UPDATE
                    SET price_data = %s, updated_at = %s
                """, (
                    supplier_id,
                    'Email response',
                    json.dumps(analysis['extracted_data']['pricing']),
                    email_log_id,
                    datetime.now(),
                    json.dumps(analysis['extracted_data']['pricing']),
                    datetime.now()
                ))
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving analysis: {e}")
            
        finally:
            cur.close()
            conn.close()
    
    def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for email campaign"""
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Get response categories breakdown
        cur.execute("""
            SELECT 
                response_category,
                COUNT(*) as count,
                AVG(response_score) as avg_score
            FROM email_log
            WHERE campaign_id = %s
            AND response_category IS NOT NULL
            GROUP BY response_category
        """, (campaign_id,))
        
        categories = cur.fetchall()
        
        # Get top responding suppliers
        cur.execute("""
            SELECT 
                s.supplier_name,
                s.country,
                el.response_category,
                el.response_score,
                el.response_analysis->>'extracted_data' as data
            FROM email_log el
            JOIN suppliers s ON el.supplier_id = s.id
            WHERE el.campaign_id = %s
            AND el.response_category IN ('interested_with_pricing', 'interested_need_info')
            ORDER BY el.response_score DESC
            LIMIT 10
        """, (campaign_id,))
        
        top_suppliers = cur.fetchall()
        
        # Get pricing summary
        cur.execute("""
            SELECT 
                MIN((response_analysis->'extracted_data'->'pricing'->'prices'->0->>'value')::float) as min_price,
                MAX((response_analysis->'extracted_data'->'pricing'->'prices'->0->>'value')::float) as max_price,
                AVG((response_analysis->'extracted_data'->'pricing'->'prices'->0->>'value')::float) as avg_price
            FROM email_log
            WHERE campaign_id = %s
            AND response_analysis->'extracted_data'->'pricing'->'prices' IS NOT NULL
        """, (campaign_id,))
        
        pricing_summary = cur.fetchone()
        
        cur.close()
        conn.close()
        
        return {
            'response_categories': categories,
            'top_interested_suppliers': top_suppliers,
            'pricing_summary': pricing_summary,
            'follow_up_required': sum(1 for c in categories if c['response_category'] == 'interested_need_info')
        }


# Demo function
def demo_response_analysis():
    """Demo email response analysis"""
    
    analyzer = EmailResponseAnalyzer()
    
    # Sample email response
    sample_email = """
    Dear FoodXchange Team,
    
    Thank you for your interest in our chocolate wafer products. We are pleased to provide you with the following information:
    
    Our chocolate sandwich cookies are available at USD 2.50 per kg for orders above 1000 kg (MOQ).
    
    Pricing:
    - 1000-5000 kg: $2.50/kg FOB Turkey
    - 5000-10000 kg: $2.35/kg FOB Turkey
    - Above 10000 kg: $2.20/kg FOB Turkey
    
    Lead time is approximately 3-4 weeks from order confirmation.
    Payment terms: 30% advance, 70% against shipping documents.
    
    We are ISO 22000, HACCP, and Halal certified.
    
    Please let us know your specific requirements and we would be happy to send samples.
    
    Best regards,
    Turkish Biscuits Co.
    """
    
    # Analyze the email
    analysis = analyzer.analyze_email_response(
        email_content=sample_email,
        supplier_id=123,
        email_log_id=456
    )
    
    print("📧 Email Response Analysis\n")
    print(f"Category: {analysis['category']}")
    print(f"Sentiment: {analysis['sentiment']['overall']}")
    print(f"\nExtracted Data:")
    print(f"- Pricing: {analysis['extracted_data']['pricing']}")
    print(f"- MOQ: {analysis['extracted_data']['moq']}")
    print(f"- Lead Time: {analysis['extracted_data']['lead_time']}")
    print(f"- Payment Terms: {analysis['extracted_data']['payment_terms']}")
    print(f"\nScores:")
    for score_type, value in analysis['scores'].items():
        print(f"- {score_type}: {value:.1f}/10")


if __name__ == "__main__":
    demo_response_analysis()