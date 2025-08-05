#!/usr/bin/env python3
"""
Enhanced AI Search with Filters and Improved Scoring
Lean implementation building on existing search capabilities
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
from typing import List, Dict, Optional

load_dotenv()

# Azure OpenAI configuration
client = AzureOpenAI(
    api_key="4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz",
    api_version="2024-02-01",
    azure_endpoint="https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/"
)

class EnhancedSearch:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
    
    def search_with_filters(self, query: str, 
                           countries: Optional[List[str]] = None,
                           supplier_types: Optional[List[str]] = None,
                           limit: int = 50) -> List[Dict]:
        """
        Fast search using PostgreSQL indexes with optional filters
        """
        
        # Build base query using full-text search index
        base_query = """
            SELECT id, supplier_name, company_name, country, products, 
                   supplier_type, company_email, company_website,
                   ts_rank(to_tsvector('english', products), plainto_tsquery('english', %s)) as text_score
            FROM suppliers
            WHERE to_tsvector('english', products) @@ plainto_tsquery('english', %s)
        """
        
        params = [query, query]
        filters = []
        
        # Add country filter
        if countries:
            placeholders = ','.join(['%s'] * len(countries))
            filters.append(f"country = ANY(ARRAY[{placeholders}])")
            params.extend(countries)
        
        # Add supplier type filter
        if supplier_types:
            type_conditions = []
            for supplier_type in supplier_types:
                type_conditions.append("LOWER(supplier_type) LIKE %s")
                params.append(f'%{supplier_type.lower()}%')
            if type_conditions:
                filters.append(f"({' OR '.join(type_conditions)})")
        
        # Combine filters
        if filters:
            base_query += " AND " + " AND ".join(filters)
        
        # Order by text relevance and limit
        base_query += f" ORDER BY text_score DESC LIMIT {limit}"
        
        self.cursor.execute(base_query, params)
        return self.cursor.fetchall()
    
    def score_supplier_fast(self, supplier: Dict, query: str) -> Dict:
        """
        Fast scoring algorithm without AI (for quick results)
        """
        score = 50  # Base score
        products = (supplier['products'] or '').lower()
        query_lower = query.lower()
        
        # Text relevance scoring
        query_words = query_lower.split()
        matches = sum(1 for word in query_words if word in products)
        score += matches * 15
        
        # Exact phrase bonus
        if query_lower in products:
            score += 25
        
        # Country preference (example: prefer certain countries)
        preferred_countries = ['Italy', 'Spain', 'France', 'Germany']
        if supplier['country'] in preferred_countries:
            score += 10
        
        # Supplier type relevance
        if any(word in (supplier['supplier_type'] or '').lower() 
               for word in query_words):
            score += 15
        
        # Contact info bonus
        if supplier['company_email']:
            score += 5
        if supplier['company_website']:
            score += 5
        
        return {
            'score': min(score, 100),
            'text_matches': matches,
            'has_exact_phrase': query_lower in products
        }
    
    def enhanced_search(self, query: str,
                       countries: Optional[List[str]] = None,
                       supplier_types: Optional[List[str]] = None,
                       use_ai_scoring: bool = False,
                       limit: int = 20) -> Dict:
        """
        Main enhanced search function with filters and improved scoring
        """
        
        print(f"Searching for: '{query}'")
        if countries:
            print(f"Countries: {', '.join(countries)}")
        if supplier_types:
            print(f"Supplier types: {', '.join(supplier_types)}")
        
        # Get suppliers using indexed search with filters
        suppliers = self.search_with_filters(query, countries, supplier_types, limit * 3)
        print(f"Found {len(suppliers)} suppliers from database")
        
        # Score suppliers
        scored_suppliers = []
        for supplier in suppliers:
            if use_ai_scoring:
                # Use AI scoring (slower but more accurate)
                ai_result = self.ai_score_supplier(supplier, query)
                supplier['ai_score'] = ai_result['score']
                supplier['match_reasons'] = ai_result['reasons']
                supplier['strengths'] = ai_result['strengths']
                supplier['concerns'] = ai_result['concerns']
            else:
                # Use fast scoring algorithm
                fast_result = self.score_supplier_fast(supplier, query)
                supplier['ai_score'] = fast_result['score']
                supplier['text_matches'] = fast_result['text_matches']
                supplier['has_exact_phrase'] = fast_result['has_exact_phrase']
                supplier['match_reasons'] = [f"Found {fast_result['text_matches']} keyword matches"]
                supplier['strengths'] = [
                    f"Supplies products matching '{query}'",
                    f"Located in {supplier['country']}",
                    f"Text relevance score: {supplier['text_score']:.3f}"
                ]
                supplier['concerns'] = []
                
                if fast_result['has_exact_phrase']:
                    supplier['strengths'].append("Exact phrase match found")
            
            if supplier['ai_score'] > 40:  # Only keep relevant results
                scored_suppliers.append(supplier)
        
        # Sort by AI score
        scored_suppliers.sort(key=lambda x: x['ai_score'], reverse=True)
        
        return {
            'success': True,
            'query': query,
            'filters': {
                'countries': countries or [],
                'supplier_types': supplier_types or []
            },
            'suppliers': scored_suppliers[:limit],
            'total_found': len(suppliers),
            'scored_results': len(scored_suppliers),
            'search_method': 'AI scoring' if use_ai_scoring else 'Fast scoring'
        }
    
    def ai_score_supplier(self, supplier: Dict, query: str) -> Dict:
        """AI scoring for higher accuracy (slower)"""
        prompt = f"""
        Score this supplier for the query: "{query}" (0-100):
        
        Supplier: {supplier['supplier_name']} ({supplier['country']})
        Type: {supplier['supplier_type']}
        Products: {supplier['products'][:300]}
        
        Return JSON:
        {{
            "score": 0-100,
            "reasons": ["why it matches"],
            "strengths": ["key strengths"],
            "concerns": ["potential issues"]
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            return json.loads(content[content.find('{'):content.rfind('}')+1])
        except:
            return {"score": 50, "reasons": ["AI scoring failed"], "strengths": [], "concerns": []}
    
    def get_filter_options(self) -> Dict:
        """Get available filter options from database"""
        
        # Get top countries
        self.cursor.execute("""
            SELECT country, COUNT(*) as count 
            FROM suppliers 
            WHERE country IS NOT NULL 
            GROUP BY country 
            ORDER BY count DESC 
            LIMIT 20
        """)
        countries = [row['country'] for row in self.cursor.fetchall()]
        
        # Get common supplier types
        self.cursor.execute("""
            SELECT supplier_type, COUNT(*) as count 
            FROM suppliers 
            WHERE supplier_type IS NOT NULL 
            GROUP BY supplier_type 
            ORDER BY count DESC 
            LIMIT 15
        """)
        supplier_types = [row['supplier_type'] for row in self.cursor.fetchall()]
        
        return {
            'countries': countries,
            'supplier_types': supplier_types
        }
    
    def close(self):
        self.cursor.close()
        self.conn.close()


# Quick search function with filters
def enhanced_search_quick(query: str, 
                         countries: List[str] = None,
                         supplier_types: List[str] = None,
                         use_ai: bool = False,
                         limit: int = 15):
    """
    Quick enhanced search with filters
    
    Examples:
    - enhanced_search_quick("sunflower oil")
    - enhanced_search_quick("olive oil", countries=["Italy", "Spain"])
    - enhanced_search_quick("pasta", supplier_types=["Manufacturer"])
    """
    
    searcher = EnhancedSearch()
    
    try:
        results = searcher.enhanced_search(
            query=query,
            countries=countries,
            supplier_types=supplier_types,
            use_ai_scoring=use_ai,
            limit=limit
        )
        
        print(f"\n{'='*80}")
        print(f"ENHANCED SEARCH RESULTS")
        print(f"Query: {results['query']}")
        print(f"Method: {results['search_method']}")
        print(f"Results: {len(results['suppliers'])}/{results['total_found']} suppliers")
        print(f"{'='*80}")
        
        for i, supplier in enumerate(results['suppliers'], 1):
            print(f"\n{i}. {supplier['supplier_name']} ({supplier['country']})")
            print(f"   Score: {supplier['ai_score']}/100")
            print(f"   Type: {supplier['supplier_type']}")
            print(f"   Contact: {supplier['company_email']}")
            
            if supplier['strengths']:
                print(f"   Strengths:")
                for strength in supplier['strengths'][:3]:
                    print(f"   + {strength}")
            
            print(f"   Products: {supplier['products'][:150]}...")
            print("-" * 80)
        
        return results
        
    finally:
        searcher.close()


if __name__ == "__main__":
    print("Enhanced Search System Ready!")
    print("="*50)
    
    # Show available filters
    searcher = EnhancedSearch()
    try:
        filters = searcher.get_filter_options()
        print("Available filters:")
        print(f"Top countries: {', '.join(filters['countries'][:10])}")
        print(f"Supplier types: {', '.join(filters['supplier_types'][:5])}")
    finally:
        searcher.close()
    
    print("\nUsage examples:")
    print('enhanced_search_quick("sunflower oil")')
    print('enhanced_search_quick("pasta", countries=["Italy"])')
    print('enhanced_search_quick("oil", supplier_types=["Manufacturer"], use_ai=True)')