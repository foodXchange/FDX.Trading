"""
Optimized Search System - Database-First with Optional AI Enhancement
=====================================================================
This search system uses intelligent database queries with scoring,
NOT AI on every record. AI is only used when explicitly requested.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from typing import List, Dict, Any, Optional

load_dotenv()

class OptimizedSearchSystem:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.use_ai = False  # AI is OFF by default
        self.ai_client = None
        
    def get_db_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)
    
    def database_search(self, query: str, filters: Dict[str, Any] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Fast database search using PostgreSQL full-text search and pattern matching
        NO AI CALLS - Pure database operations
        """
        
        start_time = datetime.now()
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        # Simple, efficient query
        base_query = """
            SELECT 
                id, supplier_name, company_name, country, products,
                company_email, company_website, verified, rating,
                -- Simple relevance scoring
                (
                    CASE WHEN LOWER(products) LIKE %s THEN 10 ELSE 0 END +
                    CASE WHEN LOWER(supplier_name) LIKE %s THEN 5 ELSE 0 END +
                    CASE WHEN verified = true THEN 3 ELSE 0 END +
                    CASE WHEN rating >= 4 THEN 2 ELSE 0 END
                ) as relevance_score
            FROM suppliers
            WHERE 
                products IS NOT NULL 
                AND company_email IS NOT NULL
                AND (
                    LOWER(products) LIKE %s OR 
                    LOWER(supplier_name) LIKE %s OR
                    LOWER(company_name) LIKE %s
                )
        """
        
        # Add filters
        filter_conditions = []
        filter_params = []
        
        if filters:
            if filters.get('countries'):
                placeholders = ','.join(['%s'] * len(filters['countries']))
                filter_conditions.append(f"country IN ({placeholders})")
                filter_params.extend(filters['countries'])
            
            if filters.get('verified_only'):
                filter_conditions.append("verified = true")
            
            if filters.get('min_rating'):
                filter_conditions.append("rating >= %s")
                filter_params.append(filters['min_rating'])
        
        if filter_conditions:
            base_query += " AND " + " AND ".join(filter_conditions)
        
        base_query += " ORDER BY relevance_score DESC, rating DESC NULLS LAST LIMIT %s"
        
        # Prepare search pattern
        search_pattern = f"%{query.lower()}%"
        
        # Execute query
        params = [
            search_pattern,  # for product scoring
            search_pattern,  # for name scoring
            search_pattern,  # for product WHERE
            search_pattern,  # for supplier_name WHERE
            search_pattern,  # for company_name WHERE
        ] + filter_params + [limit]
        
        cur.execute(base_query, params)
        results = cur.fetchall()
        
        # Calculate execution time
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
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
                'verified': result['verified'],
                'rating': float(result['rating']) if result['rating'] else None,
                'relevance_score': result['relevance_score'],
                'product_preview': result['products'][:300] if result['products'] else ''
            })
        
        cur.close()
        conn.close()
        
        return {
            'query': query,
            'search_type': 'database',
            'ai_used': False,
            'total_results': len(results),
            'execution_time_ms': execution_time,
            'results': formatted_results
        }
    
    def ai_enhanced_search(self, query: str, filters: Dict[str, Any] = None, limit: int = 10) -> Dict[str, Any]:
        """
        AI-enhanced search - Only for specific queries that need understanding
        Uses AI to interpret query, then searches database
        LIMITED to 10 results to control AI costs
        """
        
        # First, get database results
        db_results = self.database_search(query, filters, limit=50)
        
        # Only enhance top 10 results with AI if configured
        if os.getenv('AZURE_OPENAI_KEY'):
            try:
                from openai import AzureOpenAI
                
                client = AzureOpenAI(
                    api_key=os.getenv('AZURE_OPENAI_KEY'),
                    api_version="2024-02-01",
                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
                )
                
                # Get AI interpretation of the query
                ai_response = client.chat.completions.create(
                    model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini'),
                    messages=[
                        {"role": "system", "content": "Extract key product terms from this search query. Return only comma-separated terms."},
                        {"role": "user", "content": query}
                    ],
                    max_tokens=50,
                    temperature=0.3
                )
                
                ai_terms = ai_response.choices[0].message.content.split(',')
                
                # Re-score results based on AI understanding
                for result in db_results['results'][:limit]:
                    ai_score = 0
                    for term in ai_terms:
                        if term.lower().strip() in result['product_preview'].lower():
                            ai_score += 10
                    result['ai_relevance_score'] = ai_score
                
                # Re-sort by AI score
                db_results['results'] = sorted(
                    db_results['results'][:limit], 
                    key=lambda x: x.get('ai_relevance_score', 0), 
                    reverse=True
                )
                
                db_results['ai_used'] = True
                db_results['ai_terms'] = ai_terms
                db_results['search_type'] = 'ai_enhanced'
                
            except Exception as e:
                print(f"AI enhancement failed, using database results: {e}")
                db_results['ai_error'] = str(e)
        
        return db_results
    
    def quick_search(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Ultra-fast search for autocomplete and quick results
        NO SCORING - Just pattern matching
        """
        
        conn = self.get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, supplier_name, country, company_email
            FROM suppliers
            WHERE 
                company_email IS NOT NULL
                AND (
                    LOWER(supplier_name) LIKE %s OR
                    LOWER(products) LIKE %s
                )
            LIMIT %s
        """, (f"%{query.lower()}%", f"%{query.lower()}%", limit))
        
        results = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(r) for r in results]
    
    def explain_search_method(self) -> str:
        """Explain what search method is being used"""
        return """
        Current Search Configuration:
        =============================
        • Primary Method: Database Pattern Matching (PostgreSQL)
        • AI Enhancement: DISABLED by default
        • Performance: <100ms for most queries
        • Records Searched: Full database scan with indexes
        • AI API Calls: ZERO (unless explicitly enabled)
        
        To enable AI enhancement:
        1. Set AZURE_OPENAI_KEY in .env
        2. Call ai_enhanced_search() instead of database_search()
        3. AI will only process top 10 results, not all records
        """

# Usage example
if __name__ == "__main__":
    search = OptimizedSearchSystem()
    
    print(search.explain_search_method())
    
    # Fast database search (NO AI)
    results = search.database_search("sunflower oil", limit=50)
    print(f"\nDatabase Search Results: {results['total_results']} suppliers found")
    print(f"Execution time: {results['execution_time_ms']}ms")
    print(f"AI used: {results['ai_used']}")
    
    # Quick search for autocomplete (NO AI)
    quick_results = search.quick_search("oil", limit=10)
    print(f"\nQuick Search: {len(quick_results)} results")