from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
import logging

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

def get_current_user_context():
    # In a real app, fetch from session or auth
    return {
        "name": "Admin",
        "initials": "AD"
    }

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request, "current_user": get_current_user_context()})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    error = request.query_params.get("error")
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    stats = {
        "suppliers": 0,
        "rfqs": 0,
        "quotes": 0,
        "emails": 0
    }
    return templates.TemplateResponse("simple_dashboard.html", {"request": request, "stats": stats, "current_user": get_current_user_context()})

@app.get("/suppliers", response_class=HTMLResponse, name="suppliers_list")
async def suppliers_list(request: Request):
    suppliers = [
        {"id": 1, "name": "Mediterranean Delights", "location": "Greece", "products": ["Olive Oil", "Feta Cheese"], "status": "active"},
        {"id": 2, "name": "Italian Fine Foods", "location": "Italy", "products": ["Pasta", "Tomatoes"], "status": "active"},
        {"id": 3, "name": "Spanish Imports Co", "location": "Spain", "products": ["Jamón", "Manchego"], "status": "pending"}
    ]
    return templates.TemplateResponse("suppliers.html", {"request": request, "suppliers": suppliers, "current_user": get_current_user_context()})

@app.get("/suppliers/add", response_class=HTMLResponse, name="add_supplier")
async def add_supplier(request: Request):
    return templates.TemplateResponse("base.html", {"request": request, "title": "Add Supplier", "current_user": get_current_user_context()})

@app.get("/suppliers/{supplier_id}", response_class=HTMLResponse, name="view_supplier")
async def view_supplier(request: Request, supplier_id: int):
    return templates.TemplateResponse("base.html", {"request": request, "title": f"Supplier {supplier_id}", "current_user": get_current_user_context()})

@app.get("/suppliers/{supplier_id}/edit", response_class=HTMLResponse, name="edit_supplier")
async def edit_supplier(request: Request, supplier_id: int):
    return templates.TemplateResponse("base.html", {"request": request, "title": f"Edit Supplier {supplier_id}", "current_user": get_current_user_context()})

@app.get("/rfq/new", response_class=HTMLResponse, name="new_rfq")
async def new_rfq(request: Request):
    return templates.TemplateResponse("rfq_new.html", {"request": request, "current_user": get_current_user_context()})

@app.post("/rfq/new", response_class=HTMLResponse)
async def create_rfq(request: Request, product: str = Form(...), quantity: int = Form(...), deadline: str = Form(...), notes: str = Form(None)):
    # Placeholder: Save RFQ to database
    # Redirect to dashboard or show confirmation
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": {"suppliers": 0, "rfqs": 1, "quotes": 0, "emails": 0}, "message": "RFQ created!", "current_user": get_current_user_context()})

@app.get("/orders", response_class=HTMLResponse, name="orders_list")
async def orders_list(request: Request):
    return templates.TemplateResponse("orders.html", {"request": request, "current_user": get_current_user_context()})

@app.get("/products", response_class=HTMLResponse, name="products_list")
async def products_list(request: Request):
    return templates.TemplateResponse("products.html", {"request": request, "current_user": get_current_user_context()})

@app.get("/analytics", response_class=HTMLResponse, name="analytics")
async def analytics(request: Request):
    kpis = {
        "total_spend": 100000,
        "cost_savings": 15000,
        "suppliers_engaged": 12,
        "rfqs_sent": 34
    }
    return templates.TemplateResponse("analytics.html", {"request": request, "kpis": kpis, "current_user": get_current_user_context()})

@app.get("/emails", response_class=HTMLResponse, name="email_intelligence")
async def email_intelligence(request: Request):
    emails = [
        {"sender": "supplier1@example.com", "subject": "Quote for Olive Oil", "date": "2024-06-01", "insight": "Potential cost savings identified."},
        {"sender": "supplier2@example.com", "subject": "RFQ Response", "date": "2024-06-02", "insight": "Supplier offers volume discount."}
    ]
    return templates.TemplateResponse("email_intelligence.html", {"request": request, "emails": emails, "current_user": get_current_user_context()})

@app.get("/quotes/comparison", response_class=HTMLResponse, name="quote_comparison")
async def quote_comparison(request: Request):
    quotes = [
        {"supplier": "Mediterranean Delights", "product": "Olive Oil", "price": 1200, "lead_time": 7, "notes": "Includes shipping."},
        {"supplier": "Italian Fine Foods", "product": "Olive Oil", "price": 1250, "lead_time": 10, "notes": "Faster delivery available."}
    ]
    return templates.TemplateResponse("quote_comparison.html", {"request": request, "quotes": quotes, "current_user": get_current_user_context()})

@app.get("/projects", response_class=HTMLResponse, name="projects_list")
async def projects_list(request: Request):
    projects = [
        {"name": "Summer Sourcing 2024", "status": "Active", "start_date": "2024-05-01", "end_date": "2024-08-31"},
        {"name": "Winter Menu Planning", "status": "Planning", "start_date": "2024-09-01", "end_date": "2024-12-15"}
    ]
    return templates.TemplateResponse("projects.html", {"request": request, "projects": projects, "current_user": get_current_user_context()})

# Include auth routes
# TODO: Uncomment when auth_routes.py is created
# from app.routes.auth_routes import include_auth_routes
# include_auth_routes(app)

# Include agent routes
from app.routes.agent_routes import router as agent_router
app.include_router(agent_router)

# Agent dashboard route
@app.get("/agent-dashboard", response_class=HTMLResponse, name="agent_dashboard")
async def agent_dashboard(request: Request):
    return templates.TemplateResponse("agent_dashboard.html", {"request": request, "current_user": get_current_user_context()})

# Operator dashboard route - unified control center
@app.get("/operator", response_class=HTMLResponse, name="operator_dashboard")
async def operator_dashboard(request: Request):
    return templates.TemplateResponse("operator_dashboard.html", {"request": request, "current_user": get_current_user_context()})

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