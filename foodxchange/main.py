"""
FoodXchange - AI-Powered B2B Food Sourcing Platform
Main FastAPI application with integrated product analysis system
"""

import os
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
from pathlib import Path
import logging
logging.basicConfig(level=logging.INFO)
early_logger = logging.getLogger("env_loader")

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)
early_logger.info(f"Loading .env from: {env_path.absolute()}")
early_logger.info(f"AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT', 'NOT SET')}")
early_logger.info(f".env exists: {env_path.exists()}")

from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import json
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FoodXchange",
    description="AI-Powered B2B Food Sourcing Platform",
    version="1.0.0"
)

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8003",
        "https://foodxchange.com",
        "https://app.foodxchange.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Add rate limiting middleware
try:
    from foodxchange.middleware.rate_limiting import rate_limit_middleware
    app.middleware("http")(rate_limit_middleware)
    logger.info("✅ Rate limiting middleware added")
except ImportError as e:
    logger.warning(f"Rate limiting middleware not available: {e}")

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing and context"""
    import time
    import uuid
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Get user ID from session if available
    user_id = request.session.get("user_id") if hasattr(request, 'session') else None
    
    # Start timing
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request
        logger.info(
            f"Request completed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "user_agent": request.headers.get("user-agent", ""),
                "ip_address": request.client.host if request.client else "unknown"
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Calculate duration
        duration = time.time() - start_time
        
        # Log error
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "method": request.method,
                "url": str(request.url),
                "duration_ms": round(duration * 1000, 2),
                "error": str(e),
                "user_agent": request.headers.get("user-agent", ""),
                "ip_address": request.client.host if request.client else "unknown"
            }
        )
        raise

# Get the directory where main.py is located
BASE_DIR = Path(__file__).resolve().parent

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Configure Jinja2 templates with custom functions
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Add custom template functions
def url_for(name: str, **path_params) -> str:
    """Simple URL builder for templates"""
    routes = {
        "static": "/static",
        "landing": "/",
        "dashboard": "/dashboard",
        "product_analysis": "/product-analysis/",
        "login_page": "/login",
        "projects": "/projects",
        "suppliers": "/suppliers",
        "buyers": "/buyers",
        "simple_login": "/auth/login",
        "admin_login": "/admin",
        "dashboard.index": "/dashboard",
        "data_import.import_page": "/import/",
        "data_import.preview_import": "/import/preview",
        "data_import.process_import": "/import/process",
        "data_import.download_template": "/import/template/",
        "data_import.import_history": "/import/history",
        "data_import.import_details": "/import/details/",
        "profile": "/profile/",
        "profile_edit": "/profile/edit",
        "profile_settings": "/profile/settings"
    }
    
    if name == "static" and "filename" in path_params:
        return f"/static/{path_params['filename']}"
    
    # Handle routes with path parameters
    base_route = routes.get(name, "/")
    
    # Replace path parameters in the route
    for param, value in path_params.items():
        base_route = base_route.replace(f"{{{param}}}", str(value))
    
    return base_route

# Add url_for to template globals
templates.env.globals["url_for"] = url_for

# Simple database session mock (replace with actual database)
def get_db():
    return None

def get_current_user_context(request: Request, db=None):
    return None

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring and load balancers"""
    import redis
    from datetime import datetime
    import psutil
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": app.version,
        "services": {}
    }
    
    # Check Redis connection
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        redis_info = r.info()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "memory": redis_info.get("used_memory_human", "unknown"),
            "connected_clients": redis_info.get("connected_clients", 0)
        }
    except Exception as e:
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check system resources
    try:
        health_status["resources"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    except:
        health_status["resources"] = {"status": "unavailable"}
    
    # Check AI services configuration
    azure_configured = all([
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    ])
    
    health_status["services"]["azure_ai"] = {
        "status": "configured" if azure_configured else "not_configured"
    }
    
    # Overall status
    if any(service.get("status") == "unhealthy" for service in health_status["services"].values()):
        health_status["status"] = "unhealthy"
    
    return health_status

# Simple login handler (temporary - bypasses database)
@app.post("/auth/login")
async def simple_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Simple login that works without database - defaults to admin"""
    # Validate input
    if not email or not password:
        return RedirectResponse(url="/login?error=missing_credentials", status_code=303)
    
    if len(email) < 3 or len(password) < 6:
        return RedirectResponse(url="/login?error=invalid_input", status_code=303)
    
    # Development login - accept any email/password and log in as admin
    if email and password:
        # Create session data
        request.session["user_id"] = 1
        request.session["email"] = email
        request.session["is_admin"] = True
        request.session["login_time"] = datetime.now().isoformat()
        
        # Redirect to dashboard as admin
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        return RedirectResponse(url="/login?error=Invalid+credentials", status_code=303)

# Auto-login route for admin access
@app.get("/admin")
async def admin_login():
    """Direct admin access - bypasses login form"""
    return RedirectResponse(url="/dashboard", status_code=303)

# Import and include route modules
try:
    # Make templates available globally before importing routes
    import sys
    sys.path.append(str(BASE_DIR))
    sys.path.append(str(BASE_DIR.parent))  # Add parent directory to path
    
    from foodxchange.routes import product_analysis_routes, data_import_routes, azure_testing_routes_fastapi, search_routes
    
    # Include routers
    app.include_router(product_analysis_routes.router)
    app.include_router(data_import_routes.router)
    app.include_router(azure_testing_routes_fastapi.router)
    app.include_router(search_routes.router)
    
    logger.info("✅ Core route modules loaded successfully")
    
except ImportError as e:
    logger.warning(f"⚠️ Some route modules could not be loaded: {e}")

# Try to load additional routes that might have dependencies
try:
    from foodxchange.routes import error_routes, help_routes
    app.include_router(error_routes.router)
    app.include_router(help_routes.router)
    logger.info("✅ Optional route modules loaded successfully")
except ImportError as e:
    logger.info(f"Optional routes not loaded: {e}")

# Add profile routes directly to avoid import issues
from fastapi import APIRouter, Form, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse
import shutil
from typing import Optional
from datetime import datetime

profile_router = APIRouter(prefix="/profile", tags=["profile"])

# Mock user data
MOCK_USER = {
    "id": 1,
    "name": "Admin User",
    "email": "admin@foodxchange.com",
    "company": "FoodXchange Inc.",
    "role": "admin",
    "is_active": True,
    "is_admin": True,
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
    "phone": "+1 234 567 8900",
    "country": "United States",
    "city": "New York",
    "address": "123 Business St, Suite 100",
    "bio": "Experienced food industry professional with over 10 years in B2B sourcing and supply chain management.",
    "profile_picture": None,
    "job_title": "Senior Sourcing Manager",
    "department": "Operations",
    "industry": "Food & Beverage",
    "company_size": "51-200",
    "website": "https://foodxchange.com",
    "linkedin": "https://linkedin.com/in/adminuser",
    "timezone": "America/New_York",
    "language": "en"
}

class MockUser:
    def __init__(self, data):
        for key, value in data.items():
            setattr(self, key, value)

@profile_router.get("/")
async def profile_page(request: Request):
    """Display user profile page"""
    user = MockUser(MOCK_USER)
    return templates.TemplateResponse("pages/profile.html", {
        "request": request,
        "user": user,
        "current_user": {"name": user.name, "email": user.email, "is_admin": user.is_admin}
    })

@profile_router.get("/edit")
async def edit_profile_page(request: Request):
    """Display profile edit page"""
    user = MockUser(MOCK_USER)
    return templates.TemplateResponse("pages/profile_edit.html", {
        "request": request,
        "user": user,
        "current_user": {"name": user.name, "email": user.email, "is_admin": user.is_admin}
    })

@profile_router.get("/settings")
async def profile_settings_page(request: Request):
    """Display profile settings page"""
    user = MockUser(MOCK_USER)
    return templates.TemplateResponse("pages/profile_settings.html", {
        "request": request,
        "user": user,
        "current_user": {"name": user.name, "email": user.email, "is_admin": user.is_admin}
    })

@profile_router.post("/update")
async def update_profile(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    country: Optional[str] = Form(None),
    city: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    job_title: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    industry: Optional[str] = Form(None),
    company_size: Optional[str] = Form(None),
    website: Optional[str] = Form(None),
    linkedin: Optional[str] = Form(None),
    timezone: Optional[str] = Form(None),
    language: Optional[str] = Form(None)
):
    """Update user profile"""
    MOCK_USER.update({
        "name": name,
        "email": email,
        "phone": phone,
        "country": country,
        "city": city,
        "address": address,
        "bio": bio,
        "job_title": job_title,
        "department": department,
        "industry": industry,
        "company_size": company_size,
        "website": website,
        "linkedin": linkedin,
        "timezone": timezone or "UTC",
        "language": language or "en",
        "updated_at": datetime.now()
    })
    return JSONResponse(content={"success": True, "message": "Profile updated successfully"})

@profile_router.post("/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Change user password with proper validation"""
    try:
        # Check if user is authenticated
        user_id = request.session.get("user_id")
        if not user_id:
            return JSONResponse(content={
                "success": False,
                "message": "Authentication required"
            }, status_code=401)
        
        # Validate input
        if not current_password or not new_password or not confirm_password:
            return JSONResponse(content={
                "success": False,
                "message": "All password fields are required"
            }, status_code=400)
        
        # Validate password strength
        if len(new_password) < 8:
            return JSONResponse(content={
                "success": False,
                "message": "New password must be at least 8 characters long"
            }, status_code=400)
        
        # Check if passwords match
        if new_password != confirm_password:
            return JSONResponse(content={
                "success": False,
                "message": "New passwords do not match"
            }, status_code=400)
        
        # Check if new password is different from current
        if current_password == new_password:
            return JSONResponse(content={
                "success": False,
                "message": "New password must be different from current password"
            }, status_code=400)
        
        # In a real implementation, you would:
        # 1. Verify current password against database
        # 2. Hash the new password
        # 3. Update the database
        
        # For now, simulate successful password change
        logger.info(f"Password change requested for user {user_id}")
        
        return JSONResponse(content={
            "success": True, 
            "message": "Password changed successfully"
        })
        
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return JSONResponse(content={
            "success": False,
            "message": "An error occurred while changing password"
        }, status_code=500)

# Include the profile router
app.include_router(profile_router)


# Product analysis routes are handled by the product_analysis_routes module

@app.get("/")
async def landing(request: Request):
    """Landing page using Jinja2 template"""
    try:
        return templates.TemplateResponse("pages/landing.html", {"request": request})
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/dashboard")
@app.head("/dashboard")
async def dashboard(request: Request):
    """Dashboard page using Jinja2 template"""
    try:
        return templates.TemplateResponse("pages/dashboard.html", {"request": request})
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/login")
async def login_page(request: Request):
    """Login page using Jinja2 template"""
    return templates.TemplateResponse("pages/login.html", {"request": request})

@app.get("/suppliers")
async def suppliers_page(request: Request):
    """Suppliers page"""
    try:
        return templates.TemplateResponse("pages/suppliers.html", {"request": request})
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/buyers")
async def buyers_page(request: Request):
    """Buyers page"""
    try:
        return templates.TemplateResponse("pages/buyers.html", {"request": request})
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/buyers/list")
async def list_buyers():
    """Get list of buyers"""
    try:
        # For now, return empty list - will be connected to database later
        return {
            "success": True,
            "buyers": []
        }
    except Exception as e:
        logger.error(f"Error listing buyers: {e}")
        return {
            "success": False,
            "message": "Error listing buyers"
        }

@app.post("/buyers/create")
async def create_buyer(request: Request):
    """Create a new buyer"""
    try:
        form_data = await request.form()
        
        buyer_data = {
            "name": form_data.get("name"),
            "company_name": form_data.get("company_name"),
            "email": form_data.get("email"),
            "phone": form_data.get("phone"),
            "country": form_data.get("country"),
            "city": form_data.get("city"),
            "address": form_data.get("address"),
            "industry": form_data.get("industry"),
            "company_size": form_data.get("company_size"),
            "payment_terms": form_data.get("payment_terms")
        }
        
        # For now, just log the data - will be saved to database later
        logger.info(f"Creating buyer: {buyer_data}")
        
        return {
            "success": True,
            "message": "Buyer created successfully",
            "buyer_id": 1  # Placeholder ID
        }
    except Exception as e:
        logger.error(f"Error creating buyer: {e}")
        return {
            "success": False,
            "message": "Error creating buyer"
        }

@app.get("/suppliers/list")
async def list_suppliers():
    """Get list of suppliers"""
    try:
        # For now, return empty list - will be connected to database later
        return {
            "success": True,
            "suppliers": []
        }
    except Exception as e:
        logger.error(f"Error listing suppliers: {e}")
        return {
            "success": False,
            "message": "Error listing suppliers"
        }

@app.post("/suppliers/create")
async def create_supplier(request: Request):
    """Create a new supplier"""
    try:
        form_data = await request.form()
        
        supplier_data = {
            "name": form_data.get("name"),
            "company_name": form_data.get("company_name"),
            "email": form_data.get("email"),
            "phone": form_data.get("phone"),
            "country": form_data.get("country"),
            "city": form_data.get("city"),
            "address": form_data.get("address"),
            "industry": form_data.get("industry"),
            "company_size": form_data.get("company_size"),
            "certifications": form_data.get("certifications"),
            "payment_terms": form_data.get("payment_terms"),
            "minimum_order": form_data.get("minimum_order")
        }
        
        # For now, just log the data - will be saved to database later
        logger.info(f"Creating supplier: {supplier_data}")
        
        return {
            "success": True,
            "message": "Supplier created successfully",
            "supplier_id": 1  # Placeholder ID
        }
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        return {
            "success": False,
            "message": "Error creating supplier"
        }

@app.get("/projects")
async def projects_page(request: Request):
    """Projects page to view saved analysis projects"""
    try:
        # Get list of saved projects
        projects_dir = os.path.join(os.getcwd(), "projects")
        projects = []
        
        if os.path.exists(projects_dir):
            for filename in os.listdir(projects_dir):
                if filename.endswith('.json'):
                    project_path = os.path.join(projects_dir, filename)
                    try:
                        with open(project_path, 'r', encoding='utf-8') as f:
                            project_data = json.loads(f.read())
                            projects.append({
                                'name': project_data.get('name', 'Unknown Project'),
                                'description': project_data.get('description', ''),
                                'buyer_id': project_data.get('buyer_id'),
                                'priority': project_data.get('priority', 'medium'),
                                'created_at': project_data.get('created_at', ''),
                                'filename': filename
                            })
                    except Exception as e:
                        logger.error(f"Error reading project file {filename}: {e}")
        
        # Sort projects by creation date (newest first)
        projects.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return templates.TemplateResponse("pages/projects.html", {
            "request": request,
            "projects": projects
        })
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/projects/{filename}")
async def get_project(filename: str):
    """Get individual project details"""
    try:
        projects_dir = os.path.join(os.getcwd(), "projects")
        project_path = os.path.join(projects_dir, filename)
        
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        with open(project_path, 'r', encoding='utf-8') as f:
            project_data = json.loads(f.read())
        
        return {
            "success": True,
            "project": project_data
        }
    except Exception as e:
        logger.error(f"Error reading project {filename}: {e}")
        return {
            "success": False,
            "message": "Error reading project"
        }

@app.delete("/projects/{filename}")
async def delete_project(filename: str):
    """Delete a project"""
    try:
        projects_dir = os.path.join(os.getcwd(), "projects")
        project_path = os.path.join(projects_dir, filename)
        
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        os.remove(project_path)
        
        return {
            "success": True,
            "message": "Project deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting project {filename}: {e}")
        return {
            "success": False,
            "message": "Error deleting project"
        }

@app.put("/projects/{filename}")
async def update_project(filename: str, request: Request):
    """Update a project"""
    try:
        projects_dir = os.path.join(os.getcwd(), "projects")
        project_path = os.path.join(projects_dir, filename)
        
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get the updated project data from request body
        updated_data = await request.json()
        
        # Read existing project to preserve any fields not being updated
        with open(project_path, 'r', encoding='utf-8') as f:
            existing_data = json.loads(f.read())
        
        # Merge the updated data with existing data
        merged_data = {**existing_data, **updated_data}
        
        # Write the updated project back to file
        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": "Project updated successfully",
            "project": merged_data
        }
    except Exception as e:
        logger.error(f"Error updating project {filename}: {e}")
        return {
            "success": False,
            "message": f"Error updating project: {str(e)}"
        }

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    favicon_path = BASE_DIR / "static/brand/logos/Favicon.png"
    if favicon_path.exists():
        return FileResponse(path=str(favicon_path))
    else:
        raise HTTPException(status_code=404, detail="Favicon not found")

@app.get("/favicon.png")
async def favicon_png():
    """Serve favicon PNG"""
    favicon_path = BASE_DIR / "static/brand/logos/Favicon.png"
    if favicon_path.exists():
        return FileResponse(path=str(favicon_path))
    else:
        raise HTTPException(status_code=404, detail="Favicon not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("foodxchange.main:app", host="0.0.0.0", port=8003, reload=True) 