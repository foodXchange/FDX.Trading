import warnings
import time
import os
import logging
import platform
from datetime import datetime

# Load all environment variables from .env and .env.blob files
from app.load_all_env import load_all_env_files

# Suppress cryptography warnings about 32-bit Python
warnings.filterwarnings("ignore", message=".*cryptography.*32-bit.*64-bit.*")

# Enhanced Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration

# Initialize Sentry SDK with the new DSN
sentry_sdk.init(
    dsn="https://fdf092923fb6dd5351274f42e8a4dee9@o4509734929104896.ingest.de.sentry.io/4509734959775824",
    # Add data like request headers and IP for users
    send_default_pii=True,
    # Set sample rate for performance monitoring
    traces_sample_rate=1.0,  # Capture 100% of transactions for performance monitoring
    # Set the environment
    environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
    # Add integrations
    integrations=[
        FastApiIntegration(
            transaction_style="endpoint"  # Use endpoint name as transaction name
        ),
        SqlalchemyIntegration(),
        HttpxIntegration(),
    ],
    # Set release tracking
    release=os.getenv("SENTRY_RELEASE", "foodxchange@1.0.0"),
    # Enable profiling
    profiles_sample_rate=1.0,  # Profile 100% of sampled transactions
    # Attach stack trace to messages
    attach_stacktrace=True,
    # Sample rate for error events
    sample_rate=1.0,
    # Max breadcrumbs
    max_breadcrumbs=50,
)

print("Sentry SDK initialized with new DSN")

# Try to import middleware if available
try:
    from sentry_middleware import SentryMiddleware, SentryUserMiddleware, db_monitor
    print("Sentry middleware imported successfully")
except ImportError:
    print("Warning: Sentry middleware not found")

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
import psutil

from app.database import get_db
from app.auth import SessionAuth, get_current_user_context as get_user_context

# Azure Monitor integration
try:
    from app.services.azure_monitor_service import azure_monitor
    print("Azure Monitor service imported")
except ImportError as e:
    print(f"Warning: Azure Monitor service not available: {e}")
    azure_monitor = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FoodXchange API")

# Add enhanced Sentry middleware
try:
    app.add_middleware(SentryMiddleware)
    app.add_middleware(SentryUserMiddleware)
except:
    pass

# Add Azure Monitor middleware if available
if azure_monitor and azure_monitor.enabled:
    try:
        azure_middleware = azure_monitor.get_fastapi_middleware()
        if azure_middleware:
            app.add_middleware(azure_middleware)
            print("Azure Monitor middleware added")
    except Exception as e:
        print(f"Warning: Failed to add Azure Monitor middleware: {e}")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Global start time for uptime tracking
start_time = time.time()

def get_current_user_context(request: Request, db: Session):
    return get_user_context(request, db)

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("landing.html", {"request": request, "current_user": get_current_user_context(request, db)})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    error = request.query_params.get("error")
    return templates.TemplateResponse("login.html", {"request": request, "error": error, "current_user": None})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    error = request.query_params.get("error")
    return templates.TemplateResponse("register.html", {"request": request, "error": error, "current_user": None})

# Health Endpoints
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/simple")
async def health_simple():
    """Simple health check for basic uptime monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/health/detailed")
async def health_detailed():
    """Detailed health check with system information"""
    try:
        # Test database connection
        from app.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "application": "healthy",
        "version": "1.0.0"
    }

@app.get("/health/advanced")
async def health_advanced():
    """Advanced health check with comprehensive system status"""
    try:
        # Test database connection
        from app.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db.execute("SELECT version()")
        db_version = db.fetchone()[0]
        db.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        table_count = db.fetchone()[0]
        db_status = {
            "status": "healthy",
            "version": db_version,
            "tables": table_count,
            "connection": "ok"
        }
    except Exception as e:
        db_status = {
            "status": "unhealthy",
            "error": str(e),
            "connection": "failed"
        }

    system_info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage('/').percent
    }

    app_status = "healthy"
    overall_status = "healthy" if db_status["status"] == "healthy" and app_status == "healthy" else "unhealthy"

    response = {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "service": "FoodXchange",
        "version": "1.0.0",
        "environment": os.getenv('FLASK_ENV', 'production'),
        "services": {
            "database": db_status,
            "application": app_status
        },
        "system": system_info,
        "monitoring": {
            "sentry": "configured" if os.getenv('SENTRY_DSN') else "not_configured",
            "uptimerobot": "configured" if os.path.exists('uptimerobot_config.json') else "not_configured",
            "azure_monitor": azure_monitor.get_status() if azure_monitor else {"enabled": False, "error": "not_available"}
        }
    }
    return response

@app.get("/health/enhanced")
async def enhanced_health():
    """Enhanced health check with detailed monitoring"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application metrics
        process = psutil.Process()
        process_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Database health check
        try:
            from app.database import get_db
            db = next(get_db())
            db.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
            sentry_sdk.capture_exception(e)
        
        # Add metrics to Sentry
        sentry_sdk.set_tag("health_check_cpu_percent", cpu_percent)
        sentry_sdk.set_tag("health_check_memory_percent", memory.percent)
        sentry_sdk.set_tag("health_check_disk_percent", disk.percent)
        sentry_sdk.set_tag("health_check_process_memory_mb", round(process_memory, 2))
        
        # Set performance context
        sentry_sdk.set_context("system_health", {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "process_memory_mb": round(process_memory, 2),
            "database_status": db_status,
        })
        
        # Determine overall health
        overall_status = "healthy"
        if cpu_percent > 80 or memory.percent > 80 or disk.percent > 90:
            overall_status = "warning"
        if db_status != "healthy":
            overall_status = "unhealthy"
        
        response = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "process_memory_mb": round(process_memory, 2),
            },
            "services": {
                "database": db_status,
                "application": "healthy",
            },
            "version": "1.0.0",
            "environment": os.getenv("SENTRY_ENVIRONMENT", "production")
        }
        
        # Report warnings to Sentry
        if overall_status == "warning":
            sentry_sdk.capture_message(
                "System health warning detected",
                level="warning",
                tags={
                    "health_check": True,
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk.percent,
                }
            )
        
        return response
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/readiness")
async def health_readiness():
    """Kubernetes readiness probe endpoint"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health/liveness")
async def health_liveness():
    """Kubernetes liveness probe endpoint"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus-style metrics endpoint"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        process = psutil.Process()
        process_memory = process.memory_info().rss / 1024 / 1024
        
        metrics_text = f"""# HELP foodxchange_cpu_percent CPU usage percentage
# TYPE foodxchange_cpu_percent gauge
foodxchange_cpu_percent {cpu_percent}

# HELP foodxchange_memory_percent Memory usage percentage
# TYPE foodxchange_memory_percent gauge
foodxchange_memory_percent {memory.percent}

# HELP foodxchange_disk_percent Disk usage percentage
# TYPE foodxchange_disk_percent gauge
foodxchange_disk_percent {disk.percent}

# HELP foodxchange_process_memory_mb Process memory usage in MB
# TYPE foodxchange_process_memory_mb gauge
foodxchange_process_memory_mb {process_memory}

# HELP foodxchange_uptime_seconds Application uptime in seconds
# TYPE foodxchange_uptime_seconds counter
foodxchange_uptime_seconds {time.time() - start_time}
"""
        
        return Response(content=metrics_text, media_type="text/plain")
        
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return {"error": str(e)}

@app.get("/test-sentry")
async def test_sentry():
    """Test endpoint to trigger a Sentry error"""
    try:
        # Trigger a test error
        raise ValueError("This is a test error from FoodXchange - Sentry integration test")
    except Exception as e:
        # Capture the error in Sentry
        sentry_sdk.capture_exception(e)
        return {
            "message": "Test error triggered and sent to Sentry",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/sentry-debug")
async def trigger_error():
    """Debug endpoint to verify Sentry integration by triggering a division by zero error"""
    division_by_zero = 1 / 0

@app.get("/monitoring/azure")
async def azure_monitor_status():
    """Get Azure Monitor status and configuration"""
    try:
        if not azure_monitor:
            return {
                "status": "not_available",
                "message": "Azure Monitor service not available",
                "timestamp": datetime.now().isoformat()
            }
        
        status = azure_monitor.get_status()
        
        # Test Azure Monitor functionality
        if azure_monitor.enabled:
            try:
                azure_monitor.log_event("health_check", {
                    "endpoint": "/monitoring/azure",
                    "timestamp": datetime.now().isoformat()
                })
                status["test_event_sent"] = True
            except Exception as e:
                status["test_event_sent"] = False
                status["test_event_error"] = str(e)
        
        return {
            "status": "success",
            "azure_monitor": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to get Azure Monitor status: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/monitoring/test")
async def test_monitoring():
    """Test all monitoring systems"""
    results = {}
    
    # Test Sentry
    try:
        sentry_sdk.capture_message("Monitoring test from FoodXchange", level="info")
        results["sentry"] = {"status": "success", "message": "Test event sent"}
    except Exception as e:
        results["sentry"] = {"status": "error", "message": str(e)}
    
    # Test Azure Monitor
    if azure_monitor and azure_monitor.enabled:
        try:
            azure_monitor.log_event("monitoring_test", {
                "test_type": "comprehensive",
                "timestamp": datetime.now().isoformat()
            })
            results["azure_monitor"] = {"status": "success", "message": "Test event sent"}
        except Exception as e:
            results["azure_monitor"] = {"status": "error", "message": str(e)}
    else:
        results["azure_monitor"] = {"status": "not_available", "message": "Azure Monitor not configured"}
    
    return {
        "status": "completed",
        "results": results,
        "timestamp": datetime.now().isoformat()
    }

# Application Routes
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    stats = {
        "suppliers": 0,
        "rfqs": 0,
        "quotes": 0,
        "emails": 0
    }
    return templates.TemplateResponse("simple_dashboard.html", {"request": request, "stats": stats, "current_user": user})

@app.get("/suppliers", response_class=HTMLResponse, name="suppliers_list")
async def suppliers_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    suppliers = [
        {"id": 1, "name": "Mediterranean Delights", "location": "Greece", "products": ["Olive Oil", "Feta Cheese"], "status": "active"},
        {"id": 2, "name": "Italian Fine Foods", "location": "Italy", "products": ["Pasta", "Tomatoes"], "status": "active"},
        {"id": 3, "name": "Spanish Imports Co", "location": "Spain", "products": ["Jamón", "Manchego"], "status": "pending"}
    ]
    return templates.TemplateResponse("suppliers.html", {"request": request, "suppliers": suppliers, "current_user": user})

@app.get("/suppliers/add", response_class=HTMLResponse, name="add_supplier")
async def add_supplier(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("base.html", {"request": request, "title": "Add Supplier", "current_user": user})

@app.get("/suppliers/{supplier_id}", response_class=HTMLResponse, name="view_supplier")
async def view_supplier(request: Request, supplier_id: int, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("base.html", {"request": request, "title": f"Supplier {supplier_id}", "current_user": user})

@app.get("/suppliers/{supplier_id}/edit", response_class=HTMLResponse, name="edit_supplier")
async def edit_supplier(request: Request, supplier_id: int, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("base.html", {"request": request, "title": f"Edit Supplier {supplier_id}", "current_user": user})

@app.get("/rfq/new", response_class=HTMLResponse, name="new_rfq")
async def new_rfq(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("rfq_new.html", {"request": request, "current_user": user})

@app.post("/rfq/new", response_class=HTMLResponse)
async def create_rfq(request: Request, product: str = Form(...), quantity: int = Form(...), deadline: str = Form(...), notes: str = Form(None), db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Placeholder: Save RFQ to database
    # Redirect to dashboard or show confirmation
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": {"suppliers": 0, "rfqs": 1, "quotes": 0, "emails": 0}, "message": "RFQ created!", "current_user": user})

@app.get("/orders", response_class=HTMLResponse, name="orders_list")
async def orders_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("orders.html", {"request": request, "current_user": user})

@app.get("/products", response_class=HTMLResponse, name="products_list")
async def products_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("products.html", {"request": request, "current_user": user})

@app.get("/analytics", response_class=HTMLResponse, name="analytics")
async def analytics(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    kpis = {
        "total_spend": 100000,
        "cost_savings": 15000,
        "suppliers_engaged": 12,
        "rfqs_sent": 34
    }
    return templates.TemplateResponse("analytics.html", {"request": request, "kpis": kpis, "current_user": user})

@app.get("/quotes/comparison", response_class=HTMLResponse, name="quote_comparison")
async def quote_comparison(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    from app.models.rfq import RFQ
    from app.models.quote import Quote
    
    # Get RFQ ID from query params
    rfq_id = request.query_params.get("rfq_id")
    rfq = None
    quotes = []
    
    if rfq_id:
        rfq = db.query(RFQ).filter(RFQ.id == int(rfq_id)).first()
        if rfq:
            quotes = db.query(Quote).filter(Quote.rfq_id == rfq.id).all()
            
            # Calculate scores for quotes
            for quote in quotes:
                # Simple scoring algorithm
                price_score = 100 - ((quote.total_price / 10000) * 20)  # Lower price = higher score
                delivery_score = 100 - (int(quote.delivery_time.split()[0]) * 5) if quote.delivery_time else 50
                quote.score = int((price_score + delivery_score) / 2)
                
            # Sort by score
            quotes.sort(key=lambda x: x.score, reverse=True)
    else:
        # Get all quotes
        quotes = db.query(Quote).order_by(Quote.created_at.desc()).limit(10).all()
        for quote in quotes:
            quote.score = 75  # Default score
    
    return templates.TemplateResponse("quote_comparison.html", {
        "request": request, 
        "quotes": quotes, 
        "rfq": rfq,
        "current_user": user
    })

@app.get("/projects", response_class=HTMLResponse, name="projects_list")
async def projects_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    projects = [
        {"name": "Summer Sourcing 2024", "status": "Active", "start_date": "2024-05-01", "end_date": "2024-08-31"},
        {"name": "Winter Menu Planning", "status": "Planning", "start_date": "2024-09-01", "end_date": "2024-12-15"}
    ]
    return templates.TemplateResponse("projects.html", {"request": request, "projects": projects, "current_user": user})

# Include auth routes
from app.routes.auth_routes import include_auth_routes
include_auth_routes(app)

# Include agent routes
from app.routes.agent_routes import router as agent_router
app.include_router(agent_router)

# Include orchestrator routes
from app.routes.orchestrator_routes import include_orchestrator_routes
include_orchestrator_routes(app)

# Include web scraper routes
from app.routes.scraper_routes import include_scraper_routes
include_scraper_routes(app)

# Include RFQ routes
from app.routes.rfq_routes import include_rfq_routes
include_rfq_routes(app)

# Include quote routes
from app.routes.quote_routes import include_quote_routes
include_quote_routes(app)

# Include email routes
from app.routes.email_routes import include_email_routes
include_email_routes(app)

# Include planning routes
from app.routes.planning_routes import include_planning_routes
include_planning_routes(app)

# Include notification routes
from app.routes.simple_notification_routes import include_notification_routes
include_notification_routes(app)

# Include order routes
from app.routes.order_routes import router as order_router
app.include_router(order_router)

# Include file routes
from app.routes.file_routes import router as file_router
app.include_router(file_router)

# Include supplier API routes
from app.routes.supplier_api_routes import include_supplier_api_routes
include_supplier_api_routes(app)

# Include product routes
from app.routes.product_routes import include_product_routes
include_product_routes(app)

# Include Bootstrap routes
from app.routes.bootstrap_routes import router as bootstrap_router
app.include_router(bootstrap_router)

# Include AI test routes
from app.routes.ai_test_routes import router as ai_test_router
app.include_router(ai_test_router)

# Include Email test routes
from app.routes.email_test_routes import router as email_test_router
app.include_router(email_test_router)

# Include data mining routes
from app.routes.data_mining_routes import include_data_mining_routes
include_data_mining_routes(app)

# Include notification routes (full version)
from app.routes.notification_routes import include_notification_routes as include_full_notification_routes
include_full_notification_routes(app)

# Agent dashboard route
@app.get("/agent-dashboard", response_class=HTMLResponse, name="agent_dashboard")
async def agent_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("agent_dashboard.html", {"request": request, "current_user": user})

# Add missing routes for screens returning 404
@app.get("/quotes", response_class=HTMLResponse, name="quotes_list")
async def quotes_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    quotes = [
        {"id": 1, "rfq_id": "RFQ-001", "supplier": "ABC Foods", "amount": 15000, "status": "Pending"},
        {"id": 2, "rfq_id": "RFQ-002", "supplier": "XYZ Suppliers", "amount": 18000, "status": "Accepted"}
    ]
    return templates.TemplateResponse("quotes.html", {"request": request, "quotes": quotes, "current_user": user})

@app.get("/autopilot", response_class=HTMLResponse, name="autopilot_dashboard")
async def autopilot_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("autopilot_dashboard.html", {"request": request, "current_user": user})

@app.get("/agent", response_class=HTMLResponse, name="agent_dashboard_alt")
async def agent_dashboard_alt(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("agent_dashboard.html", {"request": request, "current_user": user})

@app.get("/supplier-portal", response_class=HTMLResponse, name="supplier_portal")
async def supplier_portal(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("supplier_portal.html", {"request": request, "current_user": user})

@app.get("/email-intelligence", response_class=HTMLResponse, name="email_intelligence")
async def email_intelligence(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("email_intelligence.html", {"request": request, "current_user": user})

@app.get("/quote-comparison", response_class=HTMLResponse, name="quote_comparison_alt")
async def quote_comparison_alt(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("quote_comparison.html", {"request": request, "current_user": user})

# V0 Component routes
@app.get("/v0/rfq-form", response_class=HTMLResponse, name="v0_rfq_form")
async def v0_rfq_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("v0-components/sample-rfq-form.html", {"request": request, "current_user": user})

@app.get("/v0/sample-rfq-form", response_class=HTMLResponse, name="v0_sample_rfq_form")
async def v0_sample_rfq_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("v0-components/sample-rfq-form.html", {"request": request, "current_user": user})

# Operator dashboard route - unified control center
@app.get("/operator", response_class=HTMLResponse, name="operator_dashboard")
async def operator_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("operator_dashboard.html", {"request": request, "current_user": user})

# Orchestrator dashboard route - automation control
@app.get("/orchestrator", response_class=HTMLResponse, name="orchestrator_dashboard")
async def orchestrator_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("orchestrator_dashboard.html", {"request": request, "current_user": user})

@app.get("/system-status", response_class=HTMLResponse, name="system_status")
async def system_status(request: Request):
    """System status dashboard - no authentication required for monitoring"""
    return templates.TemplateResponse("system_status.html", {"request": request})

# Error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with custom error pages"""
    if request.url.path.startswith("/api/"):
        # Return JSON for API endpoints
        return {"detail": exc.detail, "status_code": exc.status_code}
    
    # Return HTML error page for web routes
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "current_user": None
        },
        status_code=exc.status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    if request.url.path.startswith("/api/"):
        return {"detail": "Invalid request data", "errors": exc.errors()}
    
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 400,
            "detail": "Invalid request data",
            "current_user": None
        },
        status_code=400
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    if request.url.path.startswith("/api/"):
        return {"detail": "Internal server error", "status_code": 500}
    
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "status_code": 500,
            "detail": "An unexpected error occurred",
            "current_user": None
        },
        status_code=500
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 