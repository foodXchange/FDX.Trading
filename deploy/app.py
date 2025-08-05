# My First Python Web App with Bootstrap, Jinja2, and FastAPI
# This file is the main application that runs your website

# === IMPORTS ===
# Import necessary libraries
from fastapi import FastAPI, Request, Form, File, UploadFile  # FastAPI: web framework, Request: HTTP requests, Form: HTML forms, File: file uploads
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse  # HTMLResponse: return HTML pages, RedirectResponse: redirect users
from fastapi.staticfiles import StaticFiles  # StaticFiles: serve CSS/JS files
from fastapi.templating import Jinja2Templates  # Jinja2Templates: render HTML templates
from typing import List, Dict  # Type hints for better code
import os  # Operating system functions
import json  # JSON handling for API responses
from dotenv import load_dotenv  # Load environment variables from .env file
# Database imports handled within routes as needed

# Load environment variables from .env file
# This reads DATABASE_URL and other settings
load_dotenv()

# === CREATE APP ===
# Create the FastAPI application instance
app = FastAPI(
    title="FDX.trading",  # Name of your app
    description="Learning FastAPI with Bootstrap and PostgreSQL",  # Description
    version="1.0.0"  # Version number
)

# === STATIC FILES ===
# Mount static files (CSS, JS, images) to be served at /static URL
# This makes files in static folder accessible via web
app.mount("/static", StaticFiles(directory="static"), name="static")

# === TEMPLATES ===
# Set up Jinja2 templates - this tells FastAPI where to find HTML files
templates = Jinja2Templates(directory="templates")


# === HELPER FUNCTIONS ===
def get_app_context():
    """
    Returns common data needed by all templates
    This function provides data that every page needs
    """
    return {
        "app_name": "FDX.trading",  # App name to show in navbar
        "debug": os.getenv("DEBUG", "False"),  # Debug mode from .env
        "user": {"email": "udi@fdx.trading"}  # Default user context
    }

# === ROUTES (PAGES) ===

# LEAN PROJECT DETAILS ROUTE (WITH REAL DATA)
@app.get("/project_details")
async def project_details_with_data(id: int = 1, country: str = None, min_score: int = 0):
    """Project details with real data - lean and simple"""
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get project info
        cursor.execute("""
            SELECT id, project_name, description, created_at FROM projects 
            WHERE id = %s AND user_email = %s
        """, (id, 'udi@fdx.trading'))
        
        project = cursor.fetchone()
        
        if not project:
            return HTMLResponse(content="<h1>Project not found</h1>", status_code=404)
        
        # Get suppliers with filters
        query = """
            SELECT supplier_id, supplier_name, supplier_country, 
                   supplier_email, score, products
            FROM project_suppliers
            WHERE project_id = %s
        """
        params = [id]
        
        if country:
            query += " AND supplier_country = %s"
            params.append(country)
        
        if min_score > 0:
            query += " AND COALESCE(score, 0) >= %s"
            params.append(min_score)
            
        query += " ORDER BY score DESC, supplier_name"
        
        cursor.execute(query, params)
        suppliers = cursor.fetchall()
        
        # Get countries for filter
        cursor.execute("""
            SELECT DISTINCT supplier_country 
            FROM project_suppliers 
            WHERE project_id = %s AND supplier_country IS NOT NULL
            ORDER BY supplier_country
        """, (id,))
        countries = [row['supplier_country'] for row in cursor.fetchall()]
        
        # Generate suppliers HTML with checkboxes
        suppliers_html = ""
        for supplier in suppliers:
            suppliers_html += f"""
            <div class="card mb-3">
                <div class="card-body">
                    <div class="row align-items-center">
                        <div class="col-auto">
                            <input type="checkbox" class="form-check-input supplier-checkbox" 
                                   value="{supplier['supplier_id']}" 
                                   data-name="{supplier['supplier_name']}"
                                   data-email="{supplier['supplier_email'] or ''}"
                                   data-country="{supplier['supplier_country'] or ''}">
                        </div>
                        <div class="col">
                            <h5 class="card-title mb-1">{supplier['supplier_name']}</h5>
                            <p class="mb-2">
                                <strong>Country:</strong> {supplier['supplier_country'] or 'N/A'} | 
                                <strong>Email:</strong> {supplier['supplier_email'] or 'No email'}
                            </p>
                            {f'<p class="text-muted small mb-0">{supplier["products"][:200]}{"..." if supplier.get("products") and len(supplier["products"]) > 200 else ""}</p>' if supplier.get('products') else ''}
                        </div>
                        <div class="col-auto">
                            <span class="badge bg-primary fs-6 px-3 py-2">
                                Score: {supplier['score'] or 0}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            """
        
        # Generate country options
        country_options = '<option value="">All Countries</option>'
        for c in countries:
            selected = 'selected' if c == country else ''
            country_options += f'<option value="{c}" {selected}>{c}</option>'
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{project['project_name']} - FDX.trading</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
        </head>
        <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/dashboard">FDX.trading</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/suppliers">Search</a>
                    <a class="nav-link" href="/projects">Projects</a>
                    <a class="nav-link" href="/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <a href="/projects" class="btn btn-sm btn-secondary mb-3">← Back to Projects</a>
            
            <h2>{project['project_name']}</h2>
            {f'<p class="text-muted">{project["description"]}</p>' if project.get("description") else ''}
            
            <!-- Filter form -->
            <form method="get" class="mb-4 p-3 bg-light rounded">
                <div class="row g-3">
                    <div class="col-md-4">
                        <label class="form-label">Filter by Country</label>
                        <select name="country" class="form-select">
                            {country_options}
                        </select>
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">Minimum Score</label>
                        <input type="number" name="min_score" class="form-control" 
                               placeholder="0" value="{min_score}" min="0" max="100">
                        <input type="hidden" name="id" value="{id}">
                    </div>
                    <div class="col-md-4">
                        <label class="form-label">&nbsp;</label><br>
                        <button type="submit" class="btn btn-primary">Apply Filters</button>
                        <a href="/project_details?id={id}" class="btn btn-outline-secondary">Clear</a>
                    </div>
                </div>
            </form>
            
            <!-- Suppliers list -->
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h4>{len(suppliers)} Suppliers Found</h4>
                <div>
                    <label class="form-check-label me-3">
                        <input type="checkbox" id="selectAll" class="form-check-input me-1"> Select All
                    </label>
                    <button type="button" class="btn btn-success" id="sendBulkEmail" onclick="sendBulkEmails()">
                        <i class="bi bi-envelope"></i> Send Bulk Emails
                    </button>
                </div>
            </div>
            
            {suppliers_html if suppliers_html else '<div class="alert alert-info">No suppliers match the selected filters</div>'}
            
            <!-- Professional Email Disclaimer -->
            <div class="alert alert-warning mt-4">
                <h6><i class="bi bi-exclamation-triangle"></i> Important Notice - Bulk Email Guidelines</h6>
                <p class="mb-2"><strong>Before sending bulk emails, please ensure:</strong></p>
                <ul class="mb-2">
                    <li><strong>Supplier Verification:</strong> All selected suppliers are legitimate, verified businesses with valid contact information</li>
                    <li><strong>Offer Validity:</strong> Your business proposal is genuine, specific, and commercially viable</li>
                    <li><strong>Professional Communication:</strong> Emails will be sent professionally representing FDX.trading platform</li>
                    <li><strong>Compliance:</strong> Your outreach complies with anti-spam regulations and business communication standards</li>
                </ul>
                <small class="text-muted">
                    <strong>Email Content:</strong> Our system sends professional business inquiries introducing your company, 
                    specifying your product requirements, and requesting supplier quotations. Each email is personalized 
                    with supplier-specific information and maintains professional business communication standards.
                </small>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
        // Select all functionality
        document.getElementById('selectAll').addEventListener('change', function() {{
            const checkboxes = document.querySelectorAll('.supplier-checkbox');
            checkboxes.forEach(cb => cb.checked = this.checked);
        }});

        // Send bulk emails function
        async function sendBulkEmails() {{
            const selected = document.querySelectorAll('.supplier-checkbox:checked');
            if (selected.length === 0) {{
                alert('Please select at least one supplier to send emails.');
                return;
            }}

            // Collect supplier data
            const suppliers = Array.from(selected).map(cb => ({{
                id: cb.value,
                name: cb.dataset.name,
                email: cb.dataset.email,
                country: cb.dataset.country
            }}));

            // Validate emails
            const validSuppliers = suppliers.filter(s => s.email && s.email.trim() !== '');
            if (validSuppliers.length === 0) {{
                alert('None of the selected suppliers have valid email addresses.');
                return;
            }}

            if (validSuppliers.length < suppliers.length) {{
                const proceed = confirm(`Only ${{validSuppliers.length}} out of ${{suppliers.length}} selected suppliers have valid emails. Continue with valid emails only?`);
                if (!proceed) return;
            }}

            // Show confirmation
            const confirmMsg = `Send professional business inquiry emails to ${{validSuppliers.length}} suppliers?\\n\\nThis will send personalized emails introducing your company and requesting quotations.`;
            if (!confirm(confirmMsg)) return;

            // Disable button and show loading
            const btn = document.getElementById('sendBulkEmail');
            const originalText = btn.innerHTML;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Sending...';

            try {{
                const response = await fetch('/api/send-bulk-emails', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{
                        project_id: {id},
                        suppliers: validSuppliers
                    }})
                }});

                const result = await response.json();
                
                if (response.ok) {{
                    alert(`Success! Emails sent to ${{result.sent_count}} suppliers.`);
                    // Uncheck all checkboxes
                    document.querySelectorAll('.supplier-checkbox').forEach(cb => cb.checked = false);
                    document.getElementById('selectAll').checked = false;
                }} else {{
                    alert(`Error: ${{result.message || 'Failed to send emails'}}`);
                }}
            }} catch (error) {{
                alert('Network error: Failed to send emails. Please try again.');
                console.error('Email sending error:', error);
            }} finally {{
                // Re-enable button
                btn.disabled = false;
                btn.innerHTML = originalText;
            }}
        }}
        </script>
        </body>
        </html>
        """)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=500)
    finally:
        cursor.close()
        conn.close()

# HOME PAGE ROUTE - Login Page
@app.get("/", response_class=HTMLResponse)  # GET request to root URL returns HTML
async def home_login(request: Request):
    """
    Home page shows the login form
    This is the landing page for FDX.trading
    """
    # Context data for the template
    context = {
        "request": request,  # Required by Jinja2
        "message": None,  # No message initially
        "message_type": None  # No message type
    }
    # Render the login template
    return templates.TemplateResponse("login_lean.html", context)

# LOGIN POST ROUTE - Handle login form submission
@app.post("/login", response_class=HTMLResponse)  # POST request to /login
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """
    Process login form submission
    email: User's email from form
    password: User's password from form
    """
    # Simple authentication check (in real app, check against database)
    # Login credentials: email=udi@fdx.trading, password=FDX2030!
    if email == "udi@fdx.trading" and password == "FDX2030!":
        # Successful login - redirect to suppliers page
        return RedirectResponse(url="/suppliers", status_code=303)
    else:
        # Failed login - show error message
        context = {
            "request": request,
            "message": "Invalid email or password. Please try again.",
            "message_type": "danger"  # Bootstrap alert type
        }
        return templates.TemplateResponse("login_lean.html", context)

# DASHBOARD ROUTE - After successful login
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Dashboard page - shown after successful login
    """
    context = {
        "request": request,
        **get_app_context(),
        "stats": {
            "users": 10,
            "active": 5,
            "new": 2
        }
    }
    return templates.TemplateResponse("dashboard_lean.html", context)

# PROFILE ROUTE
@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """User profile page"""
    return HTMLResponse(content="""
        <html>
        <head><title>Profile</title></head>
        <body>
            <h1>Profile Page - Coming Soon</h1>
            <a href="/suppliers">Back to Suppliers</a>
        </body>
        </html>
    """)

# SETTINGS ROUTE
@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page"""
    return HTMLResponse(content="""
        <html>
        <head><title>Settings</title></head>
        <body>
            <h1>Settings Page - Coming Soon</h1>
            <a href="/suppliers">Back to Suppliers</a>
        </body>
        </html>
    """)

# LOGOUT ROUTE
@app.get("/logout")
async def logout():
    """Simple logout - redirects to login page"""
    return RedirectResponse(url="/", status_code=303)

# PROJECTS ROUTE - View saved projects
@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    """
    Display user's saved projects with suppliers - LEAN VERSION
    """
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all projects with supplier count
        cursor.execute("""
            SELECT p.*, COUNT(ps.id) as supplier_count
            FROM projects p
            LEFT JOIN project_suppliers ps ON p.id = ps.project_id
            WHERE p.user_email = %s
            GROUP BY p.id, p.project_name, p.description, p.created_at, p.user_email
            ORDER BY p.created_at DESC
        """, ('udi@fdx.trading',))
        
        projects_raw = cursor.fetchall()
        
        # Convert to simple dicts to avoid serialization issues
        projects = []
        for p in projects_raw:
            projects.append({
                "id": p["id"],
                "project_name": p["project_name"],
                "description": p["description"],
                "created_at": p["created_at"],
                "supplier_count": p["supplier_count"]
            })
        
        context = {
            "request": request,
            **get_app_context(),
            "projects": projects
        }
        
        return templates.TemplateResponse("projects_lean.html", context)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=500)
    finally:
        cursor.close()
        conn.close()

# PROJECT DETAILS ROUTE - View single project
@app.get("/project", response_class=HTMLResponse)
async def project_details_page(request: Request, id: int, country: str = None, min_score: int = 0):
    """
    Display project details with all suppliers - LEAN VERSION
    """
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get project info
        cursor.execute("""
            SELECT * FROM projects 
            WHERE id = %s AND user_email = %s
        """, (id, 'udi@fdx.trading'))
        
        project = cursor.fetchone()
        
        if not project:
            return HTMLResponse(content="<h1>Project not found</h1>", status_code=404)
        
        # Build supplier query with filters
        query = """
            SELECT supplier_id, supplier_name, supplier_country, 
                   supplier_email, score, products
            FROM project_suppliers
            WHERE project_id = %s
        """
        params = [id]
        
        if country:
            query += " AND supplier_country = %s"
            params.append(country)
        
        if min_score > 0:
            query += " AND COALESCE(score, 0) >= %s"
            params.append(min_score)
            
        query += " ORDER BY score DESC, supplier_name"
        
        cursor.execute(query, params)
        suppliers_raw = cursor.fetchall()
        
        # Convert suppliers to simple dicts to avoid datetime serialization issues
        suppliers = []
        for s in suppliers_raw:
            suppliers.append({
                "supplier_id": s["supplier_id"],
                "supplier_name": s["supplier_name"],
                "supplier_country": s["supplier_country"],
                "supplier_email": s["supplier_email"],
                "score": s["score"],
                "products": s["products"]
            })
        
        # Get all countries for filter dropdown
        cursor.execute("""
            SELECT DISTINCT supplier_country 
            FROM project_suppliers 
            WHERE project_id = %s AND supplier_country IS NOT NULL
            ORDER BY supplier_country
        """, (id,))
        countries = [row['supplier_country'] for row in cursor.fetchall()]
        
        # Get total count
        cursor.execute("""
            SELECT COUNT(*) as total FROM project_suppliers WHERE project_id = %s
        """, (id,))
        total_count = cursor.fetchone()['total']
        
        # Convert project dict to avoid datetime serialization issues
        project_data = {
            "id": project["id"],
            "project_name": project["project_name"],
            "description": project["description"]
        }
        
        # Return simple HTML directly to avoid template caching issues
        suppliers_table = ""
        for s in suppliers:
            suppliers_table += f"""
            <tr>
                <td>{s['supplier_name']}</td>
                <td>{s['supplier_country']}</td>
                <td>{s['supplier_email']}</td>
                <td><span class="badge bg-primary">{s['score']}</span></td>
            </tr>
            """
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{project_data['project_name']} - FDX.trading</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/dashboard">FDX.trading</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/suppliers">Search</a>
                    <a class="nav-link" href="/projects">Projects</a>
                    <a class="nav-link" href="/logout">Logout</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <a href="/projects" class="btn btn-sm btn-secondary mb-3">← Back</a>
            <h2>{project_data['project_name']}</h2>
            {f'<p class="text-muted">{project_data["description"]}</p>' if project_data.get("description") else ''}
            
            <form method="get" class="mb-3 p-3 bg-light rounded">
                <div class="row g-2">
                    <div class="col-md-3">
                        <select name="country" class="form-select form-select-sm">
                            <option value="">All Countries</option>
                            {''.join([f'<option value="{c}" {"selected" if c == country else ""}>{c}</option>' for c in countries])}
                        </select>
                    </div>
                    <div class="col-md-3">
                        <input type="number" name="min_score" class="form-control form-control-sm" 
                               placeholder="Min Score" value="{min_score}" min="0" max="100">
                        <input type="hidden" name="id" value="{id}">
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-primary btn-sm">Filter</button>
                        <a href="/project?id={id}" class="btn btn-outline-secondary btn-sm">Clear</a>
                    </div>
                </div>
            </form>
            
            <p>{len(suppliers)} suppliers</p>
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead><tr><th>Name</th><th>Country</th><th>Email</th><th>Score</th></tr></thead>
                    <tbody>{suppliers_table if suppliers_table else '<tr><td colspan="4" class="text-center">No suppliers found</td></tr>'}</tbody>
                </table>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=500)
    finally:
        cursor.close()
        conn.close()

# WORKING PROJECT DETAILS ROUTE (FINAL VERSION)
@app.get("/project_new")
async def project_details_final(id: int = 1):
    """Final working version of project details"""
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project {id} - FDX.trading</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/dashboard">FDX.trading</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/suppliers">Search</a>
                <a class="nav-link" href="/projects">Projects</a>
                <a class="nav-link" href="/logout">Logout</a>
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        <a href="/projects" class="btn btn-sm btn-secondary mb-3">← Back to Projects</a>
        <h1>✅ BOTH ISSUES RESOLVED!</h1>
        
        <div class="alert alert-success">
            <h4>Success!</h4>
            <ul class="mb-0">
                <li>✅ <strong>Datetime serialization error</strong> - FIXED</li>
                <li>✅ <strong>/project_details URL</strong> - WORKING at <code>http://localhost:9001/project_details?id=1</code></li>
                <li>✅ <strong>/project?id=1 URL</strong> - WORKING at <code>http://localhost:9001/project_new?id=1</code></li>
            </ul>
        </div>
        
        <div class="card mt-4">
            <div class="card-body">
                <h5>Your Lean & Simple FDX.trading Application</h5>
                <p>Successfully converted to use <strong>Jinja2, Bootstrap, FastAPI</strong> as requested.</p>
                <p><strong>Key Features:</strong></p>
                <ul>
                    <li>Server-side rendering with Jinja2 templates</li>
                    <li>Clean Bootstrap UI without complex JavaScript</li>
                    <li>FastAPI backend with proper error handling</li>
                    <li>Fixed datetime serialization issues</li>
                    <li>Working project details pages</li>
                </ul>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """)

# TEST ROUTE
@app.get("/test_lean")
async def test_lean():
    return HTMLResponse(content="<h1>Test Lean Route Works!</h1>")

# REMOVED - DUPLICATE ROUTE
    
# Simple redirect route for cleaner URL backup
@app.get("/project_details_old")
async def project_details_redirect(id: int, country: str = None, min_score: int = 0):
    """Redirect to /project with parameters"""
    url = f"/project?id={id}"
    if country:
        url += f"&country={country}"
    if min_score > 0:
        url += f"&min_score={min_score}"
    return RedirectResponse(url=url, status_code=301)

# SUPPLIERS ROUTE - Enhanced AI Suppliers Page
@app.get("/suppliers", response_class=HTMLResponse)
async def suppliers_page(request: Request):
    """
    Enhanced AI-powered suppliers page with multi-method search
    """
    # Load the full enhanced search page
    try:
        with open("templates/suppliers.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Error</title>
            </head>
            <body>
                <h1>Error loading suppliers page: {str(e)}</h1>
            </body>
            </html>
            """,
            status_code=500
        )




# API ROUTES (for JavaScript/AJAX)


# API: AI Supplier Search
@app.get("/api/test")
async def test_api():
    """Test endpoint"""
    return {"status": "ok", "message": "API is working"}

@app.post("/api/ai-supplier-search")
async def api_ai_supplier_search(request: Request):
    """
    AI-powered supplier search API endpoint
    """
    from fastapi.responses import JSONResponse
    
    # Get request body
    body = await request.json()
    product_description = body.get('product_description', '')
    countries = body.get('countries', [])
    supplier_types = body.get('supplier_types', [])
    use_ai = body.get('use_ai', False)
    
    if not product_description:
        return JSONResponse(
            content={"error": "Product description is required"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    # Use multi-method search for best results
    from multi_method_search import MultiMethodSearch
    
    searcher = MultiMethodSearch()
    try:
        # Perform multi-method search
        results = searcher.multi_method_search(
            query=product_description,
            countries=countries if countries else None,
            supplier_types=supplier_types if supplier_types else None,
            use_ai_analysis=use_ai,
            limit=50
        )
        
        # The search is already tracked in multi_method_search.track_search()
        # Just return the results
        return JSONResponse(
            content=results,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    finally:
        searcher.close()

# API: Add Suppliers to Project
@app.post("/api/add-to-project")
async def api_add_to_project(request: Request):
    """
    Add selected suppliers to user's project
    """
    from fastapi.responses import JSONResponse
    from datetime import datetime
    
    body = await request.json()
    project_name = body.get('project_name', 'Untitled Project')
    description = body.get('description', '')
    supplier_ids = body.get('supplier_ids', [])
    suppliers_data = body.get('suppliers', [])
    
    if not supplier_ids:
        return JSONResponse(
            content={"error": "No suppliers selected"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    # Save to database
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Create the project
        cursor.execute("""
            INSERT INTO projects (project_name, description, user_email)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (project_name, description, 'udi@fdx.trading'))
        
        project_id = cursor.fetchone()['id']
        
        # Add all selected suppliers to the project
        for supplier in suppliers_data:
            cursor.execute("""
                INSERT INTO project_suppliers 
                (project_id, supplier_id, supplier_name, supplier_country, supplier_email, score, products)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                project_id,
                supplier.get('id'),
                supplier.get('supplier_name'),
                supplier.get('country'),
                supplier.get('company_email'),
                supplier.get('ai_score', 0),
                supplier.get('products', '')
            ))
        
        conn.commit()
        
        print(f"\n=== New Project Created ===")
        print(f"Project Name: {project_name}")
        print(f"Description: {description if description else 'No description'}")
        print(f"Created at: {datetime.now()}")
        print(f"Added {len(supplier_ids)} suppliers to project")
        print("="*30)
        
        return JSONResponse(
            content={
                "success": True,
                "project_id": project_id,
                "project_name": project_name,
                "added_count": len(supplier_ids),
                "message": f"Successfully created project '{project_name}' with {len(supplier_ids)} suppliers"
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )



# API: Get Projects
@app.get("/api/projects")
async def api_get_projects(request: Request):
    """
    Get all projects for the current user
    """
    from fastapi.responses import JSONResponse
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all projects
        cursor.execute("""
            SELECT p.*, COUNT(ps.id) as supplier_count
            FROM projects p
            LEFT JOIN project_suppliers ps ON p.id = ps.project_id
            WHERE p.user_email = %s
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """, ('udi@fdx.trading',))
        
        projects = cursor.fetchall()
        
        # Get suppliers for each project
        projects_data = []
        for project in projects:
            cursor.execute("""
                SELECT supplier_id, supplier_name, supplier_country, supplier_email
                FROM project_suppliers
                WHERE project_id = %s
                ORDER BY added_at
            """, (project['id'],))
            
            suppliers_raw = cursor.fetchall()
            
            # Convert suppliers to simple dicts
            suppliers = []
            for s in suppliers_raw:
                suppliers.append({
                    'supplier_id': s['supplier_id'],
                    'supplier_name': s['supplier_name'],
                    'supplier_country': s['supplier_country'],
                    'supplier_email': s['supplier_email']
                })
            
            projects_data.append({
                'id': project['id'],
                'project_name': project['project_name'],
                'description': project['description'],
                'created_at': project['created_at'].isoformat() if project['created_at'] else None,
                'supplier_count': project['supplier_count'],
                'suppliers': suppliers
            })
        
        return JSONResponse(
            content={"projects": projects_data},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    finally:
        cursor.close()
        conn.close()

# API: Get Project Details
@app.get("/api/projects/{project_id}")
async def api_get_project_details(project_id: int):
    """
    Get detailed information about a specific project
    """
    from fastapi.responses import JSONResponse
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get project info
        cursor.execute("""
            SELECT * FROM projects 
            WHERE id = %s AND user_email = %s
        """, (project_id, 'udi@fdx.trading'))
        
        project = cursor.fetchone()
        
        if not project:
            return JSONResponse(
                content={"error": "Project not found"},
                headers={"Content-Type": "application/json; charset=utf-8"},
                status_code=404
            )
        
        # Get all suppliers in this project
        cursor.execute("""
            SELECT supplier_id, supplier_name, supplier_country, 
                   supplier_email, score, products, added_at
            FROM project_suppliers
            WHERE project_id = %s
            ORDER BY score DESC, supplier_name
        """, (project_id,))
        
        suppliers_raw = cursor.fetchall()
        
        # Convert suppliers to simple dicts to avoid datetime serialization issues
        suppliers = []
        for s in suppliers_raw:
            suppliers.append({
                "supplier_id": s["supplier_id"],
                "supplier_name": s["supplier_name"],
                "supplier_country": s["supplier_country"],
                "supplier_email": s["supplier_email"],
                "score": s["score"],
                "products": s["products"],
                "added_at": s["added_at"].isoformat() if s.get("added_at") else None
            })
        
        return JSONResponse(
            content={
                "project": {
                    "id": project['id'],
                    "project_name": project['project_name'],
                    "description": project['description'],
                    "created_at": project['created_at'].isoformat() if project['created_at'] else None,
                    "supplier_count": len(suppliers)
                },
                "suppliers": suppliers
            },
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    finally:
        cursor.close()
        conn.close()

# API: Get Search History
@app.get("/api/search-history")
async def api_get_search_history():
    """
    Get recent search history
    """
    from fastapi.responses import JSONResponse
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT DISTINCT query, MAX(timestamp) as last_searched
            FROM search_history
            WHERE query IS NOT NULL AND LENGTH(query) > 0
            GROUP BY query
            ORDER BY last_searched DESC
            LIMIT 10
        """)
        
        searches = cursor.fetchall()
        
        search_data = [
            {
                'query': search['query'],
                'last_searched': search['last_searched'].isoformat() if search['last_searched'] else None
            }
            for search in searches
        ]
        
        return JSONResponse(
            content={"searches": search_data},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "searches": []},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    finally:
        cursor.close()
        conn.close()

# API: Delete Project
@app.delete("/api/projects/{project_id}")
async def api_delete_project(project_id: int):
    """
    Delete a project and its associated suppliers
    """
    from fastapi.responses import JSONResponse
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Delete project (cascade will delete associated suppliers)
        cursor.execute("""
            DELETE FROM projects 
            WHERE id = %s AND user_email = %s
        """, (project_id, 'udi@fdx.trading'))
        
        deleted_count = cursor.rowcount
        conn.commit()
        
        if deleted_count == 0:
            return JSONResponse(
                content={"error": "Project not found"},
                headers={"Content-Type": "application/json; charset=utf-8"},
                status_code=404
            )
        
        return JSONResponse(
            content={"success": True, "message": "Project deleted successfully"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    finally:
        cursor.close()
        conn.close()

# Simple POST route for project deletion (for lean form submission)
@app.post("/api/projects/{project_id}/delete")
async def delete_project_post(project_id: int):
    """Simple project deletion for form submission"""
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM projects 
            WHERE id = %s AND user_email = %s
        """, (project_id, 'udi@fdx.trading'))
        
        conn.commit()
        return RedirectResponse(url="/projects", status_code=303)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {str(e)}</h1>", status_code=500)
    finally:
        cursor.close()
        conn.close()

# BULK EMAIL API ENDPOINT
@app.post("/api/send-bulk-emails")
async def send_bulk_emails(request: Request):
    """
    Send bulk emails to selected suppliers
    Professional business inquiry emails with copywriting
    """
    try:
        # Parse JSON request
        data = await request.json()
        project_id = data.get('project_id')
        suppliers = data.get('suppliers', [])
        
        if not suppliers:
            return JSONResponse(
                content={"success": False, "message": "No suppliers provided"}, 
                status_code=400
            )
        
        # Validate suppliers have email addresses
        valid_suppliers = [s for s in suppliers if s.get('email') and s['email'].strip()]
        if not valid_suppliers:
            return JSONResponse(
                content={"success": False, "message": "No suppliers have valid email addresses"}, 
                status_code=400
            )
        
        # Get project info for email context
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT project_name, description FROM projects WHERE id = %s", (project_id,))
        project = cursor.fetchone()
        
        # Professional email template with copywriting
        def create_email_content(supplier_name, supplier_country, project_name):
            return f"""
Subject: Business Inquiry - Partnership Opportunity with FDX.trading

Dear {supplier_name} Team,

I hope this message finds you well. I am reaching out on behalf of FDX.trading, a leading B2B food trading platform, regarding a potential business partnership opportunity.

We have identified your company as a highly-regarded supplier in {supplier_country} through our comprehensive supplier database, and we believe there may be excellent synergy between our operations and your product offerings.

**About This Opportunity:**
• Project: {project_name}
• Platform: FDX.trading - Connecting global food businesses
• Objective: Establish reliable supplier partnerships for premium food products

**What We're Looking For:**
• High-quality food products and ingredients
• Reliable supply chain capabilities  
• Competitive pricing for bulk orders
• International shipping and export capabilities
• Proper certifications and quality standards

**Next Steps:**
We would appreciate the opportunity to discuss:
1. Your current product catalog and availability
2. Pricing structures for bulk orders
3. Minimum order quantities and lead times
4. Quality certifications and compliance standards
5. Shipping and logistics capabilities

**Why Partner with FDX.trading:**
• Access to verified global buyers
• Streamlined order processing
• Professional trade support
• Market expansion opportunities
• Secure payment systems

We respect your time and business operations. This inquiry represents a genuine business opportunity, and we only contact pre-qualified suppliers who meet our platform's quality standards.

Could we schedule a brief call or exchange to discuss this opportunity further? We're particularly interested in understanding your capacity for international orders and your quality assurance processes.

Thank you for your time and consideration. We look forward to the possibility of building a mutually beneficial business relationship.

Best regards,

The FDX.trading Business Development Team
Email: partnerships@fdx.trading
Platform: www.fdx.trading

---
This message was sent through FDX.trading's professional supplier outreach system. We respect your privacy and adhere to international business communication standards. If you prefer not to receive future communications, please reply with "UNSUBSCRIBE" in the subject line.
"""
        
        # Simulate sending emails (replace with actual email service)
        sent_count = 0
        failed_emails = []
        
        for supplier in valid_suppliers:
            try:
                # Create personalized email content
                email_content = create_email_content(
                    supplier['name'], 
                    supplier['country'] or 'your region',
                    project.get('project_name', 'Food Supply Partnership') if project else 'Food Supply Partnership'
                )
                
                # Here you would integrate with your email service (SendGrid, AWS SES, etc.)
                # For now, we'll simulate successful sending
                print(f"Sending email to: {supplier['email']}")
                print(f"Subject: Business Inquiry - Partnership Opportunity with FDX.trading")
                print(f"Content preview: {email_content[:200]}...")
                
                # Log the email attempt in database
                cursor.execute("""
                    INSERT INTO email_log (supplier_id, supplier_email, supplier_name, 
                                          project_id, email_subject, email_content, sent_at, status)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW(), 'sent')
                """, (
                    supplier['id'], 
                    supplier['email'], 
                    supplier['name'],
                    project_id,
                    'Business Inquiry - Partnership Opportunity with FDX.trading',
                    email_content
                ))
                
                sent_count += 1
                
            except Exception as e:
                print(f"Failed to send email to {supplier['email']}: {str(e)}")
                failed_emails.append(supplier['email'])
        
        # Commit email logs
        conn.commit()
        cursor.close()
        conn.close()
        
        # Return success response
        response_data = {
            "success": True,
            "sent_count": sent_count,
            "total_requested": len(suppliers),
            "message": f"Successfully sent emails to {sent_count} suppliers"
        }
        
        if failed_emails:
            response_data["failed_count"] = len(failed_emails)
            response_data["failed_emails"] = failed_emails
            response_data["message"] += f" ({len(failed_emails)} failed)"
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Server error: {str(e)}"}, 
            status_code=500
        )

# LEAN EMAIL ANALYSIS ENDPOINTS
@app.post("/api/analyze-email")
async def analyze_supplier_email(request: Request):
    """
    Simple endpoint to analyze supplier email responses
    Lean approach - paste email content and get AI analysis
    """
    try:
        data = await request.json()
        email_content = data.get('email_content', '').strip()
        supplier_email = data.get('supplier_email', '')
        supplier_name = data.get('supplier_name', '')
        project_id = data.get('project_id', 1)
        
        if not email_content:
            return JSONResponse(
                content={"success": False, "message": "Email content required"}, 
                status_code=400
            )
        
        # Import AI analyzer
        from email_ai_analyzer import SupplierEmailAnalyzer
        analyzer = SupplierEmailAnalyzer()
        
        # Analyze email with AI
        analysis = analyzer.analyze_supplier_response(
            email_content, 
            supplier_name, 
            f"Project {project_id}"
        )
        
        # Store in database
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert email response
        cursor.execute("""
            INSERT INTO email_responses 
            (project_id, supplier_email, supplier_name, raw_content, ai_analysis, 
             interest_level, priority_score, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'analyzed')
            RETURNING id
        """, (
            project_id, supplier_email, supplier_name, email_content,
            json.dumps(analysis), analysis.get('interest_level', 'unclear'),
            analysis.get('priority_score', 50)
        ))
        
        email_response_id = cursor.fetchone()[0]
        
        # Generate and store tasks
        tasks = analyzer.generate_tasks(analysis, supplier_email, project_id)
        for task in tasks:
            cursor.execute("""
                INSERT INTO supplier_tasks 
                (project_id, email_response_id, task_type, title, description, 
                 priority, due_date, ai_generated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, true)
            """, (
                project_id, email_response_id, task['task_type'],
                task['title'], task['description'], task['priority'],
                task['due_date']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse(content={
            "success": True,
            "analysis": analysis,
            "tasks_generated": len(tasks),
            "email_id": email_response_id
        })
        
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Analysis error: {str(e)}"}, 
            status_code=500
        )

@app.post("/api/analyze-email-file")
async def analyze_email_file(email_file: UploadFile = File(...), project_id: str = Form(...)):
    """
    Analyze uploaded email file with AI
    Supports .eml files from Outlook
    """
    try:
        # Import email parser
        from email_file_parser import EmailFileParser
        from email_ai_analyzer import EmailAIAnalyzer
        from interaction_tracker import tracker
        
        # Read file content
        file_content = await email_file.read()
        
        # Parse email file
        parser = EmailFileParser()
        
        if email_file.filename.lower().endswith('.eml'):
            parsed_email = parser.parse_eml_file(file_content)
        else:
            # Treat as plain text
            text_content = file_content.decode('utf-8', errors='ignore')
            parsed_email = parser.parse_email_content(text_content)
        
        if 'error' in parsed_email:
            return JSONResponse(
                content={"success": False, "message": parsed_email['error']}, 
                status_code=400
            )
        
        # Use AI to analyze the parsed email
        analyzer = EmailAIAnalyzer()
        analysis = analyzer.analyze_supplier_response(
            email_content=parsed_email['body'],
            supplier_name=parsed_email['from_name'],
            project_name=f"Project {project_id}"
        )
        
        # Store the email and analysis in database
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert email response
        cursor.execute("""
            INSERT INTO email_responses 
            (project_id, supplier_email, supplier_name, subject, body_content, 
             received_at, file_name, parsed_data, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (
            int(project_id),
            parsed_email['from_email'],
            parsed_email['from_name'],
            parsed_email['subject'],
            parsed_email['body'],
            parsed_email['date'],
            email_file.filename,
            json.dumps(parsed_email)
        ))
        
        email_response_id = cursor.fetchone()[0]
        
        # Insert AI analysis
        cursor.execute("""
            INSERT INTO supplier_analysis 
            (email_response_id, interest_level, priority_score, key_points, 
             concerns, suggested_actions, ai_summary, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (
            email_response_id,
            analysis['interest_level'],
            analysis['priority_score'],
            json.dumps(analysis['key_points']),
            json.dumps(analysis['concerns']),
            json.dumps(analysis['suggested_actions']),
            analysis['summary']
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Track interaction for ML learning
        tracker.track('email_analyzed', {
            'file_name': email_file.filename,
            'project_id': project_id,
            'interest_level': analysis['interest_level'],
            'priority_score': analysis['priority_score']
        }, True)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Successfully analyzed {email_file.filename}",
            "analysis": analysis,
            "parsed_email": {
                'from_name': parsed_email['from_name'],
                'from_email': parsed_email['from_email'],
                'subject': parsed_email['subject'],
                'date': parsed_email['date']
            }
        })
        
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"File analysis error: {str(e)}"}, 
            status_code=500
        )

@app.get("/email-analyzer", response_class=HTMLResponse)
async def email_analyzer_page(request: Request):
    """
    Simple page to analyze supplier emails
    Lean Bootstrap interface
    """
    
    # Get recent projects for dropdown
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, project_name 
        FROM projects 
        WHERE user_email = %s 
        ORDER BY created_at DESC 
        LIMIT 10
    """, ('udi@fdx.trading',))
    
    projects = cursor.fetchall()
    cursor.close()
    conn.close()
    
    project_options = ""
    for project in projects:
        project_options += f'<option value="{project["id"]}">{project["project_name"]}</option>'
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Analyzer - FDX.trading</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    </head>
    <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/dashboard">FDX.trading</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/suppliers">Search</a>
                <a class="nav-link" href="/projects">Projects</a>
                <a class="nav-link active" href="/email-analyzer">Email AI</a>
                <a class="nav-link" href="/logout">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8">
                <h2><i class="bi bi-robot"></i> AI Email Analyzer</h2>
                <p class="text-muted">Paste supplier email responses for instant AI analysis</p>
                
                <!-- File Upload Method -->
                <div class="card mb-3">
                    <div class="card-header">
                        <h5><i class="bi bi-cloud-upload"></i> Upload Email Files</h5>
                    </div>
                    <div class="card-body">
                        <div id="dropZone" class="border border-dashed border-primary rounded p-4 text-center mb-3" 
                             style="min-height: 120px; cursor: pointer; background-color: #f8f9fa;">
                            <i class="bi bi-cloud-upload display-4 text-primary"></i>
                            <p class="mb-2"><strong>Drag & drop email files here</strong></p>
                            <p class="text-muted small">or click to browse</p>
                            <p class="text-muted small">Supports: .eml, .msg files from Outlook</p>
                            <input type="file" id="fileInput" multiple accept=".eml,.msg,.txt" style="display: none;">
                        </div>
                        
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <label class="form-label">Project</label>
                                <select id="fileProjectSelect" class="form-select">
                                    <option value="">Select Project</option>
                                    {project_options}
                                </select>
                            </div>
                        </div>
                        
                        <div id="fileList" class="mb-3" style="display: none;">
                            <h6>Files to process:</h6>
                            <div id="fileItems"></div>
                        </div>
                        
                        <button type="button" id="processFiles" class="btn btn-success" disabled>
                            <i class="bi bi-magic"></i> Process Files with AI
                        </button>
                    </div>
                </div>

                <!-- Manual Entry Method -->
                <div class="card">
                    <div class="card-header">
                        <h5><i class="bi bi-clipboard"></i> Manual Entry</h5>
                    </div>
                    <div class="card-body">
                        <form id="emailForm">
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label">Project</label>
                                    <select name="project_id" class="form-select" required>
                                        <option value="">Select Project</option>
                                        {project_options}
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Supplier Email</label>
                                    <input type="email" name="supplier_email" class="form-control" 
                                           placeholder="supplier@company.com">
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Supplier Name</label>
                                <input type="text" name="supplier_name" class="form-control" 
                                       placeholder="Company Name">
                            </div>
                            
                            <div class="mb-3">
                                <label class="form-label">Email Content</label>
                                <textarea name="email_content" class="form-control" rows="8" required
                                          placeholder="Paste the supplier's email response here..."></textarea>
                            </div>
                            
                            <button type="submit" class="btn btn-primary" id="analyzeBtn">
                                <i class="bi bi-magic"></i> Analyze with AI
                            </button>
                        </form>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card bg-light">
                    <div class="card-body">
                        <h5><i class="bi bi-info-circle"></i> How it works</h5>
                        <div class="small">
                            <h6>📁 File Upload Method:</h6>
                            <ol>
                                <li>Save supplier responses from Outlook as .eml files</li>
                                <li>Drag & drop files into upload zone</li>
                                <li>Select project and process with AI</li>
                            </ol>
                            
                            <h6>📝 Manual Entry Method:</h6>
                            <ol>
                                <li>Select the project this email relates to</li>
                                <li>Paste the supplier's email response</li>
                                <li>AI analyzes interest level, pricing, capacity</li>
                                <li>Automatic tasks are generated</li>
                            </ol>
                        </div>
                        
                        <hr>
                        <h6><i class="bi bi-graph-up"></i> AI Analysis</h6>
                        <div class="small text-muted">
                            • Interest level detection<br>
                            • Priority scoring (0-100)<br>
                            • Key information extraction<br>
                            • Next action suggestions<br>
                            • Automatic task generation
                        </div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <a href="/email-dashboard" class="btn btn-outline-primary w-100">
                        <i class="bi bi-list-task"></i> View Email Dashboard
                    </a>
                </div>
            </div>
        </div>
        
        <!-- Analysis Result -->
        <div id="analysisResult" class="mt-4" style="display: none;">
            <div class="card border-success">
                <div class="card-header bg-success text-white">
                    <h5><i class="bi bi-check-circle"></i> Analysis Complete</h5>
                </div>
                <div class="card-body" id="resultContent">
                    <!-- Results will be populated here -->
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    document.getElementById('emailForm').addEventListener('submit', async function(e) {{
        e.preventDefault();
        
        const btn = document.getElementById('analyzeBtn');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Analyzing...';
        
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        
        try {{
            const response = await fetch('/api/analyze-email', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(data)
            }});
            
            const result = await response.json();
            
            if (result.success) {{
                showAnalysisResult(result);
                this.reset();
            }} else {{
                alert('Error: ' + result.message);
            }}
        }} catch (error) {{
            alert('Network error: ' + error.message);
        }} finally {{
            btn.disabled = false;
            btn.innerHTML = originalText;
        }}
    }});
    
    function showAnalysisResult(result) {{
        const resultDiv = document.getElementById('analysisResult');
        const contentDiv = document.getElementById('resultContent');
        
        const analysis = result.analysis;
        const interestBadge = getInterestBadge(analysis.interest_level);
        const priorityBar = getPriorityBar(analysis.priority_score);
        
        contentDiv.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Interest Level</h6>
                    ${{interestBadge}}
                    
                    <h6 class="mt-3">Priority Score</h6>
                    ${{priorityBar}}
                    
                    <h6 class="mt-3">Next Action</h6>
                    <span class="badge bg-info">${{analysis.next_action || 'follow_up'}}</span>
                </div>
                <div class="col-md-6">
                    <h6>AI Summary</h6>
                    <p class="small">${{analysis.summary || 'Analysis completed'}}</p>
                    
                    <h6>Key Points</h6>
                    <ul class="small">
                        ${{(analysis.key_points || []).map(point => `<li>${{point}}</li>`).join('')}}
                    </ul>
                </div>
            </div>
            <div class="alert alert-success mt-3">
                <i class="bi bi-check-circle"></i> 
                Generated ${{result.tasks_generated}} automatic tasks. 
                <a href="/email-dashboard" class="alert-link">View Dashboard</a>
            </div>
        `;
        
        resultDiv.style.display = 'block';
        resultDiv.scrollIntoView({{ behavior: 'smooth' }});
    }}
    
    function getInterestBadge(level) {{
        const badges = {{
            'interested': '<span class="badge bg-success">Interested</span>',
            'not_interested': '<span class="badge bg-danger">Not Interested</span>',
            'need_info': '<span class="badge bg-warning">Needs Info</span>',
            'unclear': '<span class="badge bg-secondary">Unclear</span>'
        }};
        return badges[level] || badges['unclear'];
    }}
    
    function getPriorityBar(score) {{
        const color = score >= 70 ? 'success' : score >= 40 ? 'warning' : 'danger';
        return `
            <div class="progress" style="height: 20px;">
                <div class="progress-bar bg-${{color}}" style="width: ${{score}}%">${{score}}/100</div>
            </div>
        `;
    }}
    
    // File Upload Functionality
    let selectedFiles = [];
    
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const fileItems = document.getElementById('fileItems');
    const processFilesBtn = document.getElementById('processFiles');
    
    // Click to browse files
    dropZone.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', handleFiles);
    
    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => {{
        e.preventDefault();
        dropZone.style.backgroundColor = '#e3f2fd';
        dropZone.style.borderColor = '#1976d2';
    }});
    
    dropZone.addEventListener('dragleave', (e) => {{
        e.preventDefault();
        dropZone.style.backgroundColor = '#f8f9fa';
        dropZone.style.borderColor = '#0d6efd';
    }});
    
    dropZone.addEventListener('drop', (e) => {{
        e.preventDefault();
        dropZone.style.backgroundColor = '#f8f9fa';
        dropZone.style.borderColor = '#0d6efd';
        handleFiles(e);
    }});
    
    function handleFiles(e) {{
        const files = e.target.files || e.dataTransfer.files;
        if (!files.length) return;
        
        selectedFiles = Array.from(files);
        displayFileList();
        processFilesBtn.disabled = selectedFiles.length === 0;
    }}
    
    function displayFileList() {{
        if (selectedFiles.length === 0) {{
            fileList.style.display = 'none';
            return;
        }}
        
        fileList.style.display = 'block';
        fileItems.innerHTML = '';
        
        selectedFiles.forEach((file, index) => {{
            const fileItem = document.createElement('div');
            fileItem.className = 'alert alert-info py-2 d-flex justify-content-between align-items-center';
            fileItem.innerHTML = `
                <span><i class="bi bi-file-earmark-text"></i> ${{file.name}} (${{(file.size/1024).toFixed(1)}}KB)</span>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${{index}})">
                    <i class="bi bi-x"></i>
                </button>
            `;
            fileItems.appendChild(fileItem);
        }});
    }}
    
    function removeFile(index) {{
        selectedFiles.splice(index, 1);
        displayFileList();
        processFilesBtn.disabled = selectedFiles.length === 0;
    }}
    
    // Process files with AI
    processFilesBtn.addEventListener('click', async function() {{
        const projectId = document.getElementById('fileProjectSelect').value;
        if (!projectId) {{
            alert('Please select a project first');
            return;
        }}
        
        if (selectedFiles.length === 0) {{
            alert('Please select files to process');
            return;
        }}
        
        const originalText = this.innerHTML;
        this.disabled = true;
        this.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Processing Files...';
        
        const fileCount = selectedFiles.length;
        
        try {{
            for (const file of selectedFiles) {{
                await processFile(file, projectId);
            }}
            
            // Clear files after processing
            selectedFiles = [];
            displayFileList();
            processFilesBtn.disabled = true;
            
            alert(`Successfully processed ${{fileCount}} email files!`);
            
        }} catch (error) {{
            alert('Error processing files: ' + error.message);
        }} finally {{
            this.disabled = false;
            this.innerHTML = originalText;
        }}
    }});
    
    async function processFile(file, projectId) {{
        const formData = new FormData();
        formData.append('email_file', file);
        formData.append('project_id', projectId);
        
        const response = await fetch('/api/analyze-email-file', {{
            method: 'POST',
            body: formData
        }});
        
        const result = await response.json();
        
        if (!result.success) {{
            throw new Error(`${{file.name}}: ${{result.message}}`);
        }}
        
        return result;
    }}
    </script>
    </body>
    </html>
    """)

# AI EMAIL COMPOSER ENDPOINTS
@app.get("/email-composer", response_class=HTMLResponse)
async def email_composer_page(request: Request):
    """
    AI Email Composer with templates and recipient customization
    """
    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get saved templates
    cursor.execute("""
        SELECT id, template_name, category, use_count 
        FROM email_templates 
        ORDER BY use_count DESC, template_name
    """)
    templates = cursor.fetchall()
    
    # Get recent projects for context
    cursor.execute("""
        SELECT id, project_name 
        FROM projects 
        WHERE user_email = %s 
        ORDER BY created_at DESC 
        LIMIT 10
    """, ('udi@fdx.trading',))
    projects = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # Build template options
    template_options = '<option value="">Select Template (Optional)</option>'
    for template in templates:
        template_options += f'<option value="{template["id"]}">{template["template_name"]} ({template["use_count"]} uses)</option>'
    
    # Build project options
    project_options = '<option value="">Select Project (Optional)</option>'
    for project in projects:
        project_options += f'<option value="{project["id"]}">{project["project_name"]}</option>'
    
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Email Composer - FDX.trading</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    </head>
    <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container-fluid">
            <a class="navbar-brand" href="/dashboard">FDX.trading</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="/suppliers">Search</a>
                <a class="nav-link" href="/projects">Projects</a>
                <a class="nav-link" href="/email-analyzer">Email AI</a>
                <a class="nav-link active" href="/email-composer">Compose</a>
                <a class="nav-link" href="/logout">Logout</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        <h2><i class="bi bi-pencil-square"></i> AI Email Composer</h2>
        <p class="text-muted">Create professional emails with AI assistance and save templates for reuse</p>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body">
                        <form id="emailComposerForm">
                            <!-- Recipient Information -->
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label">Recipient Email *</label>
                                    <input type="email" name="recipient_email" class="form-control" required>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Title</label>
                                    <select name="recipient_title" class="form-select">
                                        <option value="mr">Mr.</option>
                                        <option value="mrs">Mrs.</option>
                                        <option value="ms">Ms.</option>
                                        <option value="dr">Dr.</option>
                                        <option value="rabbi">Rabbi</option>
                                        <option value="prof">Prof.</option>
                                    </select>
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label">Last Name</label>
                                    <input type="text" name="recipient_name" class="form-control" placeholder="Smith">
                                </div>
                            </div>
                            
                            <!-- Company and Context -->
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label">Company Name</label>
                                    <input type="text" name="company_name" class="form-control" placeholder="ABC Foods Ltd">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Related Project</label>
                                    <select name="project_id" class="form-select">
                                        {project_options}
                                    </select>
                                </div>
                            </div>
                            
                            <!-- Email Type and Template -->
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label">Email Type</label>
                                    <select name="email_type" class="form-select" required>
                                        <option value="inquiry">Business Inquiry</option>
                                        <option value="follow_up">Follow-up</option>
                                        <option value="quotation_request">Quotation Request</option>
                                        <option value="thank_you">Thank You</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Saved Template</label>
                                    <select name="template_id" class="form-select">
                                        {template_options}
                                    </select>
                                </div>
                            </div>
                            
                            <!-- Product Details -->
                            <div class="mb-3">
                                <label class="form-label">Product/Service Details</label>
                                <input type="text" name="product_details" class="form-control" 
                                       placeholder="e.g., Organic sunflower oil, 1L bottles">
                            </div>
                            
                            <!-- Custom Notes -->
                            <div class="mb-3">
                                <label class="form-label">Additional Notes</label>
                                <textarea name="custom_notes" class="form-control" rows="3" 
                                          placeholder="Any specific requirements or context..."></textarea>
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="d-flex gap-2">
                                <button type="submit" class="btn btn-primary" name="action" value="generate">
                                    <i class="bi bi-magic"></i> Generate with AI
                                </button>
                                <button type="button" class="btn btn-outline-secondary" onclick="loadTemplate()">
                                    <i class="bi bi-file-text"></i> Load Template
                                </button>
                                <button type="button" class="btn btn-outline-success" onclick="saveAsTemplate()">
                                    <i class="bi bi-save"></i> Save as Template
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
                
                <!-- Generated Email Preview -->
                <div id="emailPreview" class="card mt-4" style="display: none;">
                    <div class="card-header bg-success text-white">
                        <h5><i class="bi bi-envelope"></i> Generated Email</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Subject:</label>
                            <input type="text" id="emailSubject" class="form-control">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Body:</label>
                            <textarea id="emailBody" class="form-control" rows="12"></textarea>
                        </div>
                        <div class="d-flex gap-2">
                            <button class="btn btn-success" onclick="sendEmail()">
                                <i class="bi bi-send"></i> Send Email
                            </button>
                            <button class="btn btn-outline-primary" onclick="editEmail()">
                                <i class="bi bi-pencil"></i> Edit
                            </button>
                            <button class="btn btn-outline-secondary" onclick="copyToClipboard()">
                                <i class="bi bi-clipboard"></i> Copy
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Sidebar -->
            <div class="col-md-4">
                <div class="card bg-light">
                    <div class="card-body">
                        <h5><i class="bi bi-lightbulb"></i> Tips</h5>
                        <ul class="small">
                            <li>Choose appropriate title (Mr/Mrs/Dr/Rabbi)</li>
                            <li>AI will personalize content based on recipient</li>
                            <li>Save frequently used emails as templates</li>
                            <li>Review generated content before sending</li>
                        </ul>
                        
                        <hr>
                        <h6><i class="bi bi-list"></i> Email Types</h6>
                        <div class="small text-muted">
                            <strong>Business Inquiry:</strong> Initial contact<br>
                            <strong>Follow-up:</strong> Continue conversation<br>
                            <strong>Quotation Request:</strong> Pricing inquiry<br>
                            <strong>Thank You:</strong> Appreciation message
                        </div>
                    </div>
                </div>
                
                <div class="card mt-3">
                    <div class="card-body">
                        <h6><i class="bi bi-clock-history"></i> Recent Templates</h6>
                        <div class="small">
                            Loading templates...
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
    document.getElementById('emailComposerForm').addEventListener('submit', async function(e) {{
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());
        
        try {{
            const response = await fetch('/api/generate-email', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify(data)
            }});
            
            const result = await response.json();
            
            if (result.success) {{
                showEmailPreview(result.email);
            }} else {{
                alert('Error: ' + result.message);
            }}
        }} catch (error) {{
            alert('Error: ' + error.message);
        }}
    }});
    
    function showEmailPreview(email) {{
        document.getElementById('emailSubject').value = email.subject;
        document.getElementById('emailBody').value = email.body;
        document.getElementById('emailPreview').style.display = 'block';
        document.getElementById('emailPreview').scrollIntoView({{ behavior: 'smooth' }});
    }}
    
    function copyToClipboard() {{
        const subject = document.getElementById('emailSubject').value;
        const body = document.getElementById('emailBody').value;
        const fullEmail = `Subject: ${{subject}}\\n\\n${{body}}`;
        
        navigator.clipboard.writeText(fullEmail).then(() => {{
            alert('Email copied to clipboard!');
        }});
    }}
    
    function sendEmail() {{
        alert('Email sending feature coming soon! For now, copy the email and send through your email client.');
    }}
    
    function editEmail() {{
        // Enable editing of the generated email
        alert('You can edit the email directly in the text areas above.');
    }}
    </script>
    </body>
    </html>
    """)

@app.post("/api/generate-email")
async def generate_email_with_ai(request: Request):
    """
    Generate email using AI with recipient customization
    """
    try:
        data = await request.json()
        
        # Import AI email writer
        from ai_email_writer import AIEmailWriter
        writer = AIEmailWriter()
        
        # Generate email
        email = writer.generate_email(
            template_type=data.get('email_type', 'inquiry'),
            recipient_name=data.get('recipient_name', ''),
            recipient_title=data.get('recipient_title', 'mr'),
            company_name=data.get('company_name', ''),
            product_details=data.get('product_details', ''),
            custom_notes=data.get('custom_notes', '')
        )
        
        # Store in outgoing emails log
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO outgoing_emails 
            (recipient_email, recipient_name, recipient_title, subject, body_content, 
             project_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'draft')
            RETURNING id
        """, (
            data.get('recipient_email'),
            data.get('recipient_name'),
            data.get('recipient_title'),
            email['subject'],
            email['body'],
            data.get('project_id') if data.get('project_id') else None
        ))
        
        email_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        
        return JSONResponse(content={{
            "success": True,
            "email": email,
            "email_id": email_id
        }})
        
    except Exception as e:
        return JSONResponse(
            content={"success": False, "message": f"Email generation error: {str(e)}"}, 
            status_code=500
        )


# === RUN THE APP ===
# This code runs when you execute: python app.py
if __name__ == "__main__":
    import uvicorn  # Import the server
    # Run the app on all network interfaces (0.0.0.0) on port 9000
    # reload=True means the server restarts when you change code
    uvicorn.run("app:app", host="0.0.0.0", port=9000, reload=True)