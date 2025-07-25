from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.orm import Session
import os
import logging

from app.database import get_db
from app.auth import SessionAuth, get_current_user_context as get_user_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FoodXchange API")

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

@app.get("/health")
async def health():
    return {"status": "ok"}

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

@app.get("/emails", response_class=HTMLResponse, name="email_intelligence")
async def email_intelligence(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    emails = [
        {"sender": "supplier1@example.com", "subject": "Quote for Olive Oil", "date": "2024-06-01", "insight": "Potential cost savings identified."},
        {"sender": "supplier2@example.com", "subject": "RFQ Response", "date": "2024-06-02", "insight": "Supplier offers volume discount."}
    ]
    return templates.TemplateResponse("email_intelligence.html", {"request": request, "emails": emails, "current_user": user})

@app.get("/quotes/comparison", response_class=HTMLResponse, name="quote_comparison")
async def quote_comparison(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    quotes = [
        {"supplier": "Mediterranean Delights", "product": "Olive Oil", "price": 1200, "lead_time": 7, "notes": "Includes shipping."},
        {"supplier": "Italian Fine Foods", "product": "Olive Oil", "price": 1250, "lead_time": 10, "notes": "Faster delivery available."}
    ]
    return templates.TemplateResponse("quote_comparison.html", {"request": request, "quotes": quotes, "current_user": user})

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

# Agent dashboard route
@app.get("/agent-dashboard", response_class=HTMLResponse, name="agent_dashboard")
async def agent_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("agent_dashboard.html", {"request": request, "current_user": user})

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