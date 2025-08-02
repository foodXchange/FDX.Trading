"""
FoodXchange - AI-Powered B2B Food Sourcing Platform
Main FastAPI application with integrated product analysis system
"""

import os
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
from pathlib import Path
import logging
import json
from typing import Optional
from datetime import datetime

import bcrypt
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from foodxchange.middleware.static_headers import StaticFilesWithHeaders

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Create FastAPI app
app = FastAPI(
    title="FoodXchange",
    description="AI-Powered B2B Food Sourcing Platform",
    version="1.0.0"
)

# Setup global error handlers
from foodxchange.core.error_handlers import setup_error_handlers, request_id_middleware
setup_error_handlers(app)

# Add request ID middleware
app.middleware("http")(request_id_middleware)

# Add CORS middleware with secure configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8003",
        "http://localhost:9000",
        "https://foodxchange.com",
        "https://app.foodxchange.com",
        "https://fdx.trading"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token"
    ],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=86400,  # Cache preflight requests for 24 hours
)

# Session middleware not needed - we use JWT tokens for authentication

# Add security headers middleware
try:
    from foodxchange.middleware.security_headers import security_headers_middleware
    app.middleware("http")(security_headers_middleware)
    logger.info("✅ Security headers middleware added")
except ImportError as e:
    logger.warning(f"Security headers middleware not available: {e}")

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
    
    # Get user ID from JWT token if available (we don't use sessions)
    user_id = None
    try:
        # Extract user from authorization header if present
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # For now, just note that auth is present
            # Full JWT parsing would require importing auth dependencies
            user_id = "authenticated"
    except Exception:
        user_id = None
    
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

# Mount static files with proper headers
app.mount("/static", StaticFilesWithHeaders(directory=str(BASE_DIR / "static")), name="static")

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
        "profile_settings": "/profile/settings",
        "demo": "/demo",
        "demo_animations": "/demo/animations"
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


# Health check endpoint - added directly to app
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# SECURE LOGIN IMPLEMENTATION
from foodxchange.core.security import get_jwt_manager, get_password_manager, AuthRateLimiter
from foodxchange.core.exceptions import AuthenticationError

# Initialize rate limiter for production
auth_rate_limiter = AuthRateLimiter(
    max_attempts=5,     # 5 attempts allowed
    window_minutes=15   # 15-minute window
)

@app.post("/auth/login")
async def secure_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Secure login with JWT tokens and rate limiting"""
    
    # Rate limiting check
    client_ip = request.client.host if request.client else "unknown"
    if auth_rate_limiter.is_rate_limited(f"{email}:{client_ip}"):
        return RedirectResponse(url="/login?error=rate_limited", status_code=303)
    
    # Validate input
    if not email or not password:
        auth_rate_limiter.record_attempt(f"{email}:{client_ip}")
        return RedirectResponse(url="/login?error=missing_credentials", status_code=303)
    
    # Development mode - mock authentication
    from foodxchange.config.dev_auth import get_development_users, is_development_mode
    
    logger.info(f"Current environment: {os.getenv('ENVIRONMENT', 'production')}")
    
    if is_development_mode():
        logger.info(f"Development mode login attempt for: {email}")
        # Allow test users in development
        test_users = get_development_users()
        
        logger.info(f"Checking credentials - Email exists: {email in test_users}")
        if email in test_users:
            password_match = password == test_users[email]['password']
            logger.info(f"Password validation attempt for user: {email}, success: {password_match}")
        
        if email in test_users and password == test_users[email]["password"]:
            user_data = {
                "user_id": test_users[email]["user_id"],
                "email": email,
                "role": test_users[email]["role"],
                "is_admin": test_users[email]["role"] == "admin"
            }
            
            # Create JWT token
            jwt_manager = get_jwt_manager()
            access_token = jwt_manager.create_access_token(user_data)
            
            # Clear rate limiting attempts
            auth_rate_limiter.clear_attempts(f"{email}:{client_ip}")
            
            # Create response with redirect
            response = RedirectResponse(url="/dashboard", status_code=303)
            
            # Cookie security settings
            is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=is_production,
                samesite="strict" if is_production else "lax",
                max_age=1800
            )
            
            logger.info(f"Development login successful for: {email}")
            return response
    
    try:
        # Connect to PostgreSQL database
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        # Get database URL from environment or use default
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/foodxchange')
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        
        # Check for user in database
        result = db.execute(text("SELECT id, first_name, last_name, email, password_hash, role FROM users WHERE email = :email"), {"email": email})
        user = result.fetchone()
        
        authenticated = False
        user_data = None
        
        if user:
            # Verify password against database
            user_id, first_name, last_name, db_email, hashed_password, role = user
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                authenticated = True
                user_data = {
                    "user_id": user_id,
                    "email": db_email,
                    "role": role,
                    "is_admin": role == "admin"
                }
        
        db.close()
        
        if authenticated and user_data:
            # Create JWT token
            jwt_manager = get_jwt_manager()
            access_token = jwt_manager.create_access_token(user_data)
            
            # Clear rate limiting attempts on successful login
            auth_rate_limiter.clear_attempts(f"{email}:{client_ip}")
            
            # Create response with redirect
            response = RedirectResponse(url="/dashboard", status_code=303)
            
            # Set secure cookie with JWT token
            secure_cookie = os.getenv("ENVIRONMENT", "production").lower() == "production"
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=secure_cookie,
                samesite="strict",
                max_age=1800  # 30 minutes
            )
            
            logger.info(f"Successful login for user: {email}")
            return response
        else:
            auth_rate_limiter.record_attempt(f"{email}:{client_ip}")
            logger.warning(f"Failed login attempt for email: {email} from IP: {client_ip}")
            return RedirectResponse(url="/login?error=invalid_credentials", status_code=303)
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        auth_rate_limiter.record_attempt(f"{email}:{client_ip}")
        return RedirectResponse(url="/login?error=server_error", status_code=303)

# REMOVED INSECURE ADMIN ENDPOINT FOR SECURITY

@app.post("/auth/logout")
@app.get("/logout")
async def logout(request: Request):
    """Logout endpoint that clears the JWT token"""
    response = RedirectResponse(url="/login?success=logged_out", status_code=303)
    response.delete_cookie("access_token")
    logger.info("User logged out successfully")
    return response

# Import and include route modules
try:
    # Make templates available globally before importing routes
    import sys
    sys.path.append(str(BASE_DIR))
    sys.path.append(str(BASE_DIR.parent))  # Add parent directory to path
    
    # Import routes individually to handle errors gracefully
    try:
        from foodxchange.routes import product_analysis_routes
        app.include_router(product_analysis_routes.router)
        logger.info("✅ Product analysis routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Product analysis routes not loaded: {e}")
    
    try:
        from foodxchange.routes import data_import_routes
        app.include_router(data_import_routes.router)
        logger.info("✅ Data import routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Data import routes not loaded: {e}")
    
    try:
        from foodxchange.routes import azure_testing_routes_fastapi
        app.include_router(azure_testing_routes_fastapi.azure_testing_router)
        logger.info("✅ Azure testing routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Azure testing routes not loaded: {e}")
    
    try:
        from foodxchange.routes import ai_import_routes_fastapi
        app.include_router(ai_import_routes_fastapi.ai_import_router)
        logger.info("✅ AI import routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ AI import routes not loaded: {e}")
    
    # Skip search_routes for now due to import issues
    try:
        from foodxchange.routes import search_routes
        app.include_router(search_routes.router)
        logger.info("✅ Search routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️ Search routes not loaded: {e}")
    
    logger.info("✅ Core route modules loaded successfully")
    
except Exception as e:
    logger.warning(f"⚠️ Route loading error: {e}")

# Try to load additional routes that might have dependencies
try:
    from foodxchange.routes import health_routes
    app.include_router(health_routes.router)
    logger.info("✅ Health routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Health routes not loaded: {e}")

try:
    from foodxchange.routes import error_routes
    app.include_router(error_routes.router)
    logger.info("✅ Error routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Error routes not loaded: {e}")

try:
    from foodxchange.routes import help_routes
    app.include_router(help_routes.router)
    logger.info("✅ Help routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Help routes not loaded: {e}")

try:
    from foodxchange.routes import support_routes
    app.include_router(support_routes.router)
    logger.info("✅ Support routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Support routes not loaded: {e}")

try:
    from foodxchange.routes import error_tracking_routes
    app.include_router(error_tracking_routes.router, prefix="/errors")
    logger.info("✅ Error tracking routes loaded with prefix /errors")
except ImportError as e:
    logger.warning(f"⚠️ Error tracking routes not loaded: {e}")

try:
    from foodxchange.routes import project_routes
    app.include_router(project_routes.router)
    logger.info("✅ Enhanced project routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced project routes not loaded: {e}")

# Add footer pages routes
try:
    from foodxchange.routes import footer_routes
    app.include_router(footer_routes.router)
    logger.info("✅ Footer pages routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Footer pages routes not loaded: {e}")

# Load demo routes
try:
    from foodxchange.routes import demo_routes
    app.include_router(demo_routes.router)
    logger.info("✅ Demo routes loaded")
except ImportError as e:
    logger.warning(f"⚠️ Demo routes not loaded: {e}")

logger.info("✅ Optional route modules loaded successfully")

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
    "email": "admin@fdx.trading",
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
    from foodxchange.core.auth import get_current_user
    
    # Get current user if logged in (for navbar)
    user = get_current_user(request)
    
    try:
        context = {"request": request}
        if user:
            context["current_user"] = {
                "id": user.user_id,
                "email": user.email,
                "role": user.role,
                "is_admin": user.is_admin
            }
        return templates.TemplateResponse("pages/index_clean.html", context)
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/dashboard")
@app.post("/dashboard")  # Handle POST redirects from login
@app.head("/dashboard")
async def dashboard(request: Request):
    """Dashboard page - requires authentication"""
    from foodxchange.core.auth import get_current_user
    
    # Check authentication
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    try:
        return templates.TemplateResponse("pages/dashboard_simple.html", {
            "request": request,
            "current_user": {
                "id": user.user_id,
                "email": user.email,
                "role": user.role,
                "is_admin": user.is_admin
            }
        })
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/login")
async def login_page(request: Request):
    # Check for performance mode in query params or environment
    use_optimized = request.query_params.get("optimized", os.getenv("USE_OPTIMIZED_LOGIN", "false")).lower() == "true"
    
    template_name = "pages/login_optimized.html" if use_optimized else "pages/login_simple.html"
    return templates.TemplateResponse(template_name, {"request": request})


@app.get("/debug-routes")
async def debug_routes():
    """Debug endpoint to show all registered routes"""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, 'methods') else [],
                "name": route.name if hasattr(route, 'name') else None
            })
    return {"routes": sorted(routes, key=lambda x: x['path'])}

@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("pages/signup.html", {"request": request})

@app.post("/auth/signup")
async def signup(
    request: Request,
    firstName: str = Form(...),
    lastName: str = Form(...),
    email: str = Form(...),
    company: str = Form(...),
    password: str = Form(...),
    confirmPassword: str = Form(...),
    terms: bool = Form(False)
):
    """Handle user registration"""
    try:
        # Validate terms acceptance
        if not terms:
            return RedirectResponse(url="/signup?error=terms_required", status_code=303)
        
        # Validate passwords match
        if password != confirmPassword:
            return RedirectResponse(url="/signup?error=password_mismatch", status_code=303)
        
        # Validate password strength
        if len(password) < 8:
            return RedirectResponse(url="/signup?error=weak_password", status_code=303)
        
        # Use consistent PostgreSQL database connection
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/foodxchange')
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Check if user already exists
            result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
            if result.fetchone():
                db.close()
                return RedirectResponse(url="/signup?error=email_exists", status_code=303)
            
            # Hash password
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Create user
            db.execute(text("""
                INSERT INTO users (first_name, last_name, email, password_hash, company, role, created_at)
                VALUES (:first_name, :last_name, :email, :password_hash, :company, 'user', NOW())
            """), {
                "first_name": firstName,
                "last_name": lastName, 
                "email": email,
                "password_hash": password_hash,
                "company": company
            })
            
            # Get the new user ID
            result = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
            user_row = result.fetchone()
            user_id = user_row[0] if user_row else None
            
            db.commit()
        finally:
            db.close()
        
        # Create JWT token instead of session
        from foodxchange.core.security import get_jwt_manager
        jwt_manager = get_jwt_manager()
        user_data = {
            "user_id": user_id,
            "email": email,
            "role": "user",
            "is_admin": False
        }
        access_token = jwt_manager.create_access_token(user_data)
        
        # Redirect to dashboard
        response = RedirectResponse(url="/dashboard", status_code=303)
        
        # Cookie security settings (consistent with login)
        is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=is_production,
            samesite="strict" if is_production else "lax",
            max_age=1800  # 30 minutes (consistent with login)
        )
        return response
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}", exc_info=True)
        return RedirectResponse(url="/signup?error=registration_failed", status_code=303)

@app.get("/support")
async def support_page(request: Request):
    """Support page - requires authentication"""
    from foodxchange.core.auth import get_current_user
    
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    # Check authentication
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    return templates.TemplateResponse("pages/support_admin.html", {
        "request": request,
        "current_user": {
            "id": user.user_id,
            "email": user.email,
            "role": user.role,
            "is_admin": user.is_admin
        }
    })

@app.get("/support/admin")
async def support_admin_page(request: Request):
    """Support admin page - requires authentication"""
    from foodxchange.core.auth import get_current_user
    
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    # Check authentication
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    return templates.TemplateResponse("pages/support_admin.html", {
        "request": request,
        "current_user": {
            "id": user.user_id,
            "email": user.email,
            "role": user.role,
            "is_admin": user.is_admin
        }
    })

@app.get("/suppliers")
async def suppliers_page(request: Request):
    """Suppliers page - requires authentication"""
    from foodxchange.core.auth import get_current_user
    
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    # Check authentication
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    try:
        return templates.TemplateResponse("pages/suppliers_simple.html", {
            "request": request,
            "current_user": {
                "id": user.user_id,
                "email": user.email,
                "role": user.role,
                "is_admin": user.is_admin
            }
        })
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/buyers")
async def buyers_page(request: Request):
    """Buyers page - requires authentication"""
    from foodxchange.core.auth import get_current_user
    
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    # Check authentication - Admin/Operator only
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    if user.role not in ["admin", "operator"] and not user.is_admin:
        return RedirectResponse(url="/dashboard?error=unauthorized", status_code=303)
    
    try:
        return templates.TemplateResponse("pages/buyers.html", {
            "request": request,
            "current_user": {
                "id": user.user_id,
                "email": user.email,
                "role": user.role,
                "is_admin": user.is_admin
            }
        })
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

@app.get("/suppliers/list/debug")
async def list_suppliers_debug():
    """Debug version of list suppliers endpoint"""
    import sqlite3
    import json
    import os
    
    debug_info = {
        "cwd": os.getcwd(),
        "db_path": os.path.abspath('foodxchange.db'),
        "db_exists": os.path.exists('foodxchange.db'),
        "db_size": os.path.getsize('foodxchange.db') if os.path.exists('foodxchange.db') else 0
    }
    
    try:
        conn = sqlite3.connect('foodxchange.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM suppliers WHERE is_active = 1")
        active_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT id, name, is_active FROM suppliers LIMIT 3")
        sample = cursor.fetchall()
        
        conn.close()
        
        debug_info.update({
            "total_suppliers": total_count,
            "active_suppliers": active_count,
            "sample": sample
        })
        
    except Exception as e:
        debug_info["error"] = str(e)
    
    return debug_info

@app.get("/suppliers/list")
async def list_suppliers():
    """Get list of suppliers from database"""
    try:
        # Use SQLite for local development
        import sqlite3
        import json
        import os
        
        # Log current directory and database path
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        db_path = 'foodxchange.db'
        print(f"DEBUG: Looking for database at: {os.path.abspath(db_path)}")
        print(f"DEBUG: Database exists: {os.path.exists(db_path)}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query active suppliers
        cursor.execute("""
            SELECT id, name, company_name, email, phone, website, 
                   city, country, categories, specialties, certifications,
                   rating, response_rate, is_verified
            FROM suppliers 
            WHERE is_active = 1
            ORDER BY rating DESC
        """)
        
        rows = cursor.fetchall()
        print(f"DEBUG: Query executed, found {len(rows)} suppliers")
        
        suppliers = []
        for row in rows:
            supplier = {
                "id": row[0],
                "name": row[1],
                "company_name": row[2],
                "email": row[3],
                "phone": row[4],
                "website": row[5],
                "city": row[6],
                "country": row[7],
                "categories": json.loads(row[8]) if row[8] else [],
                "specialties": json.loads(row[9]) if row[9] else [],
                "certifications": json.loads(row[10]) if row[10] else [],
                "rating": row[11],
                "response_rate": row[12],
                "is_verified": row[13]
            }
            suppliers.append(supplier)
        
        conn.close()
        
        return {
            "success": True,
            "suppliers": suppliers
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
        import sqlite3
        import json
        from datetime import datetime
        
        form_data = await request.form()
        
        # Prepare supplier data
        supplier_data = {
            "name": form_data.get("name"),
            "company_name": form_data.get("company_name"),
            "email": form_data.get("email"),
            "phone": form_data.get("phone"),
            "country": form_data.get("country"),
            "city": form_data.get("city"),
            "address": form_data.get("address"),
            "status": "active",
            "is_active": True,
            "is_verified": False,
            "rating": 0.0,
            "response_rate": 0.0,
            "average_response_time": 0.0
        }
        
        # Handle JSON fields
        certifications = form_data.get("certifications", "[]")
        if isinstance(certifications, str):
            try:
                certifications = json.loads(certifications)
            except:
                certifications = []
        
        # Save to database
        conn = sqlite3.connect('foodxchange.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO suppliers (
                name, company_name, email, phone, website, address, city, country,
                categories, specialties, certifications, status, rating, response_rate,
                average_response_time, is_verified, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            supplier_data['name'],
            supplier_data['company_name'],
            supplier_data['email'],
            supplier_data['phone'],
            form_data.get('website', ''),
            supplier_data['address'],
            supplier_data['city'],
            supplier_data['country'],
            json.dumps([form_data.get('industry', 'Other')]) if form_data.get('industry') else '[]',
            '[]',  # specialties
            json.dumps(certifications),
            supplier_data['status'],
            supplier_data['rating'],
            supplier_data['response_rate'],
            supplier_data['average_response_time'],
            supplier_data['is_verified'],
            supplier_data['is_active'],
            datetime.now(),
            datetime.now()
        ))
        
        supplier_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created supplier with ID: {supplier_id}")
        
        return {
            "success": True,
            "message": "Supplier created successfully",
            "supplier_id": supplier_id
        }
    except Exception as e:
        logger.error(f"Error creating supplier: {e}")
        return {
            "success": False,
            "message": "Error creating supplier"
        }

@app.get("/projects")
async def projects_page(request: Request):
    """Projects page - requires authentication"""
    from foodxchange.core.auth import get_current_user
    
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    # Check authentication
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
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
        
        return templates.TemplateResponse("pages/projects_enhanced.html", {
            "request": request,
            "projects": projects,
            "current_user": {
                "id": user.user_id,
                "email": user.email,
                "role": user.role,
                "is_admin": user.is_admin
            }
        })
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/projects/{filename}")
async def get_project(filename: str, request: Request):
    """Get individual project details"""
    from foodxchange.core.auth import get_current_user
    
    # Check authentication
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
    
    try:
        projects_dir = os.path.join(os.getcwd(), "projects")
        project_path = os.path.join(projects_dir, filename)
        
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        with open(project_path, 'r', encoding='utf-8') as f:
            project_data = json.loads(f.read())
        
        # Render project detail template
        return templates.TemplateResponse("pages/project_detail.html", {
            "request": request,
            "project": project_data,
            "filename": filename,
            "current_user": {
                "id": user.user_id,
                "email": user.email,
                "role": user.role,
                "is_admin": user.is_admin
            }
        })
    except Exception as e:
        logger.error(f"Error reading project {filename}: {e}")
        return HTMLResponse(content=f"Error reading project: {str(e)}", status_code=500)

# @app.delete("/projects/{filename}")
# async def delete_project(filename: str):
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

# @app.put("/projects/{filename}")
# async def update_project(filename: str, request: Request):
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
    uvicorn.run("foodxchange.main:app", host="0.0.0.0", port=9000, reload=True) 
