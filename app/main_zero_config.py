"""
Food Xchange Platform - ZERO CONFIG VERSION
This version works out of the box with NO external dependencies or configuration.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

# Create FastAPI app with minimal configuration
app = FastAPI(
    title="Food Xchange Platform - Zero Config",
    description="B2B Food Marketplace - Works out of the box",
    version="1.0.0"
)

# CORS - allow everything for development
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

# Simple authentication
security = HTTPBasic()

# In-memory data storage (no database needed!)
class ZeroConfigDB:
    """In-memory database that works without any external dependencies"""
    
    def __init__(self):
        self.users = {
            "admin": {
                "id": 1,
                "username": "admin",
                "email": "admin@foodxchange.com",
                "password": "admin123",  # In real app, this would be hashed
                "is_admin": True,
                "created_at": datetime.now()
            }
        }
        
        self.rfqs = [
            {
                "id": 1,
                "title": "Organic Tomatoes",
                "description": "Looking for organic tomatoes for restaurant",
                "quantity": 1000,
                "unit": "kg",
                "budget": 15000,
                "status": "open",
                "created_by": 1,
                "created_at": datetime.now() - timedelta(days=2)
            },
            {
                "id": 2,
                "title": "Fresh Dairy Products",
                "description": "Need fresh milk, cheese, and yogurt",
                "quantity": 500,
                "unit": "kg",
                "budget": 8000,
                "status": "closed",
                "created_by": 1,
                "created_at": datetime.now() - timedelta(days=5)
            }
        ]
        
        self.orders = [
            {
                "id": 1,
                "rfq_id": 1,
                "supplier_id": 1,
                "product": "Organic Tomatoes",
                "quantity": 1000,
                "unit_price": 15.00,
                "total_amount": 15000,
                "status": "shipped",
                "created_at": datetime.now() - timedelta(days=1)
            },
            {
                "id": 2,
                "rfq_id": 2,
                "supplier_id": 2,
                "product": "Fresh Dairy",
                "quantity": 500,
                "unit_price": 16.00,
                "total_amount": 8000,
                "status": "delivered",
                "created_at": datetime.now() - timedelta(days=3)
            }
        ]
        
        self.suppliers = [
            {
                "id": 1,
                "name": "ABC Foods",
                "email": "contact@abcfoods.com",
                "phone": "+1-555-0123",
                "rating": 4.5,
                "products_count": 150,
                "is_active": True,
                "created_at": datetime.now() - timedelta(days=30)
            },
            {
                "id": 2,
                "name": "XYZ Suppliers",
                "email": "info@xyzsuppliers.com",
                "phone": "+1-555-0456",
                "rating": 4.2,
                "products_count": 200,
                "is_active": True,
                "created_at": datetime.now() - timedelta(days=25)
            }
        ]
        
        self.quotes = [
            {
                "id": 1,
                "rfq_id": 1,
                "supplier_id": 1,
                "supplier_name": "ABC Foods",
                "amount": 15000,
                "status": "pending",
                "created_at": datetime.now() - timedelta(hours=2)
            },
            {
                "id": 2,
                "rfq_id": 1,
                "supplier_id": 2,
                "supplier_name": "XYZ Suppliers",
                "amount": 18000,
                "status": "accepted",
                "created_at": datetime.now() - timedelta(hours=1)
            }
        ]
        
        self.products = [
            {
                "id": 1,
                "name": "Organic Tomatoes",
                "category": "Produce",
                "price": 15.00,
                "supplier_id": 1,
                "supplier_name": "ABC Foods",
                "in_stock": True,
                "created_at": datetime.now() - timedelta(days=10)
            },
            {
                "id": 2,
                "name": "Fresh Milk",
                "category": "Dairy",
                "price": 8.50,
                "supplier_id": 2,
                "supplier_name": "XYZ Suppliers",
                "in_stock": True,
                "created_at": datetime.now() - timedelta(days=8)
            }
        ]
        
        self.notifications = [
            {
                "id": 1,
                "title": "New RFQ Available",
                "message": "New RFQ for Organic Tomatoes has been posted",
                "type": "info",
                "is_read": False,
                "created_at": datetime.now() - timedelta(hours=1)
            },
            {
                "id": 2,
                "title": "Order Shipped",
                "message": "Order #1 has been shipped successfully",
                "type": "success",
                "is_read": True,
                "created_at": datetime.now() - timedelta(hours=3)
            }
        ]

# Global database instance
db = ZeroConfigDB()

# Authentication helper
def get_current_user(request: Request):
    """Simple authentication - always return admin user for demo"""
    return {
        "id": 1,
        "username": "admin",
        "email": "admin@foodxchange.com",
        "is_admin": True
    }

# ============================================================================
# ALL SCREEN ROUTES - ZERO CONFIG APPROACH
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("dashboard.html", {"request": request, "current_user": user})

# Core Business Screens
@app.get("/rfqs", response_class=HTMLResponse)
async def rfqs_list(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("rfqs.html", {"request": request, "current_user": user, "rfqs": db.rfqs})

@app.get("/rfq/new", response_class=HTMLResponse)
async def new_rfq(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("rfq_new.html", {"request": request, "current_user": user})

@app.get("/orders", response_class=HTMLResponse)
async def orders_list(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("orders.html", {"request": request, "current_user": user, "orders": db.orders})

@app.get("/products", response_class=HTMLResponse)
async def products_list(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("products.html", {"request": request, "current_user": user, "products": db.products})

@app.get("/suppliers", response_class=HTMLResponse)
async def suppliers_list(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("suppliers.html", {"request": request, "current_user": user, "suppliers": db.suppliers})

@app.get("/quotes", response_class=HTMLResponse)
async def quotes_list(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("quotes.html", {"request": request, "current_user": user, "quotes": db.quotes})

@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("analytics.html", {"request": request, "current_user": user})

# Advanced Features
@app.get("/planning", response_class=HTMLResponse)
async def planning_dashboard(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("planning_dashboard.html", {"request": request, "current_user": user})

@app.get("/orchestrator", response_class=HTMLResponse)
async def orchestrator_dashboard(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("orchestrator_dashboard.html", {"request": request, "current_user": user})

@app.get("/autopilot", response_class=HTMLResponse)
async def autopilot_dashboard(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("autopilot_dashboard.html", {"request": request, "current_user": user})

@app.get("/agent", response_class=HTMLResponse)
async def agent_dashboard(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("agent_dashboard.html", {"request": request, "current_user": user})

@app.get("/operator", response_class=HTMLResponse)
async def operator_dashboard(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("operator_dashboard.html", {"request": request, "current_user": user})

@app.get("/supplier-portal", response_class=HTMLResponse)
async def supplier_portal(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("supplier_portal.html", {"request": request, "current_user": user})

@app.get("/email-intelligence", response_class=HTMLResponse)
async def email_intelligence(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("email_intelligence.html", {"request": request, "current_user": user})

@app.get("/quote-comparison", response_class=HTMLResponse)
async def quote_comparison(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("quote_comparison.html", {"request": request, "current_user": user})

@app.get("/projects", response_class=HTMLResponse)
async def projects_list(request: Request):
    user = get_current_user(request)
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
async def v0_rfq_form(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("v0-components/sample-rfq-form.html", {"request": request, "current_user": user})

@app.get("/v0/sample-rfq-form", response_class=HTMLResponse)
async def v0_sample_rfq_form(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("v0-components/sample-rfq-form.html", {"request": request, "current_user": user})

# Bootstrap Screens
@app.get("/bootstrap/rfq", response_class=HTMLResponse)
async def bootstrap_rfq(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("bootstrap/rfq-form.html", {"request": request, "current_user": user})

@app.get("/bootstrap/orders", response_class=HTMLResponse)
async def bootstrap_orders(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("bootstrap/order-management.html", {"request": request, "current_user": user})

@app.get("/bootstrap/analytics", response_class=HTMLResponse)
async def bootstrap_analytics(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("bootstrap/analytics.html", {"request": request, "current_user": user})

@app.get("/bootstrap/help", response_class=HTMLResponse)
async def bootstrap_help(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("bootstrap/help.html", {"request": request, "current_user": user})

# ============================================================================
# WORKING API ENDPOINTS - ZERO CONFIG APPROACH
# ============================================================================

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "config": "zero-config"
    }

@app.get("/api/rfq")
async def api_rfq():
    return {"rfqs": db.rfqs}

@app.get("/api/orders")
async def api_orders():
    return {"orders": db.orders}

@app.get("/api/products")
async def api_products():
    return {"products": db.products}

@app.get("/api/suppliers")
async def api_suppliers():
    return {"suppliers": db.suppliers}

@app.get("/api/quotes")
async def api_quotes():
    return {"quotes": db.quotes}

@app.get("/api/notifications")
async def api_notifications():
    return {"notifications": db.notifications}

@app.get("/api/email-test/status")
async def email_test_status():
    return {"status": "working", "message": "Email service is operational (mock)"}

@app.get("/api/agents")
async def api_agents():
    return {
        "agents": [
            {"id": 1, "name": "Data Mining Agent", "status": "Active", "last_run": datetime.now().isoformat()},
            {"id": 2, "name": "Email Monitor Agent", "status": "Active", "last_run": datetime.now().isoformat()}
        ]
    }

@app.get("/api/ai/test")
async def ai_test():
    return {"status": "working", "message": "AI service is operational (mock)"}

@app.get("/api/files")
async def api_files():
    return {
        "files": [
            {"id": 1, "name": "products.csv", "size": "2.5MB", "uploaded": datetime.now().isoformat()},
            {"id": 2, "name": "suppliers.xlsx", "size": "1.8MB", "uploaded": datetime.now().isoformat()}
        ]
    }

@app.get("/api/data-mining")
async def api_data_mining():
    return {"status": "working", "message": "Data mining service is operational (mock)"}

@app.get("/api/planning")
async def api_planning():
    return {"status": "working", "message": "Planning service is operational (mock)"}

@app.get("/api/orchestrator")
async def api_orchestrator():
    return {"status": "working", "message": "Orchestrator service is operational (mock)"}

@app.get("/api/auth/login")
async def api_login():
    return {"status": "working", "message": "Authentication service is operational (mock)"}

@app.get("/api/auth/register")
async def api_register():
    return {"status": "working", "message": "Registration service is operational (mock)"}

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return templates.TemplateResponse("error.html", {"request": request, "error_code": 404, "error_message": "Page not found"})

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return templates.TemplateResponse("error.html", {"request": request, "error_code": 500, "error_message": "Internal server error"})

# ============================================================================
# STARTUP EVENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    print("🚀 Food Xchange Platform - Zero Config Version Started!")
    print("✅ No database setup required")
    print("✅ No configuration files needed")
    print("✅ All APIs working with mock data")
    print("✅ All screens accessible")
    print("🌐 Access at: http://localhost:8000")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 