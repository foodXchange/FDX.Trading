"""
FoodXchange - AI-Powered B2B Food Sourcing Platform
Main FastAPI application with integrated product analysis system
"""

from fastapi import FastAPI, Request, Form, Depends, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import os
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "buyers": "/buyers"
    }
    
    if name == "static" and "filename" in path_params:
        return f"/static/{path_params['filename']}"
    
    return routes.get(name, "/")

# Add url_for to template globals
templates.env.globals["url_for"] = url_for

# Simple database session mock (replace with actual database)
def get_db():
    return None

def get_current_user_context(request: Request, db=None):
    return None

# Simple login handler (temporary - bypasses database)
@app.post("/auth/login")
async def simple_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """Simple login that works without database - defaults to admin"""
    # For testing - accept any email/password and log in as admin
    if email and password:
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
    from foodxchange.routes import product_analysis_routes
    
    # Include routers
    app.include_router(product_analysis_routes.router)
    app.include_router(buyers_routes.router)
    
    logger.info("✅ Route modules loaded successfully")
    
except ImportError as e:
    logger.warning(f"⚠️ Some route modules could not be loaded: {e}")

@app.get("/product-analysis/")
async def product_analysis_page(request: Request):
    """Product Analysis page using Jinja2 template"""
    try:
        return templates.TemplateResponse("pages/product_analysis.html", {"request": request})
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.post("/product-analysis/analyze-image")
async def analyze_product_image(
    image: UploadFile = File(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None)
):
    """Analyze product image using AI"""
    try:
        import os
        import base64
        from foodxchange.services.product_analysis_service import ProductAnalysisService
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(os.getcwd(), "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded image
        image_path = os.path.join(upload_dir, image.filename)
        with open(image_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
        
        # Initialize AI service
        ai_service = ProductAnalysisService()
        
        # Analyze image using AI
        analysis_result = await ai_service.analyze_product_image(image_path)
        
        if "error" in analysis_result:
            return {"success": False, "error": analysis_result["error"]}
        
        # Generate product brief
        user_query = ""
        if product_description:
            user_query = f"Additional product information: {product_description}"
        if product_category:
            user_query += f" Category: {product_category}"
        
        brief_result = await ai_service.generate_product_brief(analysis_result, user_query)
        
        # Search for similar products
        similar_products = await ai_service.search_similar_products(
            analysis_result.get("product_name", ""),
            analysis_result.get("category", "")
        )
        
        # Convert image to base64 for display
        image_base64 = base64.b64encode(content).decode('utf-8')
        image_mime_type = image.content_type or 'image/jpeg'
        data_url = f"data:{image_mime_type};base64,{image_base64}"
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products,
            "analyzed_images": [data_url]
        }
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        return {"success": False, "error": f"Failed to analyze image: {str(e)}"}

@app.post("/product-analysis/analyze-image-url")
async def analyze_product_image_url(
    image_url: str = Form(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None)
):
    """Analyze product image from URL using AI"""
    try:
        from foodxchange.services.product_analysis_service import ProductAnalysisService
        
        # Initialize AI service
        ai_service = ProductAnalysisService()
        
        # Analyze image using AI
        analysis_result = await ai_service.analyze_product_image(image_url)
        
        if "error" in analysis_result:
            return {"success": False, "error": analysis_result["error"]}
        
        # Generate product brief
        user_query = ""
        if product_description:
            user_query = f"Additional product information: {product_description}"
        if product_category:
            user_query += f" Category: {product_category}"
        
        brief_result = await ai_service.generate_product_brief(analysis_result, user_query)
        
        # Search for similar products
        similar_products = await ai_service.search_similar_products(
            analysis_result.get("product_name", ""),
            analysis_result.get("category", "")
        )
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products,
            "analyzed_images": [image_url]
        }
    except Exception as e:
        logger.error(f"Error analyzing image URL: {e}")
        return {"success": False, "error": f"Failed to analyze image URL: {str(e)}"}

@app.post("/product-analysis/save-project")
async def save_analysis_as_project(
    name: str = Form(...),
    description: str = Form(None),
    buyer_id: Optional[str] = Form(None),
    priority: str = Form("medium"),
    search_type: Optional[str] = Form(None),
    analysis_data: str = Form(...)
):
    """Save analysis as project"""
    try:
        import os
        import json
        from datetime import datetime
        
        # Create projects directory if it doesn't exist
        projects_dir = os.path.join(os.getcwd(), "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"project_{timestamp}.json"
        filepath = os.path.join(projects_dir, filename)
        
        # Prepare project data
        project_data = {
            "name": name,
            "description": description,
            "buyer_id": buyer_id if buyer_id and buyer_id != "" else None,
            "priority": priority,
            "search_type": search_type or "image",
            "analysis_data": json.loads(analysis_data),
            "created_at": datetime.now().isoformat()
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": "Project saved successfully",
            "filename": filename
        }
    except Exception as e:
        logger.error(f"Error saving project: {e}")
        return {
            "success": False,
            "message": "Error saving project"
        }

@app.get("/")
async def landing(request: Request):
    """Landing page using Jinja2 template"""
    try:
        return templates.TemplateResponse("pages/landing.html", {"request": request})
    except Exception as e:
        logger.error(f"Template error: {e}")
        return HTMLResponse(content=f"Template error: {str(e)}", status_code=500)

@app.get("/dashboard")
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
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True) 