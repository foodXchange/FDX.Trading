"""
ADMIN PORTAL WITH IMPERSONATION
Login as super user and act on behalf of any buyer or supplier
"""

from fastapi import FastAPI, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Optional
import hashlib

app = FastAPI(title="FDX Admin Portal")

# Database
POLAND_DB = "postgresql://fdxadmin:FoodXchange2024@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"

# Simple auth (in production use proper auth)
SUPER_ADMIN = {
    "username": "admin",
    "password": "fdx2024"  # Change this!
}

def get_db():
    return psycopg2.connect(POLAND_DB, cursor_factory=RealDictCursor)

def check_auth(token: str) -> bool:
    """Simple token check"""
    return token == hashlib.md5(f"{SUPER_ADMIN['username']}:{SUPER_ADMIN['password']}".encode()).hexdigest()

@app.get("/", response_class=HTMLResponse)
async def login_page(token: Optional[str] = Cookie(None)):
    """Login page or dashboard"""
    
    # If logged in, show dashboard
    if token and check_auth(token):
        return await admin_dashboard()
    
    # Show login
    return """
<!DOCTYPE html>
<html>
<head>
    <title>FDX Admin Portal</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 400px;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 10px;
            color: #333;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        input {
            width: 100%;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        
        button:hover {
            opacity: 0.9;
        }
        
        .info {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
            font-size: 13px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🔐 Admin Portal</h1>
        <div class="subtitle">Super Admin Access</div>
        
        <form action="/auth" method="post">
            <input type="text" name="username" placeholder="Username" required autofocus>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login as Admin</button>
        </form>
        
        <div class="info">
            <strong>Admin Features:</strong><br>
            • View as any buyer<br>
            • Act as any supplier<br>
            • Manage all workflows<br>
            • Full system control
        </div>
    </div>
</body>
</html>
"""

@app.post("/auth")
async def authenticate(username: str = Form(...), password: str = Form(...)):
    """Authenticate admin"""
    if username == SUPER_ADMIN['username'] and password == SUPER_ADMIN['password']:
        token = hashlib.md5(f"{username}:{password}".encode()).hexdigest()
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="token", value=token)
        return response
    return HTMLResponse("Invalid credentials <a href='/'>Try again</a>")

async def admin_dashboard():
    """Admin dashboard with impersonation options"""
    
    conn = get_db()
    cur = conn.cursor()
    
    # Get stats
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM buyers) as buyers,
            (SELECT COUNT(*) FROM suppliers) as suppliers,
            (SELECT COUNT(*) FROM buyer_requests) as requests,
            (SELECT COUNT(*) FROM request_proposals) as proposals
    """)
    stats = cur.fetchone()
    
    # Get recent buyers
    cur.execute("""
        SELECT DISTINCT buyer_name FROM buyer_requests 
        ORDER BY buyer_name LIMIT 10
    """)
    buyers = cur.fetchall()
    
    # Get recent suppliers
    cur.execute("""
        SELECT id, supplier_name, company_email FROM suppliers 
        WHERE company_email IS NOT NULL 
        ORDER BY id DESC LIMIT 10
    """)
    suppliers = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Generate buyer options
    buyer_options = ""
    for b in buyers:
        buyer_options += f"""
        <div class="user-card">
            <div class="user-info">
                <div class="user-name">👤 {b['buyer_name']}</div>
                <div class="user-type">Buyer Account</div>
            </div>
            <button onclick="actAs('buyer', '{b['buyer_name']}')">Act as Buyer</button>
        </div>
        """
    
    # Generate supplier options
    supplier_options = ""
    for s in suppliers:
        supplier_options += f"""
        <div class="user-card">
            <div class="user-info">
                <div class="user-name">🏭 {s['supplier_name']}</div>
                <div class="user-email">{s['company_email']}</div>
                <div class="user-type">Supplier Account</div>
            </div>
            <button onclick="actAs('supplier', '{s['id']}')">Act as Supplier</button>
        </div>
        """
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard - FDX</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header h1 {{
            font-size: 24px;
        }}
        
        .admin-badge {{
            background: rgba(255,255,255,0.2);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            padding: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }}
        
        .impersonate-section {{
            padding: 20px;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }}
        
        .users-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .user-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .user-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 3px;
        }}
        
        .user-email {{
            font-size: 12px;
            color: #666;
        }}
        
        .user-type {{
            font-size: 11px;
            color: #999;
            margin-top: 3px;
        }}
        
        button {{
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 13px;
            cursor: pointer;
        }}
        
        button:hover {{
            background: #5569d8;
        }}
        
        .quick-actions {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .action-btn {{
            display: block;
            width: 200px;
            margin-bottom: 10px;
            padding: 10px;
            text-align: center;
        }}
        
        .logout {{
            background: #dc3545;
        }}
        
        .logout:hover {{
            background: #c82333;
        }}
        
        .current-mode {{
            background: #28a745;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛡️ Admin Dashboard <span class="current-mode">SUPER ADMIN MODE</span></h1>
        <div class="admin-badge">Logged in as: admin</div>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{stats['buyers']}</div>
            <div class="stat-label">Total Buyers</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['suppliers']}</div>
            <div class="stat-label">Total Suppliers</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['requests']}</div>
            <div class="stat-label">Active Requests</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{stats['proposals']}</div>
            <div class="stat-label">Proposals</div>
        </div>
    </div>
    
    <div class="impersonate-section">
        <div class="section-title">🎭 Act as Buyer</div>
        <div class="users-grid">
            {buyer_options}
            <div class="user-card">
                <div class="user-info">
                    <div class="user-name">➕ New Buyer</div>
                    <div class="user-type">Create new buyer account</div>
                </div>
                <button onclick="createNew('buyer')">Create Buyer</button>
            </div>
        </div>
    </div>
    
    <div class="impersonate-section">
        <div class="section-title">🏭 Act as Supplier</div>
        <div class="users-grid">
            {supplier_options}
            <div class="user-card">
                <div class="user-info">
                    <div class="user-name">➕ New Supplier</div>
                    <div class="user-type">Create new supplier account</div>
                </div>
                <button onclick="createNew('supplier')">Create Supplier</button>
            </div>
        </div>
    </div>
    
    <div class="quick-actions">
        <button class="action-btn" onclick="window.location.href='/buyer'">
            👤 Buyer Portal
        </button>
        <button class="action-btn" onclick="window.location.href='/supplier'">
            🏭 Supplier Portal
        </button>
        <button class="action-btn" onclick="window.location.href='/workflows'">
            📊 All Workflows
        </button>
        <button class="action-btn logout" onclick="logout()">
            🚪 Logout
        </button>
    </div>
    
    <script>
        function actAs(type, id) {{
            // Store impersonation in session
            localStorage.setItem('impersonate_type', type);
            localStorage.setItem('impersonate_id', id);
            
            if (type === 'buyer') {{
                alert('Now acting as buyer: ' + id);
                window.location.href = '/buyer?as=' + encodeURIComponent(id);
            }} else {{
                alert('Now acting as supplier ID: ' + id);
                window.location.href = '/supplier?as=' + id;
            }}
        }}
        
        function createNew(type) {{
            const name = prompt('Enter ' + type + ' name:');
            if (name) {{
                alert('Creating new ' + type + ': ' + name);
                // Would POST to create endpoint
            }}
        }}
        
        function logout() {{
            document.cookie = 'token=; expires=Thu, 01 Jan 1970 00:00:00 UTC;';
            window.location.href = '/';
        }}
    </script>
</body>
</html>
"""

@app.get("/buyer", response_class=HTMLResponse)
async def buyer_portal(as_user: Optional[str] = None, token: Optional[str] = Cookie(None)):
    """Buyer portal (admin can impersonate)"""
    
    # Check if admin
    is_admin = token and check_auth(token)
    current_user = as_user if (is_admin and as_user) else "Default Buyer"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Buyer Portal - {current_user}</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; background: #f5f7fa; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .admin-notice {{ background: #ffeaa7; padding: 10px; border-radius: 4px; margin-bottom: 10px; }}
        .search-box {{ width: 100%; padding: 15px; font-size: 16px; border: 1px solid #ddd; border-radius: 8px; }}
        .btn {{ padding: 10px 20px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; }}
    </style>
</head>
<body>
    {'<div class="admin-notice">🛡️ ADMIN MODE: Acting as ' + current_user + '</div>' if is_admin else ''}
    
    <div class="header">
        <h1>Buyer Portal</h1>
        <p>Logged in as: <strong>{current_user}</strong></p>
    </div>
    
    <form action="/buyer/search" method="post">
        <input type="hidden" name="buyer" value="{current_user}">
        <input type="text" class="search-box" name="query" placeholder="What product do you need?" required>
        <button type="submit" class="btn">Search Suppliers</button>
    </form>
    
    <h3>Your Recent Requests:</h3>
    <ul>
        <li>Sunflower Oil - 5000 bottles (3 suppliers responded)</li>
        <li>Olive Oil - 1000 bottles (5 suppliers responded)</li>
    </ul>
    
    {f'<a href="/">← Back to Admin</a>' if is_admin else ''}
</body>
</html>
"""

@app.get("/supplier", response_class=HTMLResponse)
async def supplier_portal(as_user: Optional[str] = None, token: Optional[str] = Cookie(None)):
    """Supplier portal (admin can impersonate)"""
    
    # Check if admin
    is_admin = token and check_auth(token)
    
    if not as_user:
        return "Please specify supplier ID"
    
    # Get supplier info
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM suppliers WHERE id = %s", (as_user,))
    supplier = cur.fetchone()
    cur.close()
    conn.close()
    
    if not supplier:
        return "Supplier not found"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Supplier Portal - {supplier['supplier_name']}</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; background: #f5f7fa; }}
        .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .admin-notice {{ background: #ffeaa7; padding: 10px; border-radius: 4px; margin-bottom: 10px; }}
        .request-card {{ background: white; padding: 15px; border-radius: 8px; margin-bottom: 10px; }}
        .btn {{ padding: 8px 16px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer; }}
    </style>
</head>
<body>
    {'<div class="admin-notice">🛡️ ADMIN MODE: Acting as ' + supplier['supplier_name'] + '</div>' if is_admin else ''}
    
    <div class="header">
        <h1>Supplier Portal</h1>
        <p>Company: <strong>{supplier['supplier_name']}</strong></p>
        <p>Email: {supplier['company_email']}</p>
        <p>Products: {supplier['products'][:100] if supplier['products'] else 'Not specified'}...</p>
    </div>
    
    <h3>New Requests for You:</h3>
    
    <div class="request-card">
        <h4>Sunflower Oil - 5000 bottles</h4>
        <p>Buyer: [Hidden until quote accepted]</p>
        <p>Delivery: Within 30 days</p>
        
        <form style="margin-top: 10px;">
            <input type="number" placeholder="Price per bottle" step="0.01" required>
            <input type="number" placeholder="Minimum quantity" required>
            <input type="number" placeholder="Delivery days" required>
            <button type="submit" class="btn">Send Quote</button>
        </form>
    </div>
    
    <div class="request-card">
        <h4>Olive Oil - 1000 bottles</h4>
        <p>Buyer: [Hidden until quote accepted]</p>
        <p>Delivery: Within 45 days</p>
        <button class="btn">Send Quote</button>
    </div>
    
    {f'<a href="/">← Back to Admin</a>' if is_admin else ''}
</body>
</html>
"""

@app.get("/logout")
async def logout():
    """Logout admin"""
    response = RedirectResponse(url="/")
    response.delete_cookie("token")
    return response

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("ADMIN PORTAL WITH IMPERSONATION")
    print("="*60)
    print("\nFeatures:")
    print("✓ Login as super admin")
    print("✓ View all buyers and suppliers")
    print("✓ Act on behalf of any user")
    print("✓ Switch between buyer/supplier views")
    print("✓ Full control over workflows")
    print("\nDefault login:")
    print("Username: admin")
    print("Password: fdx2024")
    print("\nStarting at: http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)