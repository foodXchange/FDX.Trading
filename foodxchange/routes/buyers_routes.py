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
from ..models.buyer import Buyer
from foodxchange.core.auth import get_current_user, require_auth

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/buyers", tags=["Buyers"])

# Configure templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/", response_class=HTMLResponse)
@require_auth
async def buyers_page(request: Request):
    """Buyers management page"""
    return templates.TemplateResponse("pages/buyers.html", {"request": request})

@router.get("/list")
async def list_buyers(db: Session = Depends(get_db)):
    """Get list of all buyers"""
    try:
        # Query buyers from database
        if db:
            buyers = db.query(Buyer).all()
            buyer_list = [{
                "id": buyer.id,
                "name": buyer.name,
                "company_name": buyer.company_name,
                "email": buyer.email,
                "phone": buyer.phone,
                "city": buyer.city,
                "country": buyer.country,
                "created_at": buyer.created_at.isoformat() if buyer.created_at else None
            } for buyer in buyers]
        else:
            # Fallback for when database is not available
            buyer_list = []
        
        return {
            "success": True,
            "buyers": buyer_list,
            "total": len(buyer_list)
        }
    except Exception as e:
        logger.error(f"Error fetching buyers: {e}")
        # Return empty list instead of raising exception for better UX
        return {
            "success": False,
            "buyers": [],
            "total": 0,
            "error": "Database connection unavailable"
        }

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
        if db:
            # Parse location into city and country if provided
            city, country = None, None
            if location:
                parts = [p.strip() for p in location.split(',')]
                if len(parts) >= 2:
                    city = parts[0]
                    country = parts[-1]
                else:
                    city = location
            
            # Create new buyer instance
            new_buyer = Buyer(
                name=name,
                company_name=company_name,
                email=email,
                phone=phone,
                city=city,
                country=country,
                description=notes,
                is_active=True
            )
            
            # Add to database
            db.add(new_buyer)
            db.commit()
            db.refresh(new_buyer)
            
            buyer_data = {
                "id": new_buyer.id,
                "name": new_buyer.name,
                "company_name": new_buyer.company_name,
                "email": new_buyer.email,
                "phone": new_buyer.phone,
                "location": f"{city}, {country}" if city and country else location,
                "notes": new_buyer.description,
                "created_at": new_buyer.created_at.isoformat() if new_buyer.created_at else datetime.now().isoformat()
            }
        else:
            # Fallback when database is not available
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
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add buyer")

@router.get("/{buyer_id}")
async def get_buyer(buyer_id: str, db: Session = Depends(get_db)):
    """Get buyer details"""
    try:
        if db:
            # Query buyer from database
            try:
                buyer_id_int = int(buyer_id)
                buyer = db.query(Buyer).filter(Buyer.id == buyer_id_int).first()
            except ValueError:
                # Handle non-integer IDs
                buyer = None
            
            if not buyer:
                raise HTTPException(status_code=404, detail="Buyer not found")
            
            buyer_data = {
                "id": buyer.id,
                "name": buyer.name,
                "company_name": buyer.company_name,
                "email": buyer.email,
                "phone": buyer.phone,
                "city": buyer.city,
                "country": buyer.country,
                "description": buyer.description,
                "is_active": buyer.is_active,
                "created_at": buyer.created_at.isoformat() if buyer.created_at else None,
                "updated_at": buyer.updated_at.isoformat() if buyer.updated_at else None
            }
        else:
            # Fallback when database is not available
            raise HTTPException(status_code=503, detail="Database connection unavailable")
        
        return {
            "success": True,
            "buyer": buyer_data
        }
    except HTTPException:
        raise
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
        if db:
            # Query buyer from database
            try:
                buyer_id_int = int(buyer_id)
                buyer = db.query(Buyer).filter(Buyer.id == buyer_id_int).first()
            except ValueError:
                buyer = None
            
            if not buyer:
                raise HTTPException(status_code=404, detail="Buyer not found")
            
            # Update fields if provided
            if name is not None:
                buyer.name = name
            if company_name is not None:
                buyer.company_name = company_name
            if email is not None:
                buyer.email = email
            if phone is not None:
                buyer.phone = phone
            if location is not None:
                # Parse location into city and country
                parts = [p.strip() for p in location.split(',')]
                if len(parts) >= 2:
                    buyer.city = parts[0]
                    buyer.country = parts[-1]
                else:
                    buyer.city = location
            if notes is not None:
                buyer.description = notes
            
            # Update timestamp
            buyer.updated_at = datetime.now()
            
            # Commit changes
            db.commit()
            
            return {
                "success": True,
                "message": "Buyer updated successfully",
                "buyer_id": buyer.id
            }
        else:
            # Fallback when database is not available
            return {
                "success": True,
                "message": "Buyer updated successfully (simulated)",
                "buyer_id": buyer_id
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating buyer: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update buyer")

@router.delete("/{buyer_id}")
async def delete_buyer(buyer_id: str, db: Session = Depends(get_db)):
    """Delete a buyer"""
    try:
        if db:
            # Query buyer from database
            try:
                buyer_id_int = int(buyer_id)
                buyer = db.query(Buyer).filter(Buyer.id == buyer_id_int).first()
            except ValueError:
                buyer = None
            
            if not buyer:
                raise HTTPException(status_code=404, detail="Buyer not found")
            
            # Delete buyer
            db.delete(buyer)
            db.commit()
            
            return {
                "success": True,
                "message": "Buyer deleted successfully"
            }
        else:
            # Fallback when database is not available
            return {
                "success": True,
                "message": "Buyer deleted successfully (simulated)"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting buyer: {e}")
        if db:
            db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete buyer")