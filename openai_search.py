#!/usr/bin/env python3
"""
OpenAI-Powered Search for FDX.trading
Uses Azure OpenAI to understand complex natural language queries
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configure Azure OpenAI
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"

class OpenAISearch:
    def __init__(self):
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        self.db_url = os.getenv("DATABASE_URL")
    
    def understand_query(self, user_query: str) -> dict:
        """Use OpenAI to understand what the user is looking for"""
        
        prompt = f"""
        Analyze this supplier search query and extract the requirements:
        Query: "{user_query}"
        
        Extract and return as JSON:
        1. products: Main products being searched (list)
        2. specifications: Specific requirements like size, packaging, quantity (list)
        3. countries: Preferred countries if mentioned (list)
        4. quality_requirements: Certifications, standards, quality needs (list)
        5. business_requirements: MOQ, pricing, delivery terms if mentioned (list)
        6. search_keywords: Important keywords to search in database (list)
        
        Be thorough and extract ALL relevant information.
        Return ONLY valid JSON.
        """
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a B2B food trade expert helping find suppliers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the response
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Fallback to basic parsing
            return {
                "products": user_query.split()[:3],
                "search_keywords": user_query.split()
            }
    
    def score_supplier_with_ai(self, supplier_data: dict, requirements: dict, user_query: str) -> float:
        """Use AI to score how well a supplier matches the requirements"""
        
        prompt = f"""
        Score this supplier for the query: "{user_query}"
        
        Requirements extracted:
        {json.dumps(requirements, indent=2)}
        
        Supplier:
        Name: {supplier_data.get('supplier_name')}
        Country: {supplier_data.get('country')}
        Products: {supplier_data.get('products', '')[:500]}
        Type: {supplier_data.get('supplier_type')}
        
        Score from 0-100 based on:
        - Product match (40%)
        - Specifications match (30%)
        - Country preference (20%)
        - Overall fit (10%)
        
        Return ONLY a number between 0-100.
        """
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a supplier matching expert. Return only a number."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            # Extract number from response
            import re
            numbers = re.findall(r'\d+', score_text)
            if numbers:
                return min(100, max(0, float(numbers[0])))
            return 50.0
            
        except:
            # Fallback scoring
            score = 0
            products_lower = (supplier_data.get('products', '') or '').lower()
            
            # Basic keyword matching
            for keyword in requirements.get('search_keywords', []):
                if keyword.lower() in products_lower:
                    score += 20
            
            # Country match
            if supplier_data.get('country') in requirements.get('countries', []):
                score += 30
            
            return min(100, score)
    
    def search_with_ai(self, user_query: str, limit: int = 50) -> dict:
        """Main search function using OpenAI"""
        
        start_time = datetime.now()
        
        # Step 1: Understand the query with AI
        print(f"Analyzing query with AI: {user_query}")
        requirements = self.understand_query(user_query)
        print(f"Understood requirements: {requirements}")
        
        # Step 2: Database search with extracted keywords
        conn = psycopg2.connect(self.db_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Build search query
        search_terms = requirements.get('search_keywords', []) + requirements.get('products', [])
        
        if search_terms:
            # Create OR conditions for all search terms
            conditions = []
            params = []
            
            for term in search_terms[:5]:  # Limit to 5 terms for performance
                conditions.append("(LOWER(products) LIKE %s OR LOWER(supplier_name) LIKE %s)")
                params.extend([f"%{term.lower()}%", f"%{term.lower()}%"])
            
            where_clause = " OR ".join(conditions)
            
            query = f"""
                SELECT id, supplier_name, company_name, country, products,
                       company_email, company_website, supplier_type, verified, rating
                FROM suppliers
                WHERE {where_clause}
                LIMIT 200
            """
            
            cursor.execute(query, params)
        else:
            # Fallback to simple search
            cursor.execute("""
                SELECT id, supplier_name, company_name, country, products,
                       company_email, company_website, supplier_type, verified, rating
                FROM suppliers
                WHERE products IS NOT NULL
                LIMIT 200
            """)
        
        raw_results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Step 3: Score each supplier with AI
        print(f"Scoring {len(raw_results)} suppliers with AI...")
        scored_results = []
        
        for supplier in raw_results[:limit]:  # Limit AI scoring for performance
            ai_score = self.score_supplier_with_ai(supplier, requirements, user_query)
            
            scored_results.append({
                'supplier_id': supplier['id'],
                'supplier_name': supplier['supplier_name'],
                'company_name': supplier['company_name'] or supplier['supplier_name'],
                'country': supplier['country'] or 'Unknown',
                'email': supplier['company_email'] or '',
                'website': supplier['company_website'] or '',
                'products': supplier['products'] or '',
                'product_preview': (supplier['products'] or '')[:300],
                'supplier_type': supplier['supplier_type'] or '',
                'verified': supplier.get('verified', False),
                'rating': float(supplier['rating']) if supplier.get('rating') else None,
                'ai_score': ai_score,
                'match_percentage': ai_score
            })
        
        # Sort by AI score
        scored_results.sort(key=lambda x: x['ai_score'], reverse=True)
        
        # Add rank
        for idx, result in enumerate(scored_results, 1):
            result['rank'] = idx
        
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            'query': user_query,
            'ai_understanding': requirements,
            'total_results': len(scored_results),
            'execution_time_ms': int(execution_time),
            'timestamp': datetime.now().isoformat(),
            'results': scored_results[:limit]
        }

# FastAPI endpoint
async def ai_search_endpoint(request):
    """FastAPI endpoint for AI search"""
    from fastapi.responses import JSONResponse
    
    try:
        data = await request.json()
        query = data.get('query', '')
        
        if not query:
            return JSONResponse(
                content={"error": "No query provided", "results": []},
                status_code=400
            )
        
        searcher = OpenAISearch()
        results = searcher.search_with_ai(query)
        
        return JSONResponse(
            content=results,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "results": []},
            status_code=500
        )

if __name__ == "__main__":
    # Test the AI search
    load_dotenv()
    
    searcher = OpenAISearch()
    
    # Test complex query
    query = "sunflower oil in 1L plastic bottles from Italy or Spain, must be refined, good for frying"
    
    print(f"Testing query: {query}")
    results = searcher.search_with_ai(query, limit=10)
    
    print(f"\nFound {results['total_results']} results")
    print(f"AI Understanding: {json.dumps(results['ai_understanding'], indent=2)}")
    
    if results['results']:
        print("\nTop 3 matches:")
        for r in results['results'][:3]:
            print(f"\n{r['rank']}. {r['supplier_name']} ({r['country']})")
            print(f"   AI Score: {r['ai_score']:.1f}%")
            print(f"   Products: {r['product_preview'][:100]}...")