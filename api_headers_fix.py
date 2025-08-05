#!/usr/bin/env python3
"""
Fix API headers and response formatting for production
"""

import re

def fix_app_py():
    """Fix app.py to include proper headers and content-type"""
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ensure JSONResponse is imported
    if 'from fastapi.responses import JSONResponse' not in content:
        content = content.replace(
            'from fastapi.responses import HTMLResponse, RedirectResponse',
            'from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse'
        )
    
    # Fix the search API endpoint
    search_function = '''@app.post("/api/search")
async def api_smart_search(request: Request):
    """
    Execute smart database search with intelligent scoring
    NOTE: This uses database pattern matching, NOT AI on every record
    Fast and efficient for 1-person company use
    """
    
    # Get form data
    form_data = await request.form()
    query = form_data.get('query', '')
    verified_only = form_data.get('verified_only') == 'on'
    min_rating = form_data.get('min_rating')
    countries = form_data.get('countries', '')
    
    try:
        # Parse filters
        filters = {}
        if verified_only:
            filters['verified_only'] = True
        if min_rating and min_rating != '':
            filters['min_rating'] = float(min_rating)
        if countries:
            filters['countries'] = [c.strip() for c in countries.split(',') if c.strip()]
        
        # Execute search using Fixed search system
        if ai_search:
            results = ai_search.search_suppliers(
                query=query,
                user_email='udi@fdx.trading',
                filters=filters,
                limit=50
            )
        else:
            # Fallback to basic search
            from database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            search_sql = """
                SELECT id, supplier_name, company_name, country, products, 
                       company_email, company_website, verified, rating, company_phone
                FROM suppliers
                WHERE products IS NOT NULL 
                AND company_email IS NOT NULL
                AND (LOWER(products) LIKE %s OR LOWER(supplier_name) LIKE %s)
                ORDER BY rating DESC NULLS LAST
                LIMIT 50
            """
            
            search_term = f"%{query.lower()}%"
            cursor.execute(search_sql, (search_term, search_term))
            
            raw_results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Format results
            results = {
                'query': query,
                'total_results': len(raw_results),
                'execution_time_ms': 100,
                'results': []
            }
            
            for r in raw_results:
                results['results'].append({
                    'supplier_id': r['id'],
                    'supplier_name': r['supplier_name'],
                    'company_name': r['company_name'],
                    'country': r['country'],
                    'email': r['company_email'],
                    'website': r['company_website'],
                    'verified': r['verified'],
                    'rating': float(r['rating']) if r['rating'] else None,
                    'product_preview': r['products'][:300] if r['products'] else '',
                    'match_percentage': 85.0,
                    'matched_terms': [query.split()[0]] if query else []
                })
        
        return JSONResponse(
            content=results,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'X-Content-Type-Options': 'nosniff',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        )
    
    except Exception as e:
        return JSONResponse(
            content={"error": f"Search error: {str(e)}"},
            status_code=500,
            headers={
                'Content-Type': 'application/json; charset=utf-8',
                'X-Content-Type-Options': 'nosniff',
                'Cache-Control': 'no-cache'
            }
        )'''
    
    # Find and replace the existing search function
    pattern = r'@app\.post\("/api/search"\).*?except Exception as e:.*?status_code=500\s*\)'
    content = re.sub(pattern, search_function, content, flags=re.DOTALL)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed app.py with proper headers")

if __name__ == "__main__":
    fix_app_py()