import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

class FixedSearchSystem:
    def __init__(self):
        self.db_url = 'postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require'
    
    def search_suppliers(self, query, user_email=None, filters=None, limit=50):
        try:
            conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
            cur = conn.cursor()
            search_term = f"%{query.lower()}%"
            
            cur.execute("""
                SELECT id, supplier_name, company_name, country, 
                       company_email, company_website,
                       phone, verified, rating, products
                FROM suppliers
                WHERE products IS NOT NULL 
                AND company_email IS NOT NULL
                AND LOWER(products) LIKE %s
                ORDER BY rating DESC NULLS LAST
                LIMIT %s
            """, (search_term, limit))
            
            results = cur.fetchall()
            cur.close()
            conn.close()
            
            formatted_results = []
            for idx, r in enumerate(results, 1):
                formatted_results.append({
                    'rank': idx,
                    'supplier_id': r['id'],
                    'supplier_name': r['supplier_name'],
                    'company_name': r['company_name'],
                    'country': r['country'],
                    'email': r['company_email'],
                    'website': r['company_website'],
                    'phone': r['phone'],
                    'verified': r['verified'],
                    'rating': float(r['rating']) if r['rating'] else None,
                    'match_percentage': 85.0,
                    'product_preview': r['products'][:300] if r['products'] else '',
                    'matched_terms': [query.split()[0]] if query else []
                })
            
            return {
                'query': query,
                'total_results': len(results),
                'execution_time_ms': 100,
                'timestamp': datetime.now().isoformat(),
                'results': formatted_results
            }
        except Exception as e:
            print(f"Search error: {e}")
            return {
                'query': query,
                'total_results': 0,
                'execution_time_ms': 0,
                'timestamp': datetime.now().isoformat(),
                'results': [],
                'error': str(e)
            }
    
    def get_search_history(self, user_email, limit=20):
        return []
    
    def get_popular_searches(self, limit=10):
        return []