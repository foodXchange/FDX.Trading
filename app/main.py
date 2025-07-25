from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from fastapi.responses import HTMLResponse

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
    return templates.TemplateResponse("dashboard.html", {"request": request, "stats": stats, "current_user": get_current_user_context()})

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

# Other routers will be included here
# from .api import auth, rfq, suppliers, quotes, emails, analytics
# app.include_router(auth.router)
# app.include_router(rfq.router)
# ... 