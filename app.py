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
from database import get_suppliers  # Import database functions

# Load environment variables from .env file
# This reads DATABASE_URL and other settings
load_dotenv()

# === CREATE APP ===
# Create the FastAPI application instance
app = FastAPI(
    title="FoodXchange",  # Name of your app
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

# === FAKE DATABASE ===
# For now, we'll use a simple list to store users
# Later, we'll connect to Azure PostgreSQL
users = []

# === HELPER FUNCTIONS ===
def get_app_context():
    """
    Returns common data needed by all templates
    This function provides data that every page needs
    """
    return {
        "app_name": "FoodXchange",  # App name to show in navbar
        "debug": os.getenv("DEBUG", "False")  # Debug mode from .env
    }

# === ROUTES (PAGES) ===

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
    return templates.TemplateResponse("login.html", context)

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
        # Successful login - redirect to dashboard
        return RedirectResponse(url="/dashboard", status_code=303)
    else:
        # Failed login - show error message
        context = {
            "request": request,
            "message": "Invalid email or password. Please try again.",
            "message_type": "danger"  # Bootstrap alert type
        }
        return templates.TemplateResponse("login.html", context)

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
            "users": len(users),
            "active": 5,
            "new": 2
        }
    }
    return templates.TemplateResponse("index.html", context)

# SUPPLIERS PAGE ROUTE - Connected to PostgreSQL
@app.get("/suppliers", response_class=HTMLResponse)
async def suppliers_page(request: Request):
    """
    Suppliers page - shows ALL suppliers with ALL columns from PostgreSQL database
    Uses Bootstrap components and Jinja2 templating
    """
    # Get suppliers from database
    suppliers = get_suppliers()  # This connects to PostgreSQL
    
    # Get unique countries (excluding None/empty)
    countries = sorted(set(s.get('country') for s in suppliers if s.get('country')))
    
    # Context for template
    context = {
        "request": request,
        **get_app_context(),
        "suppliers": suppliers,  # List of ALL suppliers from database
        "countries": countries  # List of unique countries for filter
    }
    
    return templates.TemplateResponse("suppliers_import.html", context)

# DATA VIEWER ROUTE - View imported Excel data
@app.get("/data", response_class=HTMLResponse)
async def data_viewer(request: Request):
    """View imported supplier data from Excel"""
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get first 100 rows from suppliers_test
        cursor.execute("SELECT * FROM suppliers_test LIMIT 100")
        data = cursor.fetchall()
        
        # Get column names
        columns = [desc['name'] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        context = {
            "request": request,
            **get_app_context(),
            "data": data,
            "columns": columns
        }
        
        return templates.TemplateResponse("data_viewer.html", context)
        
    except Exception as e:
        context = {
            "request": request,
            **get_app_context(),
            "data": [],
            "columns": [],
            "error": str(e)
        }
        return templates.TemplateResponse("data_viewer.html", context)

# USERS PAGE ROUTE
@app.get("/users", response_class=HTMLResponse)  # GET request to /users returns HTML
async def users_page(request: Request):
    """
    Users page - shows all users in a table
    """
    context = {
        "request": request,  # Required by Jinja2
        **get_app_context(),  # App name and other common data
        "users": users  # Pass the users list to template
    }
    return templates.TemplateResponse("users.html", context)

# ADD USER ROUTE
@app.post("/users/add")  # POST request to /users/add
async def add_user(name: str = Form(...), email: str = Form(...)):
    """
    Handles form submission to add a new user
    Form(...) means the data comes from an HTML form
    name: User's full name from form input
    email: User's email from form input
    """
    # Create new user dictionary
    new_user = {
        "id": len(users) + 1,  # Simple ID generation
        "name": name,  # Name from form
        "email": email  # Email from form
    }
    # Add user to our list
    users.append(new_user)
    
    # Redirect back to users page to see the new user
    return RedirectResponse(url="/users", status_code=303)

# API ROUTES (for JavaScript/AJAX)

# API: Get all users as JSON
@app.get("/api/users")  # GET request returns JSON data
async def api_get_users():
    """
    API endpoint - returns users as JSON
    This can be used by JavaScript or mobile apps
    """
    return {
        "users": users,  # List of all users
        "count": len(users)  # Total count
    }

# API: Add user via API
@app.post("/api/users")  # POST request to add user via API
async def api_add_user(name: str, email: str):
    """
    API endpoint to add a user
    Used by JavaScript or API clients
    """
    new_user = {
        "id": len(users) + 1,
        "name": name,
        "email": email
    }
    users.append(new_user)
    return {"message": "User added!", "user": new_user}

# ABOUT PAGE ROUTE
@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """
    About page - you can create an about.html template for this
    """
    context = {
        "request": request,
        **get_app_context()
    }
    # For now, redirect to home since we don't have about.html yet
    return RedirectResponse(url="/", status_code=303)

# === RUN THE APP ===
# This code runs when you execute: python app.py
if __name__ == "__main__":
    import uvicorn  # Import the server
    # Run the app on all network interfaces (0.0.0.0) on port 9000
    # reload=True means the server restarts when you change code
    uvicorn.run("app:app", host="0.0.0.0", port=9000, reload=True)