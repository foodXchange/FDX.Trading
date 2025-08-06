"""
Fixed Search System - Working Database Search
=============================================
Simple, working search that actually functions
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from typing import List, Dict, Any, Optional

load_dotenv()

class FixedSearchSystem:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            self.db_url = "postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require"
    
    def get_db_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def search_suppliers(self, query: str, user_email: str = None, 
                        filters: Dict[str, Any] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Simple working search that actually returns results
        """
        
        start_time = datetime.now()
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Simple, WORKING query
        search_pattern = f"%{query.lower()}%"
        
        # Build the WHERE clause
        where_conditions = [
            "products IS NOT NULL",
            "company_email IS NOT NULL",
            "(LOWER(products) LIKE %s OR LOWER(supplier_name) LIKE %s OR LOWER(company_name) LIKE %s)"
        ]
        
        params = [search_pattern, search_pattern, search_pattern]
        
        # Add filters if provided
        if filters:
            if filters.get('verified_only'):
                where_conditions.append("verified = true")
            
            if filters.get('min_rating'):
                where_conditions.append("rating >= %s")
                params.append(filters['min_rating'])
            
            if filters.get('countries') and len(filters['countries']) > 0:
                placeholders = ','.join(['%s'] * len(filters['countries']))
                where_conditions.append(f"country IN ({placeholders})")
                params.extend(filters['countries'])
        
        # Build the complete query
        query_sql = f"""
            SELECT 
                id, supplier_name, company_name, country, products,
                company_email, company_website, company_phone,
                verified, rating,
                SUBSTRING(products, 1, 300) as product_preview
            FROM suppliers
            WHERE {' AND '.join(where_conditions)}
            ORDER BY 
                CASE WHEN LOWER(products) LIKE %s THEN 1 ELSE 2 END,
                rating DESC NULLS LAST,
                verified DESC
            LIMIT %s
        """
        
        # Add ordering params
        params.append(search_pattern)
        params.append(limit)
        
        try:
            # Execute the query
            cur.execute(query_sql, params)
            results = cur.fetchall()
            
            # Calculate execution time
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Save to search history if table exists
            if user_email:
                try:
                    cur.execute("""
                        INSERT INTO search_history 
                        (user_email, query, result_count, timestamp)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        user_email,
                        query,
                        len(results),
                        datetime.now()
                    ))
                    conn.commit()
                except:
                    # Ignore if search_history table doesn't exist
                    pass
            
            cur.close()
            conn.close()
            
            # Format results
            formatted_results = []
            for idx, result in enumerate(results, 1):
                formatted_results.append({
                    'rank': idx,
                    'supplier_id': result['id'],
                    'supplier_name': result['supplier_name'],
                    'company_name': result['company_name'],
                    'country': result['country'],
                    'email': result['company_email'],
                    'website': result['company_website'],
                    'phone': result['company_phone'],
                    'verified': result['verified'],
                    'rating': float(result['rating']) if result['rating'] else None,
                    'product_preview': result['product_preview'],
                    'match_percentage': 85.0  # Simple fixed score for now
                })
            
            return {
                'query': query,
                'total_results': len(results),
                'execution_time_ms': execution_time,
                'timestamp': datetime.now().isoformat(),
                'results': formatted_results
            }
            
        except Exception as e:
            cur.close()
            conn.close()
            raise Exception(f"Search query failed: {str(e)}")
    
    def get_search_history(self, user_email: str, limit: int = 10) -> List[Dict]:
        """Get recent search history"""
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT DISTINCT query, MAX(timestamp) as last_searched
                FROM search_history
                WHERE user_email = %s
                GROUP BY query
                ORDER BY MAX(timestamp) DESC
                LIMIT %s
            """, (user_email, limit))
            
            results = cur.fetchall()
            cur.close()
            conn.close()
            
            return [
                {
                    'query': r['query'],
                    'last_searched': r['last_searched'].isoformat() if r['last_searched'] else None
                }
                for r in results
            ]
        except:
            return []
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict]:
        """Get popular searches"""
        try:
            conn = self.get_db_connection()
            cur = conn.cursor()
            
            cur.execute("""
                SELECT query, COUNT(*) as search_count
                FROM search_history
                WHERE timestamp > NOW() - INTERVAL '7 days'
                GROUP BY query
                ORDER BY search_count DESC
                LIMIT %s
            """, (limit,))
            
            results = cur.fetchall()
            cur.close()
            conn.close()
            
            return [
                {
                    'query': r['query'],
                    'count': r['search_count']
                }
                for r in results
            ]
        except:
            return []

# Test the search
if __name__ == "__main__":
    search = FixedSearchSystem()
    
    print("Testing search for 'oil'...")
    try:
        results = search.search_suppliers("oil", limit=10)
        print(f"Found {results['total_results']} results")
        print(f"Execution time: {results['execution_time_ms']}ms")
        
        if results['results']:
            print("\nFirst result:")
            first = results['results'][0]
            print(f"  {first['supplier_name']} ({first['country']})")
            print(f"  Products: {first['product_preview'][:100]}...")
    except Exception as e:
        print(f"Search failed: {e}")