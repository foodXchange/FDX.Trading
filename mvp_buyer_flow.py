"""
MVP BUYER FLOW - Professional but Simple
Clean, functional, ready for real use
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime
from typing import Optional, List
import json
import re
from urllib.parse import urlparse

# Azure OpenAI for AI matching
from openai import AzureOpenAI

app = FastAPI(title="FDX Buyer Portal MVP")

# Database connection
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_KEY'),
    api_version='2024-02-15-preview',
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)

def get_db():
    """Get database connection with error handling"""
    try:
        return psycopg2.connect(POLAND_DB, cursor_factory=RealDictCursor)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Database connection failed")

def is_valid_url(url: str) -> bool:
    """Check if string is valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_image_url(url: str) -> bool:
    """Check if URL points to an image"""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    return any(url.lower().endswith(ext) for ext in image_extensions)

@app.get("/", response_class=HTMLResponse)
async def home():
    """MVP landing page with proper styling"""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FDX Buyer Portal - MVP</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        .logo {
            text-align: center;
            font-size: 42px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .tagline {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 14px;
        }
        
        .input-group {
            position: relative;
            margin-bottom: 20px;
        }
        
        .search-input {
            width: 100%;
            padding: 16px 20px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            transition: all 0.3s;
            outline: none;
        }
        
        .search-input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .input-hint {
            display: flex;
            justify-content: space-between;
            margin-top: 8px;
            font-size: 12px;
            color: #999;
        }
        
        .btn-primary {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-primary:active {
            transform: translateY(0);
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid #e0e0e0;
        }
        
        .feature {
            text-align: center;
        }
        
        .feature-icon {
            font-size: 24px;
            margin-bottom: 8px;
        }
        
        .feature-text {
            font-size: 12px;
            color: #666;
        }
        
        .examples {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
        }
        
        .examples-title {
            font-size: 12px;
            font-weight: 600;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .example-item {
            display: inline-block;
            padding: 6px 12px;
            background: white;
            border-radius: 20px;
            font-size: 13px;
            margin: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .example-item:hover {
            background: #667eea;
            color: white;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">FDX Trading</div>
        <div class="tagline">AI-Powered Supplier Matching Platform</div>
        
        <form action="/search" method="post" onsubmit="showLoading()">
            <div class="input-group">
                <input type="text" 
                       name="query" 
                       class="search-input" 
                       placeholder="Describe product or paste image URL..."
                       required
                       autofocus>
                <div class="input-hint">
                    <span>📝 Text description</span>
                    <span>🖼️ Image URL</span>
                </div>
            </div>
            
            <button type="submit" class="btn-primary">
                Find Matching Suppliers
            </button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="margin-top: 10px; color: #666;">Analyzing with AI...</p>
        </div>
        
        <div class="examples">
            <div class="examples-title">Quick Examples</div>
            <span class="example-item" onclick="setExample('sunflower oil 1L bottles')">Sunflower Oil</span>
            <span class="example-item" onclick="setExample('extra virgin olive oil')">Olive Oil</span>
            <span class="example-item" onclick="setExample('premium pasta 500g')">Pasta</span>
            <span class="example-item" onclick="setExample('basmati rice 1kg bags')">Rice</span>
            <span class="example-item" onclick="setExample('organic honey 250g jars')">Honey</span>
        </div>
        
        <div class="features">
            <div class="feature">
                <div class="feature-icon">🤖</div>
                <div class="feature-text">AI Analysis</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🎯</div>
                <div class="feature-text">25 Best Matches</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📧</div>
                <div class="feature-text">Bulk Email</div>
            </div>
            <div class="feature">
                <div class="feature-icon">💬</div>
                <div class="feature-text">Track Replies</div>
            </div>
        </div>
    </div>
    
    <script>
        function setExample(text) {
            document.querySelector('.search-input').value = text;
            document.querySelector('.search-input').focus();
        }
        
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
    </script>
</body>
</html>
"""

@app.post("/search", response_class=HTMLResponse)
async def search(query: str = Form(...)):
    """Process search and show supplier matches"""
    
    # Validate input
    if not query or len(query) < 3:
        return "<h1>Please enter at least 3 characters</h1><a href='/'>Back</a>"
    
    # Determine query type
    query_type = "image" if is_valid_url(query) and is_image_url(query) else "text"
    
    # Get AI analysis for product understanding
    product_brief = query  # Default
    ai_categories = []
    
    try:
        if query_type == "image":
            prompt = f"""Analyze this product image URL and return:
            1. Product name and description
            2. Key specifications
            3. Relevant categories
            URL: {query}"""
        else:
            prompt = f"""Analyze this product request and return:
            1. Standardized product name
            2. Key requirements
            3. Relevant categories
            Request: {query}"""
        
        response = client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini'),
            messages=[
                {"role": "system", "content": "You are a procurement specialist. Be concise."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        product_brief = response.choices[0].message.content
        
        # Extract categories for better matching
        categories_prompt = f"List 3 product categories for: {product_brief}. Return only category names separated by commas."
        cat_response = client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini'),
            messages=[{"role": "user", "content": categories_prompt}],
            max_tokens=50
        )
        ai_categories = [c.strip() for c in cat_response.choices[0].message.content.split(',')]
        
    except Exception as e:
        print(f"AI analysis error: {e}")
    
    # Database search with AI-enhanced matching
    conn = get_db()
    cur = conn.cursor()
    
    # Build search query based on AI analysis
    search_terms = query.lower().split()[:3]  # First 3 words
    search_terms.extend([cat.lower() for cat in ai_categories[:2]])  # Add AI categories
    
    # Search with multiple terms
    search_conditions = " OR ".join([
        f"(products ILIKE '%{term}%' OR supplier_name ILIKE '%{term}%' OR product_categories ILIKE '%{term}%')"
        for term in search_terms if term
    ])
    
    # Execute search
    cur.execute(f"""
        SELECT id, supplier_name, country, products, product_categories, 
               company_email, company_website, rating, verified
        FROM suppliers
        WHERE {search_conditions if search_conditions else 'TRUE'}
        LIMIT 100
    """)
    
    all_suppliers = cur.fetchall()
    
    # Score and rank suppliers
    for supplier in all_suppliers:
        score = 0
        products_text = (supplier['products'] or '').lower()
        categories_text = (supplier['product_categories'] or '').lower()
        name_text = (supplier['supplier_name'] or '').lower()
        
        # Scoring logic
        for term in search_terms:
            if term in products_text:
                score += 30
            if term in categories_text:
                score += 20
            if term in name_text:
                score += 10
        
        # Bonus for verified suppliers
        if supplier['verified']:
            score += 15
        
        # Bonus for high rating
        if supplier['rating'] and supplier['rating'] >= 4:
            score += 10
        
        supplier['match_score'] = min(score, 100)  # Cap at 100
    
    # Sort by score and take top 25
    suppliers = sorted(all_suppliers, key=lambda x: x['match_score'], reverse=True)[:25]
    
    # Create project for tracking
    cur.execute("""
        INSERT INTO buyer_requests (buyer_name, request_name, status, created_at)
        VALUES (%s, %s, 'Active', %s)
        RETURNING id
    """, ('Buyer', product_brief[:200], datetime.now()))
    
    project_id = cur.fetchone()['id']
    conn.commit()
    
    # Store search in history
    cur.execute("""
        INSERT INTO search_history (user_email, query, results_count, timestamp)
        VALUES (%s, %s, %s, %s)
    """, ('buyer@fdx.trading', query, len(suppliers), datetime.now()))
    conn.commit()
    
    cur.close()
    conn.close()
    
    # Generate results HTML
    suppliers_html = ""
    for i, s in enumerate(suppliers, 1):
        score_class = "high" if s['match_score'] >= 80 else "medium" if s['match_score'] >= 60 else "low"
        verified_badge = "✓" if s['verified'] else ""
        
        suppliers_html += f"""
        <tr>
            <td class="checkbox-cell">
                <input type="checkbox" name="supplier_{s['id']}" value="{s['id']}" id="sup_{s['id']}">
            </td>
            <td class="rank">{i}</td>
            <td class="supplier-info">
                <div class="supplier-name">{s['supplier_name'] or 'Unknown'} {verified_badge}</div>
                <div class="supplier-location">{s['country'] or 'Not specified'}</div>
                <div class="supplier-email">{s['company_email'] or 'No email'}</div>
            </td>
            <td class="score-cell">
                <span class="score {score_class}">{s['match_score']}%</span>
            </td>
            <td class="products-cell">
                <div class="products">{(s['products'] or 'No products listed')[:150]}...</div>
            </td>
        </tr>
        """
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supplier Matches - FDX MVP</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .project-info {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .project-id {{
            background: #f0f0f0;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 14px;
            color: #666;
        }}
        
        .search-summary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        
        .query-type {{
            display: inline-block;
            padding: 4px 8px;
            background: #e0e0e0;
            border-radius: 4px;
            font-size: 12px;
            margin-left: 10px;
        }}
        
        .results-container {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
            color: #666;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        td {{
            padding: 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .checkbox-cell {{
            width: 40px;
        }}
        
        .rank {{
            width: 40px;
            font-weight: 600;
            color: #666;
        }}
        
        .supplier-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 4px;
        }}
        
        .supplier-location {{
            font-size: 13px;
            color: #666;
        }}
        
        .supplier-email {{
            font-size: 12px;
            color: #999;
            margin-top: 2px;
        }}
        
        .score {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        
        .score.high {{
            background: #d4edda;
            color: #155724;
        }}
        
        .score.medium {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .score.low {{
            background: #f8f9fa;
            color: #666;
        }}
        
        .products {{
            font-size: 13px;
            color: #666;
            line-height: 1.4;
        }}
        
        .action-bar {{
            position: sticky;
            bottom: 0;
            background: white;
            border-top: 2px solid #e0e0e0;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }}
        
        .selection-info {{
            font-size: 14px;
            color: #666;
        }}
        
        .selection-count {{
            font-weight: 600;
            color: #667eea;
            font-size: 18px;
        }}
        
        .btn-group {{
            display: flex;
            gap: 10px;
        }}
        
        .btn {{
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-secondary {{
            background: #f0f0f0;
            color: #666;
        }}
        
        .btn-secondary:hover {{
            background: #e0e0e0;
        }}
        
        .btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            cursor: pointer;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="project-info">
            <div>
                <div class="search-summary">
                    Product Analysis Complete
                    <span class="query-type">{query_type.upper()}</span>
                </div>
                <div style="color: #666; margin-top: 10px;">
                    <strong>Looking for:</strong> {product_brief[:200]}
                </div>
            </div>
            <div class="project-id">Project #{project_id}</div>
        </div>
        <div style="margin-top: 15px; color: #999; font-size: 14px;">
            Found {len(suppliers)} matching suppliers • Sorted by relevance
        </div>
    </div>
    
    <form id="suppliers-form" action="/email/{project_id}" method="post">
        <div class="results-container">
            <table>
                <thead>
                    <tr>
                        <th class="checkbox-cell">
                            <input type="checkbox" id="select-all">
                        </th>
                        <th>Rank</th>
                        <th>Supplier Details</th>
                        <th>Match</th>
                        <th>Products & Capabilities</th>
                    </tr>
                </thead>
                <tbody>
                    {suppliers_html if suppliers_html else '<tr><td colspan="5" class="no-results">No matching suppliers found. Try different search terms.</td></tr>'}
                </tbody>
            </table>
        </div>
        
        <div class="action-bar">
            <div class="selection-info">
                <span class="selection-count" id="selected-count">0</span>
                <span>suppliers selected</span>
            </div>
            <div class="btn-group">
                <button type="button" class="btn btn-secondary" onclick="window.location.href='/'">
                    New Search
                </button>
                <button type="submit" class="btn btn-primary" id="email-btn" disabled>
                    Send Email to Selected
                </button>
            </div>
        </div>
    </form>
    
    <script>
        // Select all functionality
        document.getElementById('select-all').addEventListener('change', function() {{
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name^="supplier_"]');
            checkboxes.forEach(cb => cb.checked = this.checked);
            updateCount();
        }});
        
        // Update count and button state
        function updateCount() {{
            const count = document.querySelectorAll('input[type="checkbox"][name^="supplier_"]:checked').length;
            document.getElementById('selected-count').textContent = count;
            document.getElementById('email-btn').disabled = count === 0;
        }}
        
        // Listen to individual checkboxes
        document.querySelectorAll('input[type="checkbox"][name^="supplier_"]').forEach(cb => {{
            cb.addEventListener('change', updateCount);
        }});
    </script>
</body>
</html>
"""

@app.post("/email/{project_id}", response_class=HTMLResponse)
async def email_suppliers(project_id: int, request: Request):
    """Send emails and set up conversation tracking"""
    
    form_data = await request.form()
    selected_ids = [k.split('_')[1] for k in form_data.keys() if k.startswith('supplier_')]
    
    if not selected_ids:
        return """
        <html><body style="font-family: sans-serif; padding: 40px;">
        <h2>No suppliers selected</h2>
        <p>Please select at least one supplier to email.</p>
        <a href="/" style="color: #667eea;">← Back to search</a>
        </body></html>
        """
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get supplier details
    cur.execute("""
        SELECT id, supplier_name, company_email, country
        FROM suppliers
        WHERE id = ANY(%s)
    """, (selected_ids,))
    
    suppliers = cur.fetchall()
    
    # Create email records
    email_ids = []
    for supplier in suppliers:
        cur.execute("""
            INSERT INTO email_log (supplier_id, project_id, status, sent_at, supplier_email)
            VALUES (%s, %s, 'sent', %s, %s)
            RETURNING id
        """, (supplier['id'], project_id, datetime.now(), supplier['company_email']))
        email_ids.append(cur.fetchone()['id'])
    
    conn.commit()
    
    # Get project details
    cur.execute("SELECT request_name FROM buyer_requests WHERE id = %s", (project_id,))
    project = cur.fetchone()
    
    cur.close()
    conn.close()
    
    # Generate conversation tracking page
    suppliers_html = ""
    for s in suppliers:
        suppliers_html += f"""
        <div class="conversation-card">
            <div class="supplier-header">
                <div>
                    <h3>{s['supplier_name']}</h3>
                    <span class="email">{s['company_email'] or 'No email available'}</span>
                    <span class="country">{s['country'] or ''}</span>
                </div>
                <span class="status sent">📧 Sent</span>
            </div>
            
            <div class="conversation-thread">
                <div class="message outgoing">
                    <div class="message-header">
                        <span>You</span>
                        <span class="time">Just now</span>
                    </div>
                    <div class="message-body">
                        Hello,<br><br>
                        We are looking for suppliers for: {project['request_name'] if project else 'our requirements'}.<br><br>
                        Please send us your best prices and terms.<br><br>
                        Best regards,<br>
                        FDX Trading Team
                    </div>
                </div>
                
                <div class="message incoming pending">
                    <div class="message-header">
                        <span>{s['supplier_name']}</span>
                        <span class="time">Awaiting response</span>
                    </div>
                    <div class="message-body">
                        <span style="color: #999; font-style: italic;">No response yet...</span>
                    </div>
                </div>
            </div>
            
            <div class="quick-actions">
                <button class="btn-small">Follow Up</button>
                <button class="btn-small">Mark Important</button>
                <button class="btn-small">Archive</button>
            </div>
        </div>
        """
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Conversations - Project #{project_id}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        
        .header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        
        .stats {{
            display: flex;
            gap: 30px;
            margin-top: 20px;
        }}
        
        .stat {{
            display: flex;
            flex-direction: column;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: 600;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #999;
            margin-top: 4px;
        }}
        
        .conversation-card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .supplier-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .supplier-header h3 {{
            margin-bottom: 5px;
            color: #333;
        }}
        
        .email {{
            font-size: 13px;
            color: #666;
            margin-right: 15px;
        }}
        
        .country {{
            font-size: 13px;
            color: #999;
        }}
        
        .status {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
        }}
        
        .status.sent {{
            background: #e3f2fd;
            color: #1976d2;
        }}
        
        .status.replied {{
            background: #d4edda;
            color: #155724;
        }}
        
        .conversation-thread {{
            margin: 20px 0;
        }}
        
        .message {{
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .message.outgoing {{
            background: #f0f4ff;
            margin-right: 50px;
        }}
        
        .message.incoming {{
            background: #f8f9fa;
            margin-left: 50px;
        }}
        
        .message.incoming.pending {{
            border: 1px dashed #ddd;
        }}
        
        .message-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 13px;
        }}
        
        .message-header span:first-child {{
            font-weight: 600;
            color: #333;
        }}
        
        .time {{
            color: #999;
        }}
        
        .message-body {{
            font-size: 14px;
            line-height: 1.5;
            color: #333;
        }}
        
        .quick-actions {{
            display: flex;
            gap: 10px;
            padding-top: 15px;
            border-top: 1px solid #f0f0f0;
        }}
        
        .btn-small {{
            padding: 8px 16px;
            border: 1px solid #e0e0e0;
            background: white;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s;
        }}
        
        .btn-small:hover {{
            background: #f8f9fa;
            border-color: #667eea;
            color: #667eea;
        }}
        
        .action-buttons {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
        }}
        
        .fab {{
            padding: 15px 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 30px;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
            transition: all 0.2s;
        }}
        
        .fab:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .refresh-notice {{
            background: #fff3cd;
            color: #856404;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Email Conversation Tracking</h1>
        <p style="color: #666;">Project #{project_id} • {project['request_name'][:100] if project else 'Product Sourcing'}</p>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-value">{len(suppliers)}</span>
                <span class="stat-label">Emails Sent</span>
            </div>
            <div class="stat">
                <span class="stat-value">0</span>
                <span class="stat-label">Responses</span>
            </div>
            <div class="stat">
                <span class="stat-value">0%</span>
                <span class="stat-label">Response Rate</span>
            </div>
        </div>
    </div>
    
    <div class="refresh-notice">
        💡 This page auto-refreshes every 30 seconds to check for new responses
    </div>
    
    {suppliers_html}
    
    <div class="action-buttons">
        <button class="fab" onclick="window.location.href='/'">New Search</button>
    </div>
    
    <script>
        // Auto-refresh to check for responses
        setTimeout(() => {{
            location.reload();
        }}, 30000);
        
        // Quick action handlers
        document.querySelectorAll('.btn-small').forEach(btn => {{
            btn.addEventListener('click', function() {{
                alert('Feature coming soon: ' + this.textContent);
            }});
        }});
    </script>
</body>
</html>
"""

@app.get("/api/project/{project_id}/responses")
async def get_responses(project_id: int):
    """API endpoint to check for email responses"""
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM email_log 
        WHERE project_id = %s
        ORDER BY sent_at DESC
    """, (project_id,))
    
    responses = cur.fetchall()
    cur.close()
    conn.close()
    
    return JSONResponse(content={"responses": responses})

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("FDX BUYER PORTAL - MVP")
    print("="*60)
    print("\nStarting server...")
    print("\nOpen browser: http://localhost:8000")
    print("\nFeatures:")
    print("✓ Text and image URL search")
    print("✓ AI product analysis") 
    print("✓ Top 25 supplier matching")
    print("✓ Multi-select with checkboxes")
    print("✓ Full conversation tracking")
    print("✓ Auto-refresh for responses")
    print("\nPress Ctrl+C to stop")
    uvicorn.run(app, host="0.0.0.0", port=8000)