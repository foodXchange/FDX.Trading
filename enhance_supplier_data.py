#!/usr/bin/env python3
"""
Enhanced Supplier Data Collector for FDX.trading
Scrapes supplier websites to get detailed product catalogs
Uses Azure OpenAI to understand and classify products
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import requests
from bs4 import BeautifulSoup
import openai
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import re

load_dotenv()

# Azure OpenAI setup
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"

class SupplierDataEnhancer:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
    
    def scrape_website(self, url):
        """Scrape website for product information"""
        try:
            # Add headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text = soup.get_text(separator=' ', strip=True)
            
            # Look for product-related sections
            product_keywords = ['product', 'catalog', 'offer', 'supply', 'sell', 
                              'export', 'wholesale', 'price', 'specification']
            
            relevant_text = []
            for paragraph in soup.find_all(['p', 'div', 'li', 'td']):
                para_text = paragraph.get_text(strip=True)
                if any(keyword in para_text.lower() for keyword in product_keywords):
                    relevant_text.append(para_text)
            
            # Limit to 5000 chars for AI processing
            content = ' '.join(relevant_text)[:5000]
            
            return content if content else text[:5000]
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def extract_products_with_ai(self, website_content, supplier_name):
        """Use AI to extract and classify products from website content"""
        
        if not website_content:
            return None
        
        prompt = f"""
        Analyze this supplier website content and extract their ACTUAL PRODUCTS they SELL (not ingredients they use):
        
        Supplier: {supplier_name}
        Content: {website_content[:3000]}
        
        Return a JSON object with:
        1. "primary_products": List of main products they SELL (not ingredients)
        2. "product_details": Detailed descriptions including sizes, packaging, specifications
        3. "product_categories": Categories (oils, grains, dairy, etc.)
        4. "certifications": Quality certifications mentioned
        5. "packaging_options": Packaging types and sizes available
        6. "is_manufacturer": true/false - do they manufacture or just trade?
        7. "classification": "seller" if they sell products, "user" if they use products as ingredients
        
        Focus on what they SELL, not what they use. If it's a bakery, they're users of oil, not sellers.
        Return ONLY valid JSON.
        """
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a B2B product data extraction expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            print(f"AI extraction error: {e}")
            return None
    
    def enhance_supplier(self, supplier_id):
        """Enhance a single supplier's data"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get supplier info
        cur.execute("""
            SELECT id, supplier_name, company_website, products
            FROM suppliers
            WHERE id = %s
        """, (supplier_id,))
        
        supplier = cur.fetchone()
        if not supplier or not supplier['company_website']:
            return False
        
        # Clean up website URL
        website = supplier['company_website']
        if not website.startswith('http'):
            website = 'https://' + website
        
        print(f"Enhancing {supplier['supplier_name']}...")
        
        # Scrape website
        content = self.scrape_website(website)
        
        if content:
            # Extract products with AI
            extracted = self.extract_products_with_ai(content, supplier['supplier_name'])
            
            if extracted:
                # Update database with enhanced data
                enhanced_products = {
                    'primary_products': extracted.get('primary_products', []),
                    'product_details': extracted.get('product_details', ''),
                    'categories': extracted.get('product_categories', []),
                    'certifications': extracted.get('certifications', []),
                    'packaging': extracted.get('packaging_options', []),
                    'is_manufacturer': extracted.get('is_manufacturer', False)
                }
                
                # Create detailed product description
                detailed_products = f"""
                PRIMARY PRODUCTS: {', '.join(extracted.get('primary_products', []))}
                
                DETAILS: {extracted.get('product_details', '')}
                
                PACKAGING: {', '.join(extracted.get('packaging_options', []))}
                
                CERTIFICATIONS: {', '.join(extracted.get('certifications', []))}
                
                CATEGORIES: {', '.join(extracted.get('product_categories', []))}
                """
                
                # Update supplier record
                cur.execute("""
                    UPDATE suppliers
                    SET products = %s,
                        product_classification = %s,
                        enhanced_data = %s,
                        last_enhanced = NOW()
                    WHERE id = %s
                """, (
                    detailed_products,
                    extracted.get('classification', 'unknown'),
                    json.dumps(enhanced_products),
                    supplier_id
                ))
                
                conn.commit()
                print(f"✓ Enhanced {supplier['supplier_name']}")
                return True
        
        cur.close()
        conn.close()
        return False
    
    def enhance_suppliers_batch(self, query, limit=10):
        """Enhance suppliers matching a query"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Find suppliers to enhance
        cur.execute("""
            SELECT id, supplier_name, company_website
            FROM suppliers
            WHERE LOWER(products) LIKE %s
              AND company_website IS NOT NULL
              AND company_website != ''
              AND (last_enhanced IS NULL OR last_enhanced < NOW() - INTERVAL '30 days')
            LIMIT %s
        """, (f"%{query.lower()}%", limit))
        
        suppliers = cur.fetchall()
        
        enhanced_count = 0
        for supplier in suppliers:
            if self.enhance_supplier(supplier['id']):
                enhanced_count += 1
            time.sleep(2)  # Be polite to websites
        
        cur.close()
        conn.close()
        
        return enhanced_count
    
    def setup_enhanced_columns(self):
        """Add columns for enhanced data"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                ALTER TABLE suppliers
                ADD COLUMN IF NOT EXISTS enhanced_data JSONB,
                ADD COLUMN IF NOT EXISTS last_enhanced TIMESTAMP,
                ADD COLUMN IF NOT EXISTS website_scraped BOOLEAN DEFAULT FALSE
            """)
            
            conn.commit()
            print("Added enhanced data columns")
            
        except Exception as e:
            print(f"Error adding columns: {e}")
            conn.rollback()
        
        cur.close()
        conn.close()

class SmartProductSearch:
    """Search using enhanced supplier data"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
    
    def search_enhanced(self, query):
        """Search with enhanced data priority"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Search enhanced suppliers first
        cur.execute("""
            SELECT 
                id, supplier_name, company_name, country,
                products, enhanced_data, product_classification,
                company_email, company_website, verified, rating,
                CASE 
                    WHEN enhanced_data IS NOT NULL THEN 100
                    ELSE 0
                END as enhancement_score
            FROM suppliers
            WHERE 
                (LOWER(products) LIKE %s OR LOWER(supplier_name) LIKE %s)
                AND (product_classification = 'seller' OR product_classification IS NULL)
            ORDER BY 
                enhancement_score DESC,
                CASE WHEN product_classification = 'seller' THEN 1 ELSE 2 END,
                rating DESC NULLS LAST
            LIMIT 100
        """, (f"%{query.lower()}%", f"%{query.lower()}%"))
        
        results = cur.fetchall()
        
        formatted_results = []
        for r in results:
            # Use enhanced data if available
            if r.get('enhanced_data'):
                try:
                    enhanced = json.loads(r['enhanced_data'])
                    product_list = enhanced.get('primary_products', [])
                    product_text = ', '.join(product_list) if product_list else r['products']
                except:
                    product_text = r['products']
            else:
                product_text = r['products']
            
            formatted_results.append({
                'supplier_id': r['id'],
                'supplier_name': r['supplier_name'],
                'company_name': r['company_name'] or r['supplier_name'],
                'country': r['country'] or 'Unknown',
                'email': r['company_email'] or '',
                'website': r['company_website'] or '',
                'products': product_text,
                'product_preview': (product_text or '')[:500],
                'classification': r.get('product_classification', 'unknown'),
                'is_enhanced': r.get('enhanced_data') is not None,
                'verified': r.get('verified', False),
                'rating': float(r['rating']) if r.get('rating') else None
            })
        
        # Separate enhanced vs non-enhanced
        enhanced = [r for r in formatted_results if r['is_enhanced']]
        non_enhanced = [r for r in formatted_results if not r['is_enhanced']]
        
        cur.close()
        conn.close()
        
        return {
            'query': query,
            'total_results': len(formatted_results),
            'enhanced_results': len(enhanced),
            'results': enhanced + non_enhanced  # Enhanced first
        }

if __name__ == "__main__":
    # Setup
    enhancer = SupplierDataEnhancer()
    
    print("Setting up enhanced data columns...")
    enhancer.setup_enhanced_columns()
    
    # Test enhancement for sunflower oil suppliers
    print("\nEnhancing sunflower oil suppliers...")
    enhanced = enhancer.enhance_suppliers_batch("sunflower oil", limit=3)
    print(f"Enhanced {enhanced} suppliers")
    
    # Test search with enhanced data
    print("\nSearching with enhanced data...")
    searcher = SmartProductSearch()
    results = searcher.search_enhanced("sunflower oil")
    
    print(f"\nResults: {results['total_results']} total, {results['enhanced_results']} enhanced")
    
    if results['results']:
        print("\nTop enhanced suppliers:")
        for r in results['results'][:3]:
            if r['is_enhanced']:
                print(f"\n✓ {r['supplier_name']} ({r['country']}) - ENHANCED")
                print(f"  Products: {r['product_preview'][:200]}...")
                print(f"  Classification: {r['classification']}")