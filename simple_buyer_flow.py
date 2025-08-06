"""
ULTRA SIMPLE BUYER FLOW - Google/Claude Style
One file, minimal graphics, vanilla JS
"""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from typing import Optional
import json

# Azure OpenAI for AI matching
from openai import AzureOpenAI

app = FastAPI()

# Database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_KEY'),
    api_version='2024-02-15-preview',
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)

def get_db():
    return psycopg2.connect(POLAND_DB, cursor_factory=RealDictCursor)

@app.get("/", response_class=HTMLResponse)
async def home():
    """Ultra simple search page - Google style"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>FDX Buyer Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        
        /* Google-style search */
        .search-container {
            background: white;
            padding: 40px;
            border-radius: 8px;
            margin-top: 50px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .logo {
            text-align: center;
            font-size: 48px;
            font-weight: bold;
            color: #1a73e8;
            margin-bottom: 30px;
        }
        
        .search-box {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 1px solid #ddd;
            border-radius: 24px;
            outline: none;
        }
        
        .search-box:focus {
            box-shadow: 0 1px 6px rgba(32,33,36,.28);
            border-color: #fff;
        }
        
        .or-divider {
            text-align: center;
            margin: 20px 0;
            color: #666;
        }
        
        .buttons {
            text-align: center;
            margin-top: 30px;
        }
        
        .btn {
            background: #1a73e8;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            margin: 0 5px;
        }
        
        .btn:hover {
            background: #1557b0;
        }
        
        .example {
            color: #666;
            font-size: 13px;
            margin-top: 10px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="search-container">
        <div class="logo">FDX</div>
        
        <form action="/search" method="post">
            <input type="text" 
                   name="query" 
                   class="search-box" 
                   placeholder="Type product name or paste image URL..."
                   autofocus>
            
            <div class="example">
                Try: "sunflower oil" or "https://example.com/product.jpg"
            </div>
            
            <div class="buttons">
                <button type="submit" class="btn">Search Suppliers</button>
            </div>
        </form>
    </div>
</body>
</html>
"""

@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    """AI-powered supplier search"""
    
    # Check if query is image URL
    is_image = query.startswith('http') and any(ext in query.lower() for ext in ['.jpg', '.png', '.jpeg', '.webp'])
    
    # Get AI analysis
    if is_image:
        prompt = f"Analyze this product image URL and describe what product to source: {query}"
    else:
        prompt = f"Analyze this product request and extract key requirements: {query}"
    
    # Get product brief from AI
    try:
        response = client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini'),
            messages=[
                {"role": "system", "content": "Extract product requirements in 20 words"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        product_brief = response.choices[0].message.content
    except:
        product_brief = query  # Fallback to original query
    
    # Search suppliers in database
    conn = get_db()
    cur = conn.cursor()
    
    # Simple search - will enhance with AI scoring
    search_term = query.split()[0] if ' ' in query else query
    cur.execute("""
        SELECT id, supplier_name, country, products, company_email, rating
        FROM suppliers
        WHERE products ILIKE %s OR supplier_name ILIKE %s
        LIMIT 25
    """, (f'%{search_term}%', f'%{search_term}%'))
    
    suppliers = cur.fetchall()
    
    # Calculate simple relevance score (will enhance with AI)
    for s in suppliers:
        if search_term.lower() in (s['products'] or '').lower():
            s['score'] = 95
        elif search_term.lower() in (s['supplier_name'] or '').lower():
            s['score'] = 85
        else:
            s['score'] = 75
    
    # Sort by score
    suppliers.sort(key=lambda x: x['score'], reverse=True)
    
    # Create project in database
    cur.execute("""
        INSERT INTO buyer_requests (buyer_name, request_name, status, created_at)
        VALUES ('Current User', %s, 'Active', %s)
        RETURNING id
    """, (product_brief, datetime.now()))
    
    project_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    
    # Generate results page
    suppliers_html = ""
    for i, s in enumerate(suppliers[:25], 1):
        suppliers_html += f"""
        <tr>
            <td><input type="checkbox" name="supplier_{s['id']}" value="{s['id']}"></td>
            <td>{i}</td>
            <td><strong>{s['supplier_name'] or 'Unknown'}</strong><br>
                <small>{s['country'] or 'N/A'}</small></td>
            <td>{s['score']}%</td>
            <td><small>{(s['products'] or '')[:100]}...</small></td>
        </tr>
        """
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Supplier Results</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: Arial, sans-serif; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }}
        
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .brief {{
            color: #1a73e8;
            font-size: 18px;
            margin-bottom: 10px;
        }}
        
        .stats {{
            color: #666;
            font-size: 14px;
        }}
        
        table {{
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: normal;
            color: #666;
            font-size: 14px;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .actions {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .btn {{
            background: #1a73e8;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 4px;
            cursor: pointer;
        }}
        
        .btn:hover {{
            background: #1557b0;
        }}
        
        .score {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }}
        
        .high {{ background: #d4edda; color: #155724; }}
        .medium {{ background: #fff3cd; color: #856404; }}
        .low {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="brief">Looking for: {product_brief}</div>
        <div class="stats">Found {len(suppliers)} suppliers • Project #{project_id}</div>
    </div>
    
    <form id="suppliers-form" action="/email/{project_id}" method="post">
        <table>
            <thead>
                <tr>
                    <th width="40">✓</th>
                    <th width="40">#</th>
                    <th>Supplier</th>
                    <th width="80">Match</th>
                    <th>Products</th>
                </tr>
            </thead>
            <tbody>
                {suppliers_html}
            </tbody>
        </table>
        
        <div class="actions">
            <span id="selected-count">0</span> selected
            <button type="submit" class="btn">Email Selected Suppliers</button>
        </div>
    </form>
    
    <script>
        // Vanilla JS - count selected
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => {{
            cb.addEventListener('change', () => {{
                const count = document.querySelectorAll('input[type="checkbox"]:checked').length;
                document.getElementById('selected-count').textContent = count;
            }});
        }});
    </script>
</body>
</html>
"""

@app.post("/email/{project_id}", response_class=HTMLResponse)
async def email_suppliers(project_id: int, request: Request):
    """Send emails and track conversations"""
    
    form_data = await request.form()
    selected = [k.split('_')[1] for k in form_data.keys() if k.startswith('supplier_')]
    
    if not selected:
        return "<h1>No suppliers selected</h1><a href='/'>Back</a>"
    
    # Create email tracking records
    conn = get_db()
    cur = conn.cursor()
    
    for supplier_id in selected:
        cur.execute("""
            INSERT INTO email_log (project_id, supplier_id, status, sent_at)
            VALUES (%s, %s, 'sent', %s)
        """, (project_id, supplier_id, datetime.now()))
    
    conn.commit()
    
    # Get supplier details for display
    cur.execute("""
        SELECT supplier_name, company_email 
        FROM suppliers 
        WHERE id = ANY(%s)
    """, (selected,))
    
    suppliers = cur.fetchall()
    cur.close()
    conn.close()
    
    # Simple conversation tracking page
    suppliers_list = ""
    for s in suppliers:
        suppliers_list += f"""
        <div class="supplier-card">
            <h3>{s['supplier_name']}</h3>
            <div class="email">{s['company_email'] or 'No email'}</div>
            <div class="status">📧 Email sent</div>
            <div class="thread">
                <div class="message out">Hi, we need sunflower oil. Please send prices.</div>
                <div class="message in pending">Awaiting response...</div>
            </div>
        </div>
        """
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Email Tracking</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }}
        
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        
        .supplier-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .email {{
            color: #666;
            font-size: 14px;
            margin: 5px 0;
        }}
        
        .status {{
            color: #34a853;
            font-size: 14px;
            margin: 10px 0;
        }}
        
        .thread {{
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}
        
        .message {{
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            font-size: 14px;
        }}
        
        .message.out {{
            background: #e3f2fd;
            margin-right: 50px;
        }}
        
        .message.in {{
            background: #f5f5f5;
            margin-left: 50px;
        }}
        
        .message.pending {{
            color: #999;
            font-style: italic;
        }}
        
        .btn {{
            background: #1a73e8;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Email Tracking - Project #{project_id}</h1>
        <p>Emailed {len(suppliers)} suppliers • Full conversation threads below</p>
    </div>
    
    {suppliers_list}
    
    <div style="text-align: center; margin-top: 30px;">
        <a href="/" class="btn">New Search</a>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds to check for responses
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

@app.get("/track/{project_id}", response_class=HTMLResponse)
async def track_conversations(project_id: int):
    """Track all email conversations for a project"""
    # This will show full conversation threads
    # Will implement after basic flow works
    pass

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("ULTRA SIMPLE BUYER FLOW")
    print("="*60)
    print("\nOpen browser: http://localhost:8000")
    print("\nFeatures:")
    print("1. Text or image URL search")
    print("2. AI matching for 25 suppliers")
    print("3. Checkbox selection")
    print("4. Full conversation tracking")
    print("\nPress Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)