"""
Buyers Routes for FoodXchange
Manage buyer profiles and relationships
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from sqlalchemy.orm import Session
from pathlib import Path
import logging
from datetime import datetime

from ..database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/buyers", tags=["Buyers"])

# Configure templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/", response_class=HTMLResponse)
async def buyers_page(request: Request):
    """Buyers management page"""
    return templates.TemplateResponse("pages/buyers.html", {"request": request})

@router.get("/list")
async def list_buyers(db: Session = Depends(get_db)):
    """Get list of all buyers"""
    try:
        # Query buyers from database
        # TODO: Implement actual database query when models are ready
        buyers = []
        
        return {
            "success": True,
            "buyers": buyers,
            "total": len(buyers)
        }
    except Exception as e:
        logger.error(f"Error fetching buyers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch buyers")

@router.post("/add")
async def add_buyer(
    name: str = Form(...),
    company_name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Add a new buyer"""
    try:
        # In production, this would save to database
        import uuid
        buyer_id = str(uuid.uuid4())
        
        buyer_data = {
            "id": buyer_id,
            "name": name,
            "company_name": company_name,
            "email": email,
            "phone": phone,
            "location": location,
            "notes": notes,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "message": "Buyer added successfully",
            "buyer": buyer_data
        }
    except Exception as e:
        logger.error(f"Error adding buyer: {e}")
        raise HTTPException(status_code=500, detail="Failed to add buyer")

@router.get("/{buyer_id}")
async def get_buyer(buyer_id: str, db: Session = Depends(get_db)):
    """Get buyer details"""
    try:
        # Query buyer from database
        # TODO: Implement actual database query when models are ready
        buyer = None
        
        if not buyer:
            raise HTTPException(status_code=404, detail="Buyer not found")
        
        return {
            "success": True,
            "buyer": buyer
        }
    except Exception as e:
        logger.error(f"Error fetching buyer: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch buyer details")

@router.put("/{buyer_id}")
async def update_buyer(
    buyer_id: str,
    name: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Update buyer information"""
    try:
        # In production, this would update database
        return {
            "success": True,
            "message": "Buyer updated successfully",
            "buyer_id": buyer_id
        }
    except Exception as e:
        logger.error(f"Error updating buyer: {e}")
        raise HTTPException(status_code=500, detail="Failed to update buyer")

@router.delete("/{buyer_id}")
async def delete_buyer(buyer_id: str, db: Session = Depends(get_db)):
    """Delete a buyer"""
    try:
        # In production, this would delete from database
        return {
            "success": True,
            "message": "Buyer deleted successfully"
        }
    except Exception as e:
        logger.error(f"Error deleting buyer: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete buyer")