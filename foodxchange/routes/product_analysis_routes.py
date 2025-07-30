"""
Product Analysis Routes for FoodXchange
AI-powered product analysis and brief generation endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any, List
import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/product-analysis", tags=["Product Analysis"])

@router.get("/", response_class=HTMLResponse)
@router.head("/", response_class=HTMLResponse)
async def product_analysis_page(request: Request):
    """Product Analysis Dashboard - Using Jinja2 template"""
    try:
        from pathlib import Path
        from fastapi.templating import Jinja2Templates
        
        # Get the directory where this file is located
        BASE_DIR = Path(__file__).resolve().parent.parent
        templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
        
        # Add the url_for function to this templates instance
        def url_for(name: str, **path_params) -> str:
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
                "dashboard.index": "/dashboard"
            }
            
            if name == "static" and "filename" in path_params:
                return f"/static/{path_params['filename']}"
            
            base_route = routes.get(name, "/")
            
            for param, value in path_params.items():
                base_route = base_route.replace(f"{{{param}}}", str(value))
            
            return base_route
        
        templates.env.globals["url_for"] = url_for
        
        return templates.TemplateResponse("pages/product_analysis.html", {"request": request})
    except Exception as e:
        logger.error(f"Error in product_analysis_page: {e}")
        # Return a simple error page instead of raising an exception
        return HTMLResponse(content=f"""
        <html>
        <head><title>Product Analysis - Error</title></head>
        <body>
            <h1>Product Analysis Page</h1>
            <p>There was an error loading the page: {str(e)}</p>
            <p><a href="/dashboard">Back to Dashboard</a></p>
        </body>
        </html>
        """, status_code=500)

@router.get("/test")
async def test_product_analysis():
    """Test route to verify the router is working"""
    return {"message": "Product analysis router is working!"}

@router.post("/analyze-image")
async def analyze_product_image(
    image: UploadFile = File(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None)
):
    """Analyze product image using AI - Simplified version"""
    try:
        # Analyze product image using AI services
        # TODO: Implement actual AI analysis when services are configured
        
        # Convert image to base64 for display
        import base64
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        image_mime_type = image.content_type or 'image/jpeg'
        data_url = f"data:{image_mime_type};base64,{image_base64}"
        
        # Mock analysis result
        analysis_result = {
            "product_name": "Sample Product",
            "category": product_category or "Food & Beverage",
            "confidence": 0.85,
            "description": product_description or "Product analysis completed successfully"
        }
        
        # Mock brief result
        brief_result = {
            "product_name": "Sample Product",
            "producing_company": "Sample Company",
            "brand_name": "Sample Brand",
            "country_of_origin": "United States",
            "category": product_category or "Food & Beverage",
            "packaging_type": "Plastic Container",
            "product_weight": "500g",
            "product_appearance": "Reddish-brown powder",
            "storage_conditions": "Store in a cool, dry place",
            "target_market": "Retail consumers",
            "kosher": "Yes",
            "kosher_writings": "OU",
            "gluten_free": "Yes",
            "sugar_free": "No",
            "no_sugar_added": "Yes"
        }
        
        # Mock similar products
        similar_products = [
            {
                "name": "Similar Product 1",
                "supplier": "Supplier A",
                "price": "$15.99",
                "rating": "4.5★",
                "availability": "In Stock"
            },
            {
                "name": "Similar Product 2", 
                "supplier": "Supplier B",
                "price": "$12.99",
                "rating": "4.2★",
                "availability": "Limited Stock"
            }
        ]
        
        return {
            "success": True,
            "analysis": analysis_result,
            "brief": brief_result,
            "similar_products": similar_products,
            "analyzed_images": [data_url]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze image")

@router.post("/analyze-multiple-images")
async def analyze_multiple_images(
    images: List[UploadFile] = File(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None)
):
    """Analyze multiple product images using AI"""
    try:
        if not images:
            raise HTTPException(status_code=400, detail="No images provided")
        
        analysis_results = []
        brief_results = []
        analyzed_images = []
        
        for image in images:
            # Convert image to base64 for display
            import base64
            image_content = await image.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            image_mime_type = image.content_type or 'image/jpeg'
            data_url = f"data:{image_mime_type};base64,{image_base64}"
            analyzed_images.append(data_url)
            
            # Mock analysis result for each image
            analysis_result = {
                "product_name": f"Sample Product {len(analysis_results) + 1}",
                "category": product_category or "Food & Beverage",
                "confidence": 0.85,
                "description": product_description or f"Product analysis completed successfully for image {len(analysis_results) + 1}"
            }
            analysis_results.append(analysis_result)
            
            # Mock brief result for each image
            brief_result = {
                "product_name": f"Sample Product {len(brief_results) + 1}",
                "producing_company": "Sample Company",
                "brand_name": "Sample Brand",
                "country_of_origin": "United States",
                "category": product_category or "Food & Beverage",
                "packaging_type": "Plastic Container",
                "product_weight": "500g",
                "product_appearance": "Reddish-brown powder",
                "storage_conditions": "Store in a cool, dry place",
                "target_market": "Retail consumers",
                "kosher": "Yes",
                "kosher_writings": "OU",
                "gluten_free": "Yes",
                "sugar_free": "No",
                "no_sugar_added": "Yes"
            }
            brief_results.append(brief_result)
        
        # Mock similar products
        similar_products = [
            {
                "name": "Similar Product 1",
                "supplier": "Supplier A",
                "price": "$15.99",
                "rating": "4.5★",
                "availability": "In Stock"
            },
            {
                "name": "Similar Product 2", 
                "supplier": "Supplier B",
                "price": "$12.99",
                "rating": "4.2★",
                "availability": "Limited Stock"
            }
        ]
        
        return {
            "success": True,
            "analysis": analysis_results,
            "brief": brief_results[0] if brief_results else None,  # Use first brief as main
            "similar_products": similar_products,
            "analyzed_images": analyzed_images
        }
        
    except Exception as e:
        logger.error(f"Error analyzing multiple images: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze images")

@router.post("/save-project")
async def save_analysis_as_project(
    name: str = Form(...),
    description: str = Form(None),
    buyer_id: Optional[str] = Form(None),
    priority: str = Form("medium"),
    search_type: Optional[str] = Form(None),
    analysis_data: str = Form(...)
):
    """Save analysis as a project"""
    try:
        import os
        from datetime import datetime
        
        # Create projects directory if it doesn't exist
        projects_dir = os.path.join(os.getcwd(), "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        # Create project data
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
        import uuid
        project_filename = f"project_{uuid.uuid4()}.json"
        project_path = os.path.join(projects_dir, project_filename)
        
        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": "Project saved successfully",
            "project_filename": project_filename
        }
        
    except Exception as e:
        logger.error(f"Error saving project: {e}")
        raise HTTPException(status_code=500, detail="Failed to save project")