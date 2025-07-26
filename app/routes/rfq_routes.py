"""
RFQ (Request for Quotation) routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import random
import string
import json

from app.database import get_db
from app.auth import get_current_user, get_current_user_context
from app.models.user import User
from app.models.rfq import RFQ
from app.models.supplier import Supplier
from app.models.quote import Quote
from app.models.company import Company
from app.models.notification import Notification
from app.services.simple_notification_service import NotificationService
from app.services.email_service import EmailService

router = APIRouter(prefix="/api/rfqs", tags=["rfqs"])
templates = Jinja2Templates(directory="app/templates")


def generate_rfq_number() -> str:
    """Generate unique RFQ number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"RFQ-{timestamp}-{random_suffix}"


async def send_rfq_to_suppliers(rfq_id: int, supplier_ids: List[int], db: Session, current_user: User) -> int:
    """Helper function to send RFQ to multiple suppliers"""
    quotes_created = 0
    notification_service = NotificationService(db)
    email_service = EmailService()
    
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()
    if not rfq:
        raise ValueError("RFQ not found")
    
    for supplier_id in supplier_ids:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if supplier:
            # Create quote record
            quote = Quote(
                rfq_id=rfq.id,
                supplier_id=supplier_id,
                status="pending"
            )
            db.add(quote)
            quotes_created += 1
            
            # Create notification for supplier
            if supplier.company_id:
                # Get supplier users
                supplier_users = db.query(User).filter(User.company_id == supplier.company_id).all()
                for user in supplier_users:
                    notification_service.create_notification(
                        user_id=user.id,
                        title="New RFQ Received",
                        message=f"You have received a new RFQ {rfq.rfq_number} for {rfq.product_name}",
                        type="rfq",
                        entity_type="rfq",
                        entity_id=rfq.id
                    )
            
            # Send email notification
            if supplier.email:
                try:
                    await email_service.send_rfq_notification(
                        supplier_email=supplier.email,
                        rfq_number=rfq.rfq_number,
                        product_name=rfq.product_name,
                        quantity=rfq.quantity,
                        delivery_date=rfq.delivery_date
                    )
                except Exception as e:
                    # Log error but continue processing
                    print(f"Failed to send email to {supplier.email}: {str(e)}")
    
    db.commit()
    return quotes_created


@router.get("/", response_model=List[dict])
async def get_rfqs(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all RFQs with advanced filtering and pagination"""
    # Base query with eager loading
    query = db.query(RFQ).options(
        joinedload(RFQ.quotes),
        joinedload(RFQ.company),
        joinedload(RFQ.user)
    )
    
    # Filter by user or company
    if current_user.company_id:
        query = query.filter(RFQ.company_id == current_user.company_id)
    else:
        query = query.filter(RFQ.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(RFQ.status == status)
    
    if category:
        query = query.filter(RFQ.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                RFQ.product_name.ilike(search_term),
                RFQ.requirements.ilike(search_term),
                RFQ.rfq_number.ilike(search_term)
            )
        )
    
    if date_from:
        query = query.filter(RFQ.created_at >= date_from)
    
    if date_to:
        query = query.filter(RFQ.created_at <= date_to + timedelta(days=1))
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    rfqs = query.order_by(RFQ.created_at.desc()).offset(offset).limit(limit).all()
    
    # Calculate metrics
    active_quotes = sum(1 for rfq in rfqs for quote in rfq.quotes if quote.status == "submitted")
    
    return {
        "items": [
            {
                "id": rfq.id,
                "rfq_number": rfq.rfq_number,
                "product_name": rfq.product_name,
                "category": rfq.category,
                "quantity": rfq.quantity,
                "delivery_date": rfq.delivery_date.isoformat() if rfq.delivery_date else None,
                "delivery_location": rfq.delivery_location,
                "status": rfq.status,
                "budget_range": f"${rfq.budget_min or 0} - ${rfq.budget_max or 'Open'}" if rfq.budget_min or rfq.budget_max else "Not specified",
                "quotes_count": len(rfq.quotes),
                "active_quotes": len([q for q in rfq.quotes if q.status == "submitted"]),
                "created_at": rfq.created_at.isoformat(),
                "days_until_delivery": (rfq.delivery_date - date.today()).days if rfq.delivery_date else None,
                "company_name": rfq.company.name if rfq.company else None
            }
            for rfq in rfqs
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": (total_count + limit - 1) // limit
        },
        "stats": {
            "total_rfqs": total_count,
            "active_quotes": active_quotes,
            "draft_count": db.query(RFQ).filter(RFQ.status == "draft").count(),
            "sent_count": db.query(RFQ).filter(RFQ.status == "sent").count()
        }
    }


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
    preferred_suppliers: Optional[str] = Form(None),  # JSON string of supplier IDs
    auto_send: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new RFQ with enhanced features"""
    try:
        # Create RFQ
        rfq = RFQ(
            rfq_number=generate_rfq_number(),
            user_id=current_user.id,
            company_id=current_user.company_id,
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
        
        # Create notification
        notification_service = NotificationService(db)
        notification_service.create_notification(
            user_id=current_user.id,
            title="RFQ Created",
            message=f"RFQ {rfq.rfq_number} for {product_name} has been created",
            type="rfq",
            entity_type="rfq",
            entity_id=rfq.id
        )
        
        # Auto-send to suppliers if requested
        if auto_send and preferred_suppliers:
            supplier_ids = json.loads(preferred_suppliers) if isinstance(preferred_suppliers, str) else []
            if supplier_ids:
                # Send to suppliers
                await send_rfq_to_suppliers(rfq.id, supplier_ids, db, current_user)
                rfq.status = "sent"
                db.commit()
        
        return {
            "id": rfq.id,
            "rfq_number": rfq.rfq_number,
            "status": rfq.status,
            "message": f"RFQ created successfully{' and sent to suppliers' if auto_send else ''}"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


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


@router.put("/{rfq_id}")
async def update_rfq(
    rfq_id: int,
    product_name: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    quantity: Optional[str] = Form(None),
    delivery_date: Optional[str] = Form(None),
    delivery_location: Optional[str] = Form(None),
    budget_min: Optional[float] = Form(None),
    budget_max: Optional[float] = Form(None),
    requirements: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an RFQ (only if in draft status)"""
    rfq = db.query(RFQ).filter(
        RFQ.id == rfq_id,
        RFQ.user_id == current_user.id
    ).first()
    
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    if rfq.status != "draft":
        raise HTTPException(status_code=400, detail="Can only update draft RFQs")
    
    # Update fields if provided
    if product_name is not None:
        rfq.product_name = product_name
    if category is not None:
        rfq.category = category
    if quantity is not None:
        rfq.quantity = quantity
    if delivery_date is not None:
        rfq.delivery_date = datetime.strptime(delivery_date, "%Y-%m-%d").date()
    if delivery_location is not None:
        rfq.delivery_location = delivery_location
    if budget_min is not None:
        rfq.budget_min = budget_min
    if budget_max is not None:
        rfq.budget_max = budget_max
    if requirements is not None:
        rfq.requirements = requirements
    
    db.commit()
    db.refresh(rfq)
    
    return {
        "id": rfq.id,
        "rfq_number": rfq.rfq_number,
        "message": "RFQ updated successfully"
    }


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


@router.get("/categories")
async def get_rfq_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all available RFQ categories"""
    categories = [
        {"value": "fresh_produce", "label": "Fresh Produce", "icon": "🥬"},
        {"value": "meat_poultry", "label": "Meat & Poultry", "icon": "🍖"},
        {"value": "dairy_eggs", "label": "Dairy & Eggs", "icon": "🥛"},
        {"value": "grains_cereals", "label": "Grains & Cereals", "icon": "🌾"},
        {"value": "beverages", "label": "Beverages", "icon": "🥤"},
        {"value": "snacks_confectionery", "label": "Snacks & Confectionery", "icon": "🍫"},
        {"value": "frozen_foods", "label": "Frozen Foods", "icon": "🧊"},
        {"value": "canned_goods", "label": "Canned Goods", "icon": "🥫"},
        {"value": "condiments_sauces", "label": "Condiments & Sauces", "icon": "🍯"},
        {"value": "bakery", "label": "Bakery Products", "icon": "🍞"}
    ]
    
    return categories


@router.get("/stats")
async def get_rfq_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get RFQ statistics for the dashboard"""
    # Base query
    if current_user.company_id:
        base_query = db.query(RFQ).filter(RFQ.company_id == current_user.company_id)
    else:
        base_query = db.query(RFQ).filter(RFQ.user_id == current_user.id)
    
    # Calculate statistics
    total_rfqs = base_query.count()
    active_rfqs = base_query.filter(RFQ.status.in_(["sent", "quoted"])).count()
    draft_rfqs = base_query.filter(RFQ.status == "draft").count()
    closed_rfqs = base_query.filter(RFQ.status == "closed").count()
    
    # Get recent RFQs
    recent_rfqs = base_query.order_by(RFQ.created_at.desc()).limit(5).all()
    
    # Calculate response rate
    rfqs_with_quotes = base_query.join(Quote).distinct().count()
    response_rate = (rfqs_with_quotes / total_rfqs * 100) if total_rfqs > 0 else 0
    
    return {
        "total_rfqs": total_rfqs,
        "active_rfqs": active_rfqs,
        "draft_rfqs": draft_rfqs,
        "closed_rfqs": closed_rfqs,
        "response_rate": round(response_rate, 1),
        "recent_rfqs": [
            {
                "id": rfq.id,
                "rfq_number": rfq.rfq_number,
                "product_name": rfq.product_name,
                "status": rfq.status,
                "created_at": rfq.created_at.isoformat()
            }
            for rfq in recent_rfqs
        ]
    }


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