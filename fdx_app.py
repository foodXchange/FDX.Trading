"""
FDX Trading Application
Technologies: FastAPI, Bootstrap, Jinja2, Azure PostgreSQL, Azure AI
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv
import json

# Azure OpenAI for AI enhancements
import openai

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="FDX Trading System", version="1.0.0")

# Setup templates with Jinja2
templates = Jinja2Templates(directory="templates")

# Azure PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require")

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")

def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(DATABASE_URL)

def ai_enhance_search(query: str) -> str:
    """Use Azure AI to enhance search queries"""
    try:
        response = openai.ChatCompletion.create(
            deployment_id=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a food trading expert. Expand this search query to include related terms, synonyms, and variations. Return only a comma-separated list of search terms."},
                {"role": "user", "content": f"Expand search for: {query}"}
            ],
            max_tokens=100,
            temperature=0.3
        )
        return response.choices[0].message.content
    except:
        return query  # Fallback to original query if AI fails

def ai_match_suppliers(request_data: dict) -> List[dict]:
    """Use AI to intelligently match suppliers to requests"""
    try:
        response = openai.ChatCompletion.create(
            deployment_id=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a supply chain expert. Based on the request, identify the best matching criteria for suppliers."},
                {"role": "user", "content": f"Request: {json.dumps(request_data)}. What supplier attributes should we match?"}
            ],
            max_tokens=200,
            temperature=0.5
        )
        # Parse AI response to get matching criteria
        return response.choices[0].message.content
    except:
        return []

# Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main dashboard"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get statistics
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM suppliers) as total_suppliers,
            (SELECT COUNT(*) FROM buyers) as total_buyers,
            (SELECT COUNT(*) FROM buyer_requests) as total_requests,
            (SELECT COUNT(*) FROM request_proposals) as total_proposals,
            (SELECT COUNT(*) FROM orders_raw) as total_orders
    """)
    stats = cur.fetchone()
    
    # Get recent activity
    cur.execute("""
        SELECT 
            br.buyer_name,
            br.request_name,
            br.status,
            br.created_at
        FROM buyer_requests br
        ORDER BY br.created_at DESC
        LIMIT 5
    """)
    recent_requests = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stats": stats,
        "recent_requests": recent_requests
    })

@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: Optional[str] = None):
    """AI-enhanced product search"""
    results = {"suppliers": [], "products": [], "proposals": []}
    
    if q:
        # Enhance search with AI
        enhanced_query = ai_enhance_search(q)
        search_terms = enhanced_query.split(',')
        
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Search suppliers with AI-enhanced terms
        for term in search_terms[:3]:  # Limit to top 3 terms
            term = term.strip()
            cur.execute("""
                SELECT 
                    id,
                    supplier_name,
                    country,
                    products,
                    company_email,
                    rating
                FROM suppliers
                WHERE products ILIKE %s 
                   OR product_categories ILIKE %s
                   OR supplier_name ILIKE %s
                LIMIT 10
            """, (f'%{term}%', f'%{term}%', f'%{term}%'))
            
            results["suppliers"].extend(cur.fetchall())
        
        # Remove duplicates
        seen = set()
        unique_suppliers = []
        for s in results["suppliers"]:
            if s['id'] not in seen:
                seen.add(s['id'])
                unique_suppliers.append(s)
        results["suppliers"] = unique_suppliers[:20]
        
        cur.close()
        conn.close()
    
    return templates.TemplateResponse("search.html", {
        "request": request,
        "query": q,
        "results": results,
        "enhanced_terms": enhanced_query if q else None
    })

@app.post("/api/create-request")
async def create_request(
    buyer_id: int = Form(...),
    product_needed: str = Form(...),
    quantity: float = Form(...),
    target_price: float = Form(...),
    delivery_date: str = Form(...)
):
    """Create a new buyer request with AI matching"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Create the request
    cur.execute("""
        INSERT INTO buyer_requests 
        (buyer_id, request_name, status, created_at)
        VALUES (%s, %s, 'New', %s)
        RETURNING id
    """, (buyer_id, product_needed, datetime.now()))
    
    request_id = cur.fetchone()['id']
    
    # Use AI to find matching suppliers
    request_data = {
        "product": product_needed,
        "quantity": quantity,
        "target_price": target_price
    }
    
    # AI-enhanced supplier matching
    matching_criteria = ai_match_suppliers(request_data)
    
    # Find and notify matching suppliers
    cur.execute("""
        SELECT id, supplier_name, company_email
        FROM suppliers
        WHERE products ILIKE %s
        LIMIT 10
    """, (f'%{product_needed}%',))
    
    matching_suppliers = cur.fetchall()
    
    conn.commit()
    cur.close()
    conn.close()
    
    return JSONResponse({
        "success": True,
        "request_id": request_id,
        "matched_suppliers": len(matching_suppliers),
        "ai_criteria": matching_criteria
    })

@app.get("/api/ai-insights/{supplier_id}")
async def get_ai_insights(supplier_id: int):
    """Get AI-generated insights for a supplier"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT supplier_name, products, country, rating
        FROM suppliers
        WHERE id = %s
    """, (supplier_id,))
    
    supplier = cur.fetchone()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    # Generate AI insights
    try:
        response = openai.ChatCompletion.create(
            deployment_id=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a supply chain analyst. Provide brief insights about this supplier."},
                {"role": "user", "content": f"Supplier: {supplier['supplier_name']}, Products: {supplier['products'][:200]}, Country: {supplier['country']}"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        insights = response.choices[0].message.content
    except:
        insights = "AI insights temporarily unavailable"
    
    cur.close()
    conn.close()
    
    return JSONResponse({
        "supplier": supplier,
        "ai_insights": insights
    })

@app.get("/workflow", response_class=HTMLResponse)
async def workflow_view(request: Request):
    """Visual workflow status"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get workflow statistics
    cur.execute("""
        SELECT 
            'Buyers' as stage, COUNT(*) as count FROM buyers
        UNION ALL
        SELECT 'Requests', COUNT(*) FROM buyer_requests
        UNION ALL
        SELECT 'Proposals', COUNT(*) FROM request_proposals
        UNION ALL
        SELECT 'Orders', COUNT(*) FROM orders_raw
        UNION ALL
        SELECT 'Invoices', COUNT(*) FROM invoices_raw
    """)
    
    workflow_stats = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return templates.TemplateResponse("workflow.html", {
        "request": request,
        "workflow_stats": workflow_stats
    })

@app.get("/api/price-comparison")
async def compare_prices(product: str):
    """AI-enhanced price comparison"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get prices from database
    cur.execute("""
        SELECT 
            data->>'Product Name' as product,
            data->>'Supplier' as supplier,
            data->>'Unit Wholesale Price (latest)' as price,
            data->>'Currency for price' as currency
        FROM products_raw
        WHERE data->>'Product Name' ILIKE %s
        LIMIT 20
    """, (f'%{product}%',))
    
    prices = cur.fetchall()
    
    # AI analysis of prices
    if prices:
        try:
            price_data = [f"{p['supplier']}: {p['price']}" for p in prices if p['price']]
            response = openai.ChatCompletion.create(
                deployment_id=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "Analyze these prices and provide a brief recommendation."},
                    {"role": "user", "content": f"Product: {product}\nPrices: {', '.join(price_data[:5])}"}
                ],
                max_tokens=100,
                temperature=0.5
            )
            recommendation = response.choices[0].message.content
        except:
            recommendation = "Compare prices to find the best value"
    else:
        recommendation = "No price data available"
    
    cur.close()
    conn.close()
    
    return JSONResponse({
        "product": product,
        "prices": prices,
        "ai_recommendation": recommendation
    })

@app.get("/api/workflow-optimization")
async def optimize_workflow():
    """AI suggestions for workflow optimization"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get current workflow metrics
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM buyer_requests WHERE status = 'New') as pending_requests,
            (SELECT COUNT(*) FROM request_proposals WHERE status = 'New') as pending_proposals,
            (SELECT AVG(EXTRACT(DAY FROM (NOW() - created_at))) 
             FROM buyer_requests WHERE status = 'New') as avg_request_age
    """)
    
    metrics = cur.fetchone()
    
    # Get AI recommendations
    try:
        response = openai.ChatCompletion.create(
            deployment_id=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "You are a business process optimization expert."},
                {"role": "user", "content": f"Metrics: {json.dumps(metrics)}. Provide 3 brief optimization suggestions."}
            ],
            max_tokens=200,
            temperature=0.6
        )
        suggestions = response.choices[0].message.content
    except:
        suggestions = "1. Process pending requests\n2. Follow up on proposals\n3. Automate routine tasks"
    
    cur.close()
    conn.close()
    
    return JSONResponse({
        "metrics": metrics,
        "ai_suggestions": suggestions
    })

if __name__ == "__main__":
    import uvicorn
    
    # Create templates directory if not exists
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    print("Starting FDX Trading Application...")
    print("Using Azure PostgreSQL and Azure AI")
    print("Access at: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)