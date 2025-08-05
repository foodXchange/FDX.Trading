#!/usr/bin/env python3
"""
Multi-Method Search System
Combines PostgreSQL full-text search, AI analysis, and smart filters
Phase 2: Smart Features Implementation
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from openai import AzureOpenAI
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import hashlib

load_dotenv()

# Azure OpenAI configuration
client = AzureOpenAI(
    api_key="4mSTbyKUOviCB5cxUXY7xKveMTmeRqozTJSmW61MkJzSknM8YsBLJQQJ99BDACYeBjFXJ3w3AAAAACOGtOUz",
    api_version="2024-02-01",
    azure_endpoint="https://foodzxaihub2ea6656946887.cognitiveservices.azure.com/"
)

class MultiMethodSearch:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.search_history = []
        
    def analyze_query_intent(self, query: str) -> Dict:
        """AI-powered query analysis for better understanding"""
        prompt = f"""
        Analyze this supplier search query: "{query}"
        
        Extract:
        1. Product categories (e.g., oils, pasta, dairy)
        2. Specific requirements (organic, gluten-free, etc.)
        3. Packaging preferences (bottles, bulk, etc.)
        4. Quality indicators (premium, certified, etc.)
        5. Search strategy (broad or specific)
        
        Return JSON:
        {{
            "categories": ["product categories"],
            "requirements": ["specific requirements"],
            "packaging": ["packaging types"],
            "quality": ["quality indicators"],
            "strategy": "broad" or "specific",
            "keywords": ["key search terms"]
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
            # Fallback to simple keyword extraction
            return {
                "categories": [],
                "requirements": [],
                "packaging": [],
                "quality": [],
                "strategy": "broad",
                "keywords": query.lower().split()
            }
    
    def text_search(self, keywords: List[str], limit: int = 200) -> List[Dict]:
        """PostgreSQL full-text search using indexes"""
        if not keywords:
            return []
            
        # Build query using full-text search
        query_text = ' '.join(keywords)
        
        query = """
            SELECT id, supplier_name, company_name, country, products, 
                   supplier_type, company_email, company_website,
                   ts_rank(to_tsvector('english', products), 
                          plainto_tsquery('english', %s)) as text_score
            FROM suppliers
            WHERE to_tsvector('english', products) @@ plainto_tsquery('english', %s)
            ORDER BY text_score DESC
            LIMIT %s
        """
        
        self.cursor.execute(query, [query_text, query_text, limit])
        return self.cursor.fetchall()
    
    def keyword_search(self, keywords: List[str], limit: int = 200) -> List[Dict]:
        """Traditional keyword search as backup"""
        if not keywords:
            return []
            
        conditions = []
        params = []
        
        for keyword in keywords:
            conditions.append("""
                (LOWER(products) LIKE %s OR 
                 LOWER(supplier_name) LIKE %s OR 
                 LOWER(supplier_type) LIKE %s)
            """)
            kw = f'%{keyword.lower()}%'
            params.extend([kw, kw, kw])
        
        query = f"""
            SELECT id, supplier_name, company_name, country, products, 
                   supplier_type, company_email, company_website
            FROM suppliers
            WHERE {' OR '.join(conditions)}
            AND products IS NOT NULL
            LIMIT %s
        """
        params.append(limit)
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def apply_smart_filters(self, suppliers: List[Dict], intent: Dict) -> List[Dict]:
        """Apply intelligent filtering based on query intent"""
        filtered = []
        
        for supplier in suppliers:
            score_boost = 0
            products_lower = (supplier.get('products', '') or '').lower()
            type_lower = (supplier.get('supplier_type', '') or '').lower()
            
            # Check requirements
            for req in intent.get('requirements', []):
                if req.lower() in products_lower:
                    score_boost += 20
            
            # Check packaging
            for pkg in intent.get('packaging', []):
                if pkg.lower() in products_lower:
                    score_boost += 15
            
            # Check quality indicators
            for quality in intent.get('quality', []):
                if quality.lower() in products_lower or quality.lower() in type_lower:
                    score_boost += 10
            
            # Category matching
            for category in intent.get('categories', []):
                if category.lower() in products_lower or category.lower() in type_lower:
                    score_boost += 25
            
            supplier['filter_score'] = score_boost
            filtered.append(supplier)
        
        # Sort by filter score
        filtered.sort(key=lambda x: x.get('filter_score', 0), reverse=True)
        
        return filtered
    
    def hybrid_scoring(self, supplier: Dict, query: str, intent: Dict) -> Dict:
        """Combine multiple scoring methods"""
        
        # Base scores
        text_score = supplier.get('text_score', 0) * 100 if 'text_score' in supplier else 50
        filter_score = supplier.get('filter_score', 0)
        
        # If no filter score, give a base score of 50
        if filter_score == 0 and text_score > 0:
            filter_score = 50
        
        # Calculate final score - prioritize text relevance
        if text_score > 0:
            final_score = min(100, text_score * 0.7 + filter_score * 0.3)
        else:
            final_score = filter_score
        
        # Build match explanation
        strengths = []
        if text_score > 70:
            strengths.append("High text relevance")
        if filter_score > 40:
            strengths.append("Matches specific requirements")
        if supplier.get('country') in ['Italy', 'Spain', 'France', 'Germany']:
            strengths.append(f"Premium supplier from {supplier['country']}")
        if supplier.get('company_website'):
            strengths.append("Has website for direct contact")
        
        return {
            'final_score': round(final_score),
            'text_relevance': round(text_score),
            'requirement_match': filter_score,
            'strengths': strengths
        }
    
    def multi_method_search(self, 
                           query: str,
                           countries: Optional[List[str]] = None,
                           supplier_types: Optional[List[str]] = None,
                           use_ai_analysis: bool = True,
                           limit: int = 25) -> Dict:
        """
        Main multi-method search combining all techniques
        """
        
        start_time = datetime.now()
        
        # Step 1: Analyze query intent
        if use_ai_analysis:
            print(f"Analyzing query: '{query}'...")
            intent = self.analyze_query_intent(query)
        else:
            intent = {"keywords": query.lower().split(), "strategy": "broad"}
        
        # Step 2: Text search (primary method)
        print("Performing full-text search...")
        text_results = self.text_search(intent.get('keywords', query.split()))
        
        # Step 3: Keyword search (fallback/supplement)
        if len(text_results) < 50:
            print("Supplementing with keyword search...")
            keyword_results = self.keyword_search(intent.get('keywords', query.split()))
            # Merge results (avoiding duplicates)
            seen_ids = {r['id'] for r in text_results}
            for r in keyword_results:
                if r['id'] not in seen_ids:
                    text_results.append(r)
        
        # Step 4: Apply smart filters
        print("Applying smart filters...")
        filtered_results = self.apply_smart_filters(text_results, intent)
        
        # Step 5: Apply country/type filters if specified
        if countries:
            filtered_results = [s for s in filtered_results 
                              if s.get('country') in countries]
        
        if supplier_types:
            filtered_results = [s for s in filtered_results 
                              if any(st.lower() in (s.get('supplier_type', '') or '').lower() 
                                    for st in supplier_types)]
        
        # Step 6: Hybrid scoring
        print("Calculating final scores...")
        scored_results = []
        for supplier in filtered_results[:limit * 2]:  # Score more than needed
            scores = self.hybrid_scoring(supplier, query, intent)
            supplier.update({
                'ai_score': scores['final_score'],
                'text_relevance': scores['text_relevance'],
                'requirement_match': scores['requirement_match'],
                'strengths': scores['strengths'],
                'match_reason': f"Text: {scores['text_relevance']}%, Requirements: {scores['requirement_match']}%"
            })
            
            if scores['final_score'] > 10:  # Lower threshold for better results
                scored_results.append(supplier)
        
        # Step 7: Final sorting and limiting
        scored_results.sort(key=lambda x: x['ai_score'], reverse=True)
        final_results = scored_results[:limit]
        
        # Step 8: Track search for analytics
        search_time = (datetime.now() - start_time).total_seconds()
        self.track_search(query, len(final_results), search_time)
        
        return {
            'success': True,
            'query': query,
            'intent': intent,
            'filters': {
                'countries': countries or [],
                'supplier_types': supplier_types or []
            },
            'suppliers': final_results,
            'total_found': len(text_results),
            'filtered_count': len(filtered_results),
            'final_count': len(final_results),
            'search_time': round(search_time, 3),
            'search_method': 'Multi-method (Text + AI + Filters)'
        }
    
    def track_search(self, query: str, results_count: int, search_time: float):
        """Track search for history and analytics"""
        search_record = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results_count': results_count,
            'search_time': search_time,
            'query_hash': hashlib.md5(query.encode()).hexdigest()
        }
        
        self.search_history.append(search_record)
        
        # Save to database (optional)
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    query TEXT,
                    results_count INTEGER,
                    search_time FLOAT,
                    query_hash VARCHAR(32)
                )
            """)
            
            self.cursor.execute("""
                INSERT INTO search_history (query, results_count, search_time, query_hash)
                VALUES (%s, %s, %s, %s)
            """, (query, results_count, search_time, search_record['query_hash']))
            
            self.conn.commit()
        except:
            self.conn.rollback()
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on history"""
        try:
            self.cursor.execute("""
                SELECT DISTINCT query 
                FROM search_history 
                WHERE LOWER(query) LIKE %s
                AND results_count > 0
                ORDER BY timestamp DESC
                LIMIT 5
            """, (f'{partial_query.lower()}%',))
            
            return [row['query'] for row in self.cursor.fetchall()]
        except:
            return []
    
    def close(self):
        self.cursor.close()
        self.conn.close()


# Convenience function for quick multi-method search
def smart_search(query: str, **kwargs):
    """
    Quick multi-method search with all enhancements
    
    Examples:
    - smart_search("organic olive oil")
    - smart_search("pasta", countries=["Italy"])
    - smart_search("sunflower oil 1L bottles", use_ai_analysis=True)
    """
    
    searcher = MultiMethodSearch()
    
    try:
        results = searcher.multi_method_search(query, **kwargs)
        
        print(f"\n{'='*80}")
        print(f"SMART SEARCH RESULTS (Multi-Method)")
        print(f"Query: {results['query']}")
        print(f"Method: {results['search_method']}")
        print(f"Time: {results['search_time']}s")
        print(f"Results: {results['final_count']} suppliers (from {results['total_found']} total)")
        
        if results.get('intent', {}).get('categories'):
            print(f"Categories: {', '.join(results['intent']['categories'])}")
        if results.get('intent', {}).get('requirements'):
            print(f"Requirements: {', '.join(results['intent']['requirements'])}")
        
        print(f"{'='*80}")
        
        for i, supplier in enumerate(results['suppliers'][:10], 1):
            print(f"\n{i}. {supplier['supplier_name']} ({supplier['country']})")
            print(f"   Score: {supplier['ai_score']}/100 | Match: {supplier['match_reason']}")
            print(f"   Type: {supplier['supplier_type']}")
            
            if supplier.get('strengths'):
                print(f"   Strengths: {', '.join(supplier['strengths'][:3])}")
            
            if supplier.get('company_email'):
                print(f"   Contact: {supplier['company_email']}")
            
            print(f"   Products: {supplier['products'][:120]}...")
        
        return results
        
    finally:
        searcher.close()


if __name__ == "__main__":
    print("Multi-Method Search System Ready!")
    print("="*50)
    print("Features:")
    print("- AI query analysis")
    print("- PostgreSQL full-text search")
    print("- Smart filtering")
    print("- Hybrid scoring")
    print("- Search history tracking")
    print("\nTry: smart_search('your product query')")