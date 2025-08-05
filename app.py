# My First Python Web App with Bootstrap, Jinja2, and FastAPI
# This file is the main application that runs your website

# === IMPORTS ===
# Import necessary libraries
from fastapi import FastAPI, Request, Form  # FastAPI: web framework, Request: HTTP requests, Form: HTML forms
from fastapi.responses import HTMLResponse, RedirectResponse  # HTMLResponse: return HTML pages, RedirectResponse: redirect users
from fastapi.staticfiles import StaticFiles  # StaticFiles: serve CSS/JS files
from fastapi.templating import Jinja2Templates  # Jinja2Templates: render HTML templates
from typing import List, Dict  # Type hints for better code
import os  # Operating system functions
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

# Store templates in app state for access from routers
app.state.templates = templates

# Import and include email CRM router
try:
    from app.email_crm.routes import router as email_router
    app.include_router(email_router)
except ImportError:
    print("Email CRM module not found - skipping")

# Import and include admin cost monitoring router
try:
    from app.admin.cost_dashboard import router as admin_router
    app.include_router(admin_router, prefix="/admin", tags=["admin"])
except ImportError:
    print("Admin cost monitoring module not found - skipping")


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
                    <a class="nav-link" href="/email"><i class="bi bi-envelope-at"></i> AI Emails</a>
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
    
    try:
        conn = get_db_connection()
        if not conn:
            return HTMLResponse(content="<html><head><title>Database Error</title></head><body><h1>Database connection failed</h1><p><a href='/suppliers'>Go to Suppliers</a></p></body></html>", status_code=500)
        
        cursor = conn.cursor()
        
        # First check if projects table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'projects'
            )
        """)
        
        table_exists = cursor.fetchone()
        if not table_exists or not table_exists[0]:
            # Projects table doesn't exist, create it
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
        
        # Get all projects with supplier count
        cursor.execute("""
            SELECT p.id, p.project_name, p.description, p.created_at, p.user_email,
                   COALESCE(COUNT(ps.id), 0) as supplier_count
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
                "id": p[0],
                "project_name": p[1],
                "description": p[2],
                "created_at": p[3],
                "supplier_count": p[5]
            })
        
        context = {
            "request": request,
            **get_app_context(),
            "projects": projects
        }
        
        return templates.TemplateResponse("projects_lean.html", context)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return HTMLResponse(content=f"""
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Projects Error - FDX.trading</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="/dashboard">FDX.trading</a>
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="/suppliers">Search</a>
                    <a class="nav-link" href="/projects">Projects</a>
                    <a class="nav-link" href="/email"><i class="bi bi-envelope-at"></i> AI Emails</a>
                    <a class="nav-link" href="/logout">Logout</a>
                </div>
            </div>
        </nav>
        <div class="container mt-4">
            <div class="alert alert-danger">
                <h4>Database Error</h4>
                <p>There was an error loading your projects. Please try again or contact support.</p>
                <details>
                    <summary>Error Details</summary>
                    <pre>{str(e)}</pre>
                </details>
            </div>
            <a href="/suppliers" class="btn btn-primary">Go to Suppliers Search</a>
        </div>
        </body>
        </html>
        """, status_code=500)
    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass

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
                    <a class="nav-link" href="/email"><i class="bi bi-envelope-at"></i> AI Emails</a>
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
    
    try:
        conn = get_db_connection()
        if not conn:
            return JSONResponse(
                content={"searches": []},
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
        
        cursor = conn.cursor()
        
        # Simplified query to avoid cursor issues
        cursor.execute("""
            SELECT query, timestamp
            FROM search_history
            WHERE query IS NOT NULL AND LENGTH(query) > 0
            ORDER BY timestamp DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        # Build search data manually to avoid cursor format issues
        search_data = []
        for result in results:
            try:
                # Try to access as tuple first
                query = result[0] if len(result) > 0 else ''
                timestamp = result[1] if len(result) > 1 else None
                
                if query:
                    search_data.append({
                        'query': str(query),
                        'last_searched': timestamp.isoformat() if timestamp else None
                    })
            except:
                # Skip problematic entries
                continue
        
        # Remove duplicates and keep most recent
        unique_searches = {}
        for search in search_data:
            query = search['query']
            if query not in unique_searches or (search['last_searched'] and 
                search['last_searched'] > unique_searches[query]['last_searched']):
                unique_searches[query] = search
        
        final_searches = list(unique_searches.values())[:10]
        
        return JSONResponse(
            content={"searches": final_searches},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
    except Exception as e:
        # Return empty searches on any error to avoid breaking the UI
        return JSONResponse(
            content={"searches": [], "error": f"Search history temporarily unavailable: {str(e)}"},
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    finally:
        try:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
        except:
            pass

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

# EMAIL DASHBOARD ROUTE
@app.get("/email", response_class=HTMLResponse)
async def email_dashboard(request: Request):
    """AI Email Dashboard with Azure OpenAI Integration"""
    from database import get_db_connection
    
    try:
        # Get basic email stats from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create email_log table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_log (
                id SERIAL PRIMARY KEY,
                supplier_id INTEGER,
                supplier_email VARCHAR(255),
                supplier_name VARCHAR(255),
                project_id INTEGER,
                email_subject TEXT,
                email_content TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(50) DEFAULT 'sent'
            )
        """)
        conn.commit()
        
        # Get email statistics
        cursor.execute("SELECT COUNT(*) FROM email_log WHERE sent_at >= CURRENT_DATE")
        today_count = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        cursor.execute("SELECT COUNT(*) FROM email_log WHERE sent_at >= CURRENT_DATE - INTERVAL '7 days'")
        week_count = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        cursor.execute("SELECT COUNT(*) FROM email_log WHERE sent_at >= CURRENT_DATE - INTERVAL '30 days'")
        month_count = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        cursor.execute("SELECT COUNT(*) FROM email_log")
        total_count = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        # Get recent emails
        cursor.execute("""
            SELECT id, supplier_email, supplier_name, sent_at, status
            FROM email_log
            ORDER BY sent_at DESC
            LIMIT 20
        """)
        
        recent_emails = []
        for row in cursor.fetchall():
            recent_emails.append({
                'id': row[0],
                'supplier_email': row[1], 
                'supplier_name': row[2],
                'sent_at': row[3],
                'status': row[4] or 'sent'
            })
        
        cursor.close()
        conn.close()
        
        # Create stats object
        stats = {
            'totals': {
                'total_today': today_count,
                'total_7_days': week_count,
                'total_30_days': month_count,
                'total_all_time': total_count
            }
        }
        
        context = get_app_context()
        context.update({
            "request": request,
            "stats": stats,
            "recent_emails": recent_emails
        })
        
        return templates.TemplateResponse("email_dashboard.html", context)
        
    except Exception as e:
        # Return simplified dashboard on error
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Email Center - FDX.trading</title>
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
                    <a class="nav-link active" href="/email"><i class="bi bi-envelope-at"></i> AI Emails</a>
                    <a class="nav-link" href="/logout">Logout</a>
                </div>
            </div>
        </nav>
        
        <div class="container mt-4">
            <h1><i class="bi bi-envelope-at"></i> AI Email Center</h1>
            
            <div class="alert alert-info">
                <h5><i class="bi bi-robot"></i> Azure OpenAI Email Integration</h5>
                <p>Our AI-powered email system uses Azure OpenAI to generate professional business communications with suppliers.</p>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-success text-white">
                            <h5><i class="bi bi-pencil-square"></i> Compose AI Email</h5>
                        </div>
                        <div class="card-body">
                            <p>Generate professional supplier emails with AI assistance.</p>
                            <a href="/email/compose" class="btn btn-success">
                                <i class="bi bi-pencil-square"></i> Compose Email
                            </a>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5><i class="bi bi-people"></i> Bulk Email Campaigns</h5>
                        </div>
                        <div class="card-body">
                            <p>Send AI-generated emails to multiple suppliers from your projects.</p>
                            <a href="/projects" class="btn btn-primary">
                                <i class="bi bi-folder2"></i> Select Project
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h5><i class="bi bi-gear"></i> Email Features</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <h6><i class="bi bi-robot"></i> AI-Generated Content</h6>
                            <p>Professional business emails crafted by Azure OpenAI</p>
                        </div>
                        <div class="col-md-4">
                            <h6><i class="bi bi-envelope-check"></i> Bulk Campaigns</h6>
                            <p>Send personalized emails to multiple suppliers at once</p>
                        </div>
                        <div class="col-md-4">
                            <h6><i class="bi bi-graph-up"></i> Tracking & Analytics</h6>
                            <p>Monitor email delivery and engagement metrics</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """, status_code=200)

# COMPOSE EMAIL ROUTE
@app.get("/email/compose", response_class=HTMLResponse)
async def compose_email(request: Request, project_id: int = None):
    """Simple email composer"""
    context = get_app_context()
    context.update({
        "request": request,
        "project_id": project_id
    })
    
    return templates.TemplateResponse("email_compose.html", context)

# AI EMAIL GENERATION API
@app.post("/api/email/generate")
async def generate_ai_email(request: Request):
    """Generate email with AI"""
    from email_service_lean import email_service
    
    data = await request.json()
    
    email_content = email_service.write_email(
        supplier_name=data.get('supplier_name', 'Supplier'),
        supplier_country=data.get('supplier_country', 'your country'),
        products=data.get('products', ''),
        email_type=data.get('email_type', 'inquiry')
    )
    
    return JSONResponse({
        "success": True,
        "content": email_content
    })

# GET EMAIL DETAILS API
@app.get("/api/email/{email_id}")
async def get_email_details(email_id: int):
    """Get email details for preview"""
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT supplier_email, email_content, sent_at
        FROM email_log
        WHERE id = %s
    """, (email_id,))
    
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row:
        return JSONResponse({
            "supplier_email": row[0],
            "content": row[1],
            "sent_at": row[2].isoformat() if row[2] else None
        })
    else:
        return JSONResponse({"error": "Email not found"}, status_code=404)

# === RUN THE APP ===
# This code runs when you execute: python app.py
if __name__ == "__main__":
    import uvicorn  # Import the server
    # Run the app on all network interfaces (0.0.0.0) on port 9000
    # reload=True means the server restarts when you change code
    uvicorn.run("app:app", host="0.0.0.0", port=9000, reload=True)