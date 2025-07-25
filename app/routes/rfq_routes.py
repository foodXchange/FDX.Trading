"""
RFQ (Request for Quotation) routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import random
import string

from app.database import get_db
from app.auth import get_current_user, get_current_user_context
from app.models.user import User
from app.models.rfq import RFQ
from app.models.supplier import Supplier
from app.models.quote import Quote

router = APIRouter(prefix="/api/rfqs", tags=["rfqs"])
templates = Jinja2Templates(directory="app/templates")


def generate_rfq_number() -> str:
    """Generate unique RFQ number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"RFQ-{timestamp}-{random_suffix}"


@router.get("/", response_model=List[dict])
async def get_rfqs(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all RFQs for the current user"""
    query = db.query(RFQ).filter(RFQ.user_id == current_user.id)
    
    if status:
        query = query.filter(RFQ.status == status)
    
    rfqs = query.order_by(RFQ.created_at.desc()).all()
    
    return [
        {
            "id": rfq.id,
            "rfq_number": rfq.rfq_number,
            "product_name": rfq.product_name,
            "category": rfq.category,
            "quantity": rfq.quantity,
            "delivery_date": rfq.delivery_date.isoformat() if rfq.delivery_date else None,
            "status": rfq.status,
            "quotes_count": len(rfq.quotes),
            "created_at": rfq.created_at.isoformat()
        }
        for rfq in rfqs
    ]


@router.post("/")
async def create_rfq(
    product_name: str = Form(...),
    category: str = Form(None),
    quantity: str = Form(...),
    delivery_date: str = Form(...),
    delivery_location: str = Form(None),
    budget_min: Optional[float] = Form(None),
    budget_max: Optional[float] = Form(None),
    requirements: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new RFQ"""
    rfq = RFQ(
        rfq_number=generate_rfq_number(),
        user_id=current_user.id,
        product_name=product_name,
        category=category,
        quantity=quantity,
        delivery_date=datetime.strptime(delivery_date, "%Y-%m-%d").date(),
        delivery_location=delivery_location,
        budget_min=budget_min,
        budget_max=budget_max,
        requirements=requirements,
        status="draft"
    )
    
    db.add(rfq)
    db.commit()
    db.refresh(rfq)
    
    return {
        "id": rfq.id,
        "rfq_number": rfq.rfq_number,
        "message": "RFQ created successfully"
    }


@router.get("/{rfq_id}")
async def get_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific RFQ with quotes"""
    rfq = db.query(RFQ).filter(
        RFQ.id == rfq_id,
        RFQ.user_id == current_user.id
    ).first()
    
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    return {
        "id": rfq.id,
        "rfq_number": rfq.rfq_number,
        "product_name": rfq.product_name,
        "category": rfq.category,
        "quantity": rfq.quantity,
        "delivery_date": rfq.delivery_date.isoformat() if rfq.delivery_date else None,
        "delivery_location": rfq.delivery_location,
        "budget_min": float(rfq.budget_min) if rfq.budget_min else None,
        "budget_max": float(rfq.budget_max) if rfq.budget_max else None,
        "requirements": rfq.requirements,
        "status": rfq.status,
        "created_at": rfq.created_at.isoformat(),
        "quotes": [
            {
                "id": quote.id,
                "supplier_name": quote.supplier.name if quote.supplier else "Unknown",
                "price_per_unit": float(quote.price_per_unit) if quote.price_per_unit else None,
                "total_price": float(quote.total_price) if quote.total_price else None,
                "currency": quote.currency,
                "delivery_time": quote.delivery_time,
                "payment_terms": quote.payment_terms,
                "status": quote.status,
                "created_at": quote.created_at.isoformat()
            }
            for quote in rfq.quotes
        ]
    }


@router.post("/{rfq_id}/send")
async def send_rfq(
    rfq_id: int,
    supplier_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send RFQ to selected suppliers"""
    rfq = db.query(RFQ).filter(
        RFQ.id == rfq_id,
        RFQ.user_id == current_user.id
    ).first()
    
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    # Update RFQ status
    rfq.status = "sent"
    
    # Create quote records for each supplier
    quotes_created = 0
    for supplier_id in supplier_ids:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if supplier:
            quote = Quote(
                rfq_id=rfq.id,
                supplier_id=supplier_id,
                status="pending"
            )
            db.add(quote)
            quotes_created += 1
    
    db.commit()
    
    return {
        "message": f"RFQ sent to {quotes_created} suppliers",
        "rfq_id": rfq.id,
        "quotes_created": quotes_created
    }


@router.put("/{rfq_id}/status")
async def update_rfq_status(
    rfq_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update RFQ status"""
    valid_statuses = ["draft", "sent", "quoted", "closed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    rfq = db.query(RFQ).filter(
        RFQ.id == rfq_id,
        RFQ.user_id == current_user.id
    ).first()
    
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    rfq.status = status
    db.commit()
    
    return {"message": f"RFQ status updated to {status}"}


@router.delete("/{rfq_id}")
async def delete_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an RFQ (only if in draft status)"""
    rfq = db.query(RFQ).filter(
        RFQ.id == rfq_id,
        RFQ.user_id == current_user.id
    ).first()
    
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    if rfq.status != "draft":
        raise HTTPException(status_code=400, detail="Can only delete draft RFQs")
    
    db.delete(rfq)
    db.commit()
    
    return {"message": "RFQ deleted successfully"}


def include_rfq_routes(app):
    """Include RFQ routes in the main app"""
    app.include_router(router)
    
    # Template routes
    @app.get("/rfqs", response_class=HTMLResponse, name="rfqs_list")
    async def rfqs_list(request: Request, db: Session = Depends(get_db)):
        user = get_current_user_context(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Get RFQs from database
        user_obj = db.query(User).filter(User.id == user["id"]).first()
        rfqs = db.query(RFQ).filter(RFQ.user_id == user_obj.id).order_by(RFQ.created_at.desc()).all()
        
        return templates.TemplateResponse("rfqs.html", {
            "request": request,
            "current_user": user,
            "rfqs": rfqs
        })