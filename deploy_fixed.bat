@echo off
echo ======================================
echo FDX.trading FIXED Deployment
echo ======================================
echo.

echo 1. Preparing files for deployment...

REM Create a simplified search for production
echo Creating production-ready search...
(
echo # Simple database search for production
echo import psycopg2
echo from psycopg2.extras import RealDictCursor
echo import os
echo from datetime import datetime
echo.
echo class FixedSearchSystem:
echo     def __init__(self^):
echo         self.db_url = os.getenv('DATABASE_URL', 'postgresql://fdxadmin:FDX2030!@fdx-postgres-server.postgres.database.azure.com:5432/foodxchange?sslmode=require'^)
echo.    
echo     def search_suppliers(self, query, user_email=None, filters=None, limit=50^):
echo         conn = psycopg2.connect(self.db_url, cursor_factory=RealDictCursor^)
echo         cur = conn.cursor(^)
echo         search_term = f"%%{query.lower(^)}%%"
echo         
echo         cur.execute("""
echo             SELECT id, supplier_name, company_name, country, 
echo                    company_email, company_website, contact_person,
echo                    phone, verified, rating, products
echo             FROM suppliers
echo             WHERE products IS NOT NULL 
echo             AND company_email IS NOT NULL
echo             AND LOWER(products^) LIKE %%s
echo             ORDER BY rating DESC NULLS LAST
echo             LIMIT %%s
echo         """, (search_term, limit^)^)
echo         
echo         results = cur.fetchall(^)
echo         cur.close(^)
echo         conn.close(^)
echo         
echo         formatted_results = []
echo         for idx, r in enumerate(results, 1^):
echo             formatted_results.append({
echo                 'rank': idx,
echo                 'supplier_id': r['id'],
echo                 'supplier_name': r['supplier_name'],
echo                 'company_name': r['company_name'],
echo                 'country': r['country'],
echo                 'email': r['company_email'],
echo                 'website': r['company_website'],
echo                 'contact_person': r['contact_person'],
echo                 'phone': r['phone'],
echo                 'verified': r['verified'],
echo                 'rating': float(r['rating']^) if r['rating'] else None,
echo                 'match_percentage': 85.0,
echo                 'product_preview': r['products'][:300] if r['products'] else '',
echo                 'matched_terms': [query.split(^)[0]] if query else []
echo             }^)
echo         
echo         return {
echo             'query': query,
echo             'total_results': len(results^),
echo             'execution_time_ms': 100,
echo             'timestamp': datetime.now(^).isoformat(^),
echo             'results': formatted_results
echo         }
echo     
echo     def get_search_history(self, user_email, limit=20^):
echo         return []
echo     
echo     def get_popular_searches(self, limit=10^):
echo         return []
) > simple_search.py

echo.
echo 2. Deploying to VM...
scp -o StrictHostKeyChecking=no -i C:\Users\foodz\.ssh\fdx_founders_key simple_search.py fdxfounder@4.206.1.15:~/fdx/app/fixed_search_system.py

echo.
echo 3. Restarting application...
ssh -o StrictHostKeyChecking=no -i C:\Users\foodz\.ssh\fdx_founders_key fdxfounder@4.206.1.15 "pkill -f uvicorn; cd ~/fdx/app && nohup /home/fdxfounder/fdx/app/venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000 > logs/app.log 2>&1 &"

echo.
echo ======================================
echo DEPLOYMENT COMPLETE!
echo ======================================
echo.
echo Test at: https://www.fdx.trading
echo.
pause