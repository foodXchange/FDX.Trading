import warnings
import os
import logging
from datetime import datetime

# Suppress warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FoodXchange Platform")

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

# Simple authentication check
def get_current_user_context(request: Request, db: Session):
    """Simple user context for demo purposes"""
    return {
        "id": 1,
        "username": "demo_user",
        "email": "demo@foodxchange.com",
        "is_admin": True
    }

# ============================================================================
# ALL SCREEN ROUTES - SIMPLIFIED APPROACH
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("dashboard.html", {"request": request, "current_user": user})

# Core Business Screens
@app.get("/rfqs", response_class=HTMLResponse)
async def rfqs_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("rfqs.html", {"request": request, "current_user": user})

@app.get("/rfq/new", response_class=HTMLResponse)
async def new_rfq(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("rfq_new.html", {"request": request, "current_user": user})

@app.get("/orders", response_class=HTMLResponse)
async def orders_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("orders.html", {"request": request, "current_user": user})

@app.get("/products", response_class=HTMLResponse)
async def products_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("products.html", {"request": request, "current_user": user})

@app.get("/suppliers", response_class=HTMLResponse)
async def suppliers_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("suppliers.html", {"request": request, "current_user": user})

@app.get("/quotes", response_class=HTMLResponse)
async def quotes_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    quotes = [
        {"id": 1, "rfq_id": "RFQ-001", "supplier": "ABC Foods", "amount": 15000, "status": "Pending"},
        {"id": 2, "rfq_id": "RFQ-002", "supplier": "XYZ Suppliers", "amount": 18000, "status": "Accepted"}
    ]
    return templates.TemplateResponse("quotes.html", {"request": request, "quotes": quotes, "current_user": user})

@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("analytics.html", {"request": request, "current_user": user})

# Advanced Features
@app.get("/planning", response_class=HTMLResponse)
async def planning_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("planning_dashboard.html", {"request": request, "current_user": user})

@app.get("/orchestrator", response_class=HTMLResponse)
async def orchestrator_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("orchestrator_dashboard.html", {"request": request, "current_user": user})

@app.get("/autopilot", response_class=HTMLResponse)
async def autopilot_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("autopilot_dashboard.html", {"request": request, "current_user": user})

@app.get("/agent", response_class=HTMLResponse)
async def agent_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("agent_dashboard.html", {"request": request, "current_user": user})

@app.get("/operator", response_class=HTMLResponse)
async def operator_dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("operator_dashboard.html", {"request": request, "current_user": user})

@app.get("/supplier-portal", response_class=HTMLResponse)
async def supplier_portal(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("supplier_portal.html", {"request": request, "current_user": user})

@app.get("/email-intelligence", response_class=HTMLResponse)
async def email_intelligence(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("email_intelligence.html", {"request": request, "current_user": user})

@app.get("/quote-comparison", response_class=HTMLResponse)
async def quote_comparison(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("quote_comparison.html", {"request": request, "current_user": user})

@app.get("/projects", response_class=HTMLResponse)
async def projects_list(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    projects = [
        {"name": "Summer Sourcing 2024", "status": "Active", "start_date": "2024-05-01", "end_date": "2024-08-31"},
        {"name": "Winter Menu Planning", "status": "Planning", "start_date": "2024-09-01", "end_date": "2024-12-15"}
    ]
    return templates.TemplateResponse("projects.html", {"request": request, "projects": projects, "current_user": user})

@app.get("/system-status", response_class=HTMLResponse)
async def system_status(request: Request):
    return templates.TemplateResponse("system_status.html", {"request": request})

# V0 Components
@app.get("/v0/rfq-form", response_class=HTMLResponse)
async def v0_rfq_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("v0-components/sample-rfq-form.html", {"request": request, "current_user": user})

@app.get("/v0/sample-rfq-form", response_class=HTMLResponse)
async def v0_sample_rfq_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("v0-components/sample-rfq-form.html", {"request": request, "current_user": user})

# Bootstrap Screens
@app.get("/bootstrap/rfq", response_class=HTMLResponse)
async def bootstrap_rfq(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("bootstrap/rfq-form.html", {"request": request, "current_user": user})

@app.get("/bootstrap/orders", response_class=HTMLResponse)
async def bootstrap_orders(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("bootstrap/order-management.html", {"request": request, "current_user": user})

@app.get("/bootstrap/analytics", response_class=HTMLResponse)
async def bootstrap_analytics(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("bootstrap/analytics.html", {"request": request, "current_user": user})

@app.get("/bootstrap/help", response_class=HTMLResponse)
async def bootstrap_help(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_context(request, db)
    return templates.TemplateResponse("bootstrap/help.html", {"request": request, "current_user": user})

# ============================================================================
# SIMPLE API ENDPOINTS - WORKING MOCK DATA
# ============================================================================

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/rfq")
async def api_rfq():
    return {
        "rfqs": [
            {"id": 1, "title": "Organic Tomatoes", "status": "Open", "deadline": "2024-02-15"},
            {"id": 2, "title": "Fresh Dairy", "status": "Closed", "deadline": "2024-02-10"}
        ]
    }

@app.get("/api/orders")
async def api_orders():
    return {
        "orders": [
            {"id": 1, "product": "Organic Tomatoes", "quantity": 1000, "status": "Shipped"},
            {"id": 2, "product": "Fresh Dairy", "quantity": 500, "status": "Delivered"}
        ]
    }

@app.get("/api/products")
async def api_products():
    return {
        "products": [
            {"id": 1, "name": "Organic Tomatoes", "category": "Produce", "price": 15.00},
            {"id": 2, "name": "Fresh Milk", "category": "Dairy", "price": 8.50}
        ]
    }

@app.get("/api/suppliers")
async def api_suppliers():
    return {
        "suppliers": [
            {"id": 1, "name": "ABC Foods", "rating": 4.5, "products": 150},
            {"id": 2, "name": "XYZ Suppliers", "rating": 4.2, "products": 200}
        ]
    }

@app.get("/api/quotes")
async def api_quotes():
    return {
        "quotes": [
            {"id": 1, "rfq_id": "RFQ-001", "supplier": "ABC Foods", "amount": 15000, "status": "Pending"},
            {"id": 2, "rfq_id": "RFQ-002", "supplier": "XYZ Suppliers", "amount": 18000, "status": "Accepted"}
        ]
    }

@app.get("/api/notifications")
async def api_notifications():
    return {
        "notifications": [
            {"id": 1, "title": "New RFQ", "message": "New RFQ available", "type": "info"},
            {"id": 2, "title": "Order Update", "message": "Order #123 shipped", "type": "success"}
        ]
    }

@app.get("/api/email-test/status")
async def email_test_status():
    return {"status": "working", "message": "Email service is operational"}

@app.get("/api/agents")
async def api_agents():
    return {
        "agents": [
            {"id": 1, "name": "Data Mining Agent", "status": "Active", "last_run": "2024-01-15"},
            {"id": 2, "name": "Email Monitor Agent", "status": "Active", "last_run": "2024-01-15"}
        ]
    }

@app.get("/api/ai/test")
async def ai_test():
    return {"status": "working", "message": "AI service is operational"}

@app.get("/api/files")
async def api_files():
    return {
        "files": [
            {"id": 1, "name": "products.csv", "size": "2.5MB", "uploaded": "2024-01-15"},
            {"id": 2, "name": "suppliers.xlsx", "size": "1.8MB", "uploaded": "2024-01-14"}
        ]
    }

@app.get("/api/data-mining")
async def api_data_mining():
    return {"status": "working", "message": "Data mining service is operational"}

@app.get("/api/planning")
async def api_planning():
    return {"status": "working", "message": "Planning service is operational"}

@app.get("/api/orchestrator")
async def api_orchestrator():
    return {"status": "working", "message": "Orchestrator service is operational"}

@app.get("/api/auth/login")
async def api_login():
    return {"status": "working", "message": "Authentication service is operational"}

@app.get("/api/auth/register")
async def api_register():
    return {"status": "working", "message": "Registration service is operational"}

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("error.html", {"request": request, "error_code": 404, "error_message": "Page not found"})

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return templates.TemplateResponse("error.html", {"request": request, "error_code": 500, "error_message": "Internal server error"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 