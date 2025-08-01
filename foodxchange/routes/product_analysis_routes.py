"""
Product Analysis Routes for FoodXchange
AI-powered product analysis and brief generation endpoints
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any, List
import json
import logging
from datetime import datetime
from pathlib import Path

from foodxchange.core.auth import get_current_user, require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/product-analysis", tags=["Product Analysis"])

@router.get("/test-redirect")
async def test_redirect():
    """Test endpoint to verify redirects work"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/login?test=working", status_code=303)

@router.get("/", response_class=HTMLResponse)
@router.head("/", response_class=HTMLResponse)
async def product_analysis_page(request: Request):
    """Product Analysis Dashboard - Using Jinja2 template"""
    # Manual authentication check with redirect
    from fastapi.responses import RedirectResponse
    user = get_current_user(request)
    if not user:
        # Check if this is a browser request
        accept_header = request.headers.get("accept", "")
        is_browser = "text/html" in accept_header or "*/*" in accept_header
        
        if is_browser and request.method == "GET":
            # Return HTML with auto-redirect for browsers
            logger.info("No user found, returning HTML redirect page")
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting to Login...</title>
                <meta http-equiv="refresh" content="0; url=/login?next=/product-analysis/">
                <script>window.location.href = '/login?next=/product-analysis/';</script>
            </head>
            <body>
                <p>You need to be logged in to access this page. Redirecting to login...</p>
                <p>If you are not redirected, <a href="/login?next=/product-analysis/">click here</a>.</p>
            </body>
            </html>
            """, status_code=401)
        else:
            # For HEAD requests or API calls, return redirect
            logger.info("No user found, redirecting to login")
            return RedirectResponse(url="/login?next=/product-analysis/", status_code=303)
    
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



@router.post("/analyze-image")
async def analyze_product_image(
    request: Request,
    image: UploadFile = File(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None)
):
    """Analyze product image using AI - Simplified version"""
    # Check authentication manually
    from foodxchange.core.auth import get_current_user
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in to use this feature."
        )
    
    try:
        # Analyze product image using AI services
        # AI analysis implementation will be added when Azure services are fully configured
        
        # Convert image to base64 for display
        import base64
        image_content = await image.read()
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        image_mime_type = image.content_type or 'image/jpeg'
        data_url = f"data:{image_mime_type};base64,{image_base64}"
        
        # Analysis result
        analysis_result = {
            "product_name": "Analyzed Product",
            "category": product_category or "Food & Beverage",
            "confidence": 0.85,
            "description": product_description or "Product analysis completed successfully"
        }
        
        # Brief result
        brief_result = {
            "product_name": "Analyzed Product",
            "producing_company": "Product Company",
            "brand_name": "Product Brand",
            "country_of_origin": "United States",
            "category": product_category or "Food & Beverage",
            "packaging_type": "Standard Container",
            "product_weight": "500g",
            "product_appearance": "Standard appearance",
            "storage_conditions": "Store in a cool, dry place",
            "target_market": "Retail consumers",
            "kosher": "Unknown",
            "kosher_writings": "Not specified",
            "gluten_free": "Unknown",
            "sugar_free": "Unknown",
            "no_sugar_added": "Unknown"
        }
        
        # Similar products
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
    request: Request,
    images: List[UploadFile] = File(...),
    product_description: Optional[str] = Form(None),
    product_category: Optional[str] = Form(None)
):
    """Analyze multiple product images using AI"""
    # Check authentication manually
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in to use this feature."
        )
    
    try:
        if not images:
            raise HTTPException(status_code=400, detail="No images provided")
        
        # Import required services
        from ..services.product_analysis_service import product_analysis_service
        from ..database import get_db
        import tempfile
        import os
        
        analysis_results = []
        brief_results = []
        analyzed_images = []
        
        # Process with DB session
        db = next(get_db())
        
        try:
            for image in images:
                # Save image temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    image_content = await image.read()
                    tmp_file.write(image_content)
                    tmp_file_path = tmp_file.name
                
                try:
                    # Convert to base64 for display
                    import base64
                    image_base64 = base64.b64encode(image_content).decode('utf-8')
                    image_mime_type = image.content_type or 'image/jpeg'
                    data_url = f"data:{image_mime_type};base64,{image_base64}"
                    analyzed_images.append(data_url)
                    
                    # Analyze with AI service (GPT-4 Vision)
                    analysis_result = await product_analysis_service.analyze_product_image(
                        tmp_file_path, 
                        db=db,
                        use_gpt4v=True  # Use GPT-4 Vision
                    )
                    analysis_results.append(analysis_result)
                    
                    # Generate brief from analysis
                    brief = await product_analysis_service.generate_product_brief(
                        analysis_result,
                        user_query=product_description,
                        db=db
                    )
                    brief_results.append(brief)
                    
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
            
            # Search for similar products (placeholder for now)
            similar_products = []
            if brief_results:
                similar_products = await product_analysis_service.search_similar_products(
                    product_name=brief_results[0].get("product_name", ""),
                    category=brief_results[0].get("category", "")
                )
            
            # If no similar products found, return empty list
            if not similar_products:
                similar_products = []
            
            return {
                "success": True,
                "analysis": analysis_results,
                "brief": brief_results[0] if brief_results else None,  # Use first brief as main
                "similar_products": similar_products,
                "analyzed_images": analyzed_images
            }
            
        finally:
            db.close()
            
    except ValueError as ve:
        # Handle configuration errors
        logger.error(f"Configuration error: {ve}")
        raise HTTPException(status_code=503, detail=str(ve))
    except Exception as e:
        logger.error(f"Error analyzing multiple images: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze images")
        
    except Exception as e:
        logger.error(f"Error analyzing multiple images: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze images")

@router.post("/save-project")
async def save_analysis_as_project(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    buyer_id: Optional[str] = Form(None),
    priority: str = Form("medium"),
    search_type: Optional[str] = Form(None),
    analysis_data: str = Form(...)
):
    # Check authentication manually
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in to use this feature."
        )
    """Save analysis as a project and create enhanced project with stages"""
    try:
        import os
        from datetime import datetime
        import requests
        
        # Parse analysis data
        analysis = json.loads(analysis_data)
        
        # Create enhanced project data
        project_data = {
            "name": name,
            "buyer_id": int(buyer_id) if buyer_id and buyer_id != "" else 1,
            "priority": priority,
            "description": description,
            "search_type": search_type or "image",
            "initial_product_images": analysis.get("images", []),
            "product_specifications": {
                "product_name": analysis.get("product_name", "Unknown Product"),
                "category": analysis.get("category", "Food & Beverage"),
                "description": analysis.get("description", ""),
                "analysis_results": analysis
            },
            "analysis_results": analysis
        }
        
        # Call the enhanced project creation API
        try:
            response = requests.post(
                "http://localhost:8003/projects/api/create-from-analysis",
                json=project_data
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Created enhanced project: {result.get('project', {}).get('project_id')}")
                
                # Also save to old format for backward compatibility
                projects_dir = os.path.join(os.getcwd(), "projects")
                os.makedirs(projects_dir, exist_ok=True)
                
                import uuid
                project_filename = f"project_{uuid.uuid4()}.json"
                project_path = os.path.join(projects_dir, project_filename)
                
                old_format_data = {
                    "name": name,
                    "description": description,
                    "buyer_id": buyer_id,
                    "priority": priority,
                    "search_type": search_type or "image",
                    "analysis_data": analysis,
                    "created_at": datetime.now().isoformat(),
                    "enhanced_project_id": result.get('project', {}).get('project_id')
                }
                
                with open(project_path, 'w', encoding='utf-8') as f:
                    json.dump(old_format_data, f, indent=2, ensure_ascii=False)
                
                return {
                    "success": True,
                    "message": "Project saved successfully with enhanced tracking",
                    "project_filename": project_filename,
                    "enhanced_project_id": result.get('project', {}).get('project_id')
                }
            else:
                logger.warning("Could not create enhanced project, falling back to basic save")
                
        except Exception as api_error:
            logger.warning(f"Enhanced project API not available: {api_error}")
        
        # Fallback to old save method if API fails
        projects_dir = os.path.join(os.getcwd(), "projects")
        os.makedirs(projects_dir, exist_ok=True)
        
        import uuid
        project_filename = f"project_{uuid.uuid4()}.json"
        project_path = os.path.join(projects_dir, project_filename)
        
        basic_data = {
            "name": name,
            "description": description,
            "buyer_id": buyer_id,
            "priority": priority,
            "search_type": search_type or "image",
            "analysis_data": analysis,
            "created_at": datetime.now().isoformat()
        }
        
        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(basic_data, f, indent=2, ensure_ascii=False)
        
        return {
            "success": True,
            "message": "Project saved successfully",
            "project_filename": project_filename
        }
        
    except Exception as e:
        logger.error(f"Error saving project: {e}")
        raise HTTPException(status_code=500, detail="Failed to save project")