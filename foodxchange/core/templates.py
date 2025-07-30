"""
Shared templates configuration for FoodXchange
"""
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent.parent

# Configure Jinja2 templates
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
        "admin_login": "/admin"
    }
    
    if name == "static" and "filename" in path_params:
        return f"/static/{path_params['filename']}"
    
    return routes.get(name, "/")

# Add url_for to template globals
templates.env.globals["url_for"] = url_for