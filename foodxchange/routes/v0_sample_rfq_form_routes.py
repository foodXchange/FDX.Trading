from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import json

router = APIRouter()
templates = Jinja2Templates(directory="foodxchange/templates")

@router.get("/sample-rfq-form", response_class=HTMLResponse)
async def sample_rfq_form_page(request: Request):
    """Render the sample RFQ form page"""
    return templates.TemplateResponse(
        "v0-components/sample-rfq-form.html",
        {"request": request, "title": "Create RFQ"}
    )

@router.post("/api/rfq/create")
async def create_rfq(
    category: str = Form(...),
    quantity: int = Form(...),
    unit: str = Form(...),
    deliveryDate: str = Form(...),
    budget: int = Form(...),
    requirements: Optional[str] = Form(None)
):
    """API endpoint for creating RFQs"""
    try:
        # Validate input
        if not category or category not in ['grains', 'dairy', 'meat', 'produce', 'seafood', 'beverages', 'snacks']:
            raise HTTPException(status_code=400, detail="Invalid product category")
        
        if quantity < 1:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        if budget < 100:
            raise HTTPException(status_code=400, detail="Budget must be at least $100")
        
        # Here you would typically save to database
        # For demo purposes, we'll just return success
        
        rfq_data = {
            "id": f"RFQ-{hash(f'{category}{quantity}{deliveryDate}') % 10000:04d}",
            "category": category,
            "quantity": quantity,
            "unit": unit,
            "delivery_date": deliveryDate,
            "budget": budget,
            "requirements": requirements,
            "status": "pending",
            "created_at": "2025-07-27T10:30:00Z"
        }
        
        # Log the RFQ creation (in production, save to database)
        print(f"RFQ Created: {json.dumps(rfq_data, indent=2)}")
        
        return {
            "status": "success",
            "message": "RFQ created successfully",
            "rfq_id": rfq_data["id"],
            "data": rfq_data
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        print(f"Error creating RFQ: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create RFQ")

@router.get("/api/rfq/categories")
async def get_rfq_categories():
    """Get available product categories"""
    return {
        "categories": [
            {"value": "grains", "label": "Grains & Cereals"},
            {"value": "dairy", "label": "Dairy Products"},
            {"value": "meat", "label": "Meat & Poultry"},
            {"value": "produce", "label": "Fresh Produce"},
            {"value": "seafood", "label": "Seafood"},
            {"value": "beverages", "label": "Beverages"},
            {"value": "snacks", "label": "Snacks & Confectionery"}
        ]
    }

@router.get("/api/rfq/units")
async def get_rfq_units():
    """Get available units"""
    return {
        "units": [
            {"value": "kg", "label": "Kilograms (kg)"},
            {"value": "lbs", "label": "Pounds (lbs)"},
            {"value": "cases", "label": "Cases"},
            {"value": "pallets", "label": "Pallets"},
            {"value": "units", "label": "Units"}
        ]
    } 