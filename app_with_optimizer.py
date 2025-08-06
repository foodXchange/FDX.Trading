#!/usr/bin/env python3
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# Import the optimizer
import sys
sys.path.append('/home/fdxfounder/fdx/app')
try:
    from optimize_product_search import ProductSearchOptimizer
    optimizer_available = True
except:
    optimizer_available = False

load_dotenv()

app = FastAPI(
    title="FDX.trading",
    description="B2B Food Trading Platform with Optimized Search",
    version="2.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_db_connection():
    """Get database connection with proper error handling"""
    try:
        conn = psycopg2.connect(
            os.getenv('DATABASE_URL'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse(url="/suppliers", status_code=303)

@app.get("/suppliers", response_class=HTMLResponse)
async def suppliers_page(request: Request):
    """Suppliers search page"""
    try:
        return templates.TemplateResponse("suppliers.html", {
            "request": request,
            "user_email": "udi@fdx.trading"
        })
    except:
        # Return the fixed template
        return HTMLResponse(content=open("suppliers_fixed.html").read())

@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    """Projects page with proper error handling"""
    try:
        conn = get_db_connection()
        if not conn:
            raise Exception("Database connection failed")
        
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                project_name VARCHAR(255) NOT NULL,
                description TEXT,
                user_email VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_suppliers (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                supplier_id INTEGER,
                supplier_name VARCHAR(255),
                supplier_country VARCHAR(100),
                supplier_email VARCHAR(255),
                score INTEGER DEFAULT 0,
                products TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        
        # Get projects
        cursor.execute("""
            SELECT p.id, p.project_name, p.description, p.created_at,
                   COUNT(ps.id) as supplier_count
            FROM projects p
            LEFT JOIN project_suppliers ps ON p.id = ps.project_id
            WHERE p.user_email = %s
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """, ('udi@fdx.trading',))
        
        projects = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Return simple HTML
        projects_html = ""
        for p in projects:
            projects_html += f"""
            <div class="card mb-3">
                <div class="card-body">
                    <h5>{p['project_name']}</h5>
                    <p>{p['description'] or 'No description'}</p>
                    <p>{p['supplier_count']} suppliers</p>
                    <a href="/project_details?id={p['id']}" class="btn btn-primary">View</a>
                </div>
            </div>
            """
        
        if not projects_html:
            projects_html = '<p class="text-muted">No projects yet. Search for suppliers and add them to a project.</p>'
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Projects - FDX.trading</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar navbar-dark bg-primary">
                <div class="container-fluid">
                    <a class="navbar-brand" href="/">FDX.trading</a>
                    <div class="navbar-nav ms-auto">
                        <a class="nav-link" href="/suppliers">Search</a>
                        <a class="nav-link active" href="/projects">Projects</a>
                    </div>
                </div>
            </nav>
            <div class="container mt-4">
                <h2>My Projects</h2>
                {projects_html}
            </div>
        </body>
        </html>
        """)
        
    except Exception as e:
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error - FDX.trading</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <nav class="navbar navbar-dark bg-primary">
                <div class="container-fluid">
                    <a class="navbar-brand" href="/">FDX.trading</a>
                </div>
            </nav>
            <div class="container mt-4">
                <div class="alert alert-danger">
                    <h4>Database Error</h4>
                    <p>Unable to load projects. Please try again.</p>
                    <div class="mt-3 p-3 bg-light">
                        <strong>Error:</strong> {str(e)}
                    </div>
                </div>
                <a href="/suppliers" class="btn btn-primary">Go to Search</a>
            </div>
        </body>
        </html>
        """)

@app.post("/api/search")
async def api_search(request: Request):
    """Optimized search API that excludes suppliers who use products as ingredients"""
    try:
        form_data = await request.form()
        query = form_data.get('query', '')
        
        if not query:
            return JSONResponse(
                content={"error": "No search query provided", "results": []},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        # Try to use optimizer if available
        if optimizer_available:
            try:
                optimizer = ProductSearchOptimizer()
                optimized_results = optimizer.optimize_search(query, limit=100)
                
                # Return optimized results
                return JSONResponse(
                    content={
                        'query': query,
                        'total_results': optimized_results['total_sellers'],
                        'message': f"Found {optimized_results['total_sellers']} suppliers who SELL {query} (excluded {optimized_results['total_users']} who use it as ingredient)",
                        'results': optimized_results['sellers']
                    },
                    headers={"Content-Type": "application/json; charset=utf-8"}
                )
            except Exception as opt_error:
                print(f"Optimizer error, falling back: {opt_error}")
        
        # Fallback to regular search if optimizer not available
        conn = get_db_connection()
        if not conn:
            return JSONResponse(
                content={"error": "Database connection failed", "results": []},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        cursor = conn.cursor()
        
        # Search for suppliers with classification preference
        search_term = f"%{query.lower()}%"
        cursor.execute("""
            SELECT id, supplier_name, company_name, country, products,
                   company_email as email, company_website as website,
                   verified, rating, product_classification
            FROM suppliers
            WHERE (LOWER(supplier_name) LIKE %s
               OR LOWER(products) LIKE %s
               OR LOWER(company_name) LIKE %s)
               AND (product_classification != 'user' OR product_classification IS NULL)
            ORDER BY 
                CASE 
                    WHEN product_classification = 'seller' THEN 1
                    WHEN product_classification IS NULL THEN 2
                    ELSE 3
                END,
                rating DESC NULLS LAST
            LIMIT 100
        """, (search_term, search_term, search_term))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format results
        formatted_results = []
        for r in results:
            formatted_results.append({
                'supplier_id': r['id'],
                'supplier_name': r['supplier_name'],
                'company_name': r['company_name'] or r['supplier_name'],
                'country': r['country'] or 'Unknown',
                'email': r['email'] or '',
                'website': r['website'] or '',
                'verified': r.get('verified', False),
                'rating': float(r['rating']) if r.get('rating') else 0,
                'product_preview': r['products'][:300] if r.get('products') else '',
                'match_percentage': 85.0,
                'classification': r.get('product_classification', 'unknown')
            })
        
        # Filter out known users
        sellers_only = [r for r in formatted_results if r['classification'] != 'user']
        
        return JSONResponse(
            content={
                'query': query,
                'total_results': len(sellers_only),
                'results': sellers_only
            },
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Cache-Control": "no-cache"
            }
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "results": []},
            status_code=500,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "optimizer": "enabled" if optimizer_available else "disabled",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)