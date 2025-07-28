"""
Supplier API routes for RFQ viewing and quote submission
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query, Form, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func, case
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import json

from foodxchange.database import get_db
from foodxchange.auth import get_current_user
from foodxchange.models.user import User
from foodxchange.models.rfq import RFQ
from foodxchange.models.quote import Quote
from foodxchange.models.supplier import Supplier
from foodxchange.models.company import Company
from foodxchange.models.product import Product
from foodxchange.models.notification import Notification
from foodxchange.services.simple_notification_service import NotificationService
from foodxchange.services.email_service import EmailService

router = APIRouter(prefix="/api/supplier", tags=["supplier-api"])


@router.get("/rfqs/available")
async def get_available_rfqs(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_budget: Optional[float] = Query(None),
    max_budget: Optional[float] = Query(None),
    delivery_days: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at|delivery_date|budget_max)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available RFQs that supplier can bid on"""
    # Verify user is a supplier
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=403, detail="Supplier profile not found")
    
    # Base query for open RFQs
    query = db.query(RFQ).options(
        joinedload(RFQ.company),
        joinedload(RFQ.quotes)
    ).filter(
        RFQ.status.in_(["sent", "quoted"]),
        RFQ.deadline >= date.today()  # Not expired
    )
    
    # Exclude RFQs where supplier already quoted
    quoted_rfq_ids = db.query(Quote.rfq_id).filter(
        Quote.supplier_id == supplier.id
    ).subquery()
    query = query.filter(~RFQ.id.in_(quoted_rfq_ids))
    
    # Apply filters
    if category:
        query = query.filter(RFQ.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                RFQ.product_name.ilike(search_term),
                RFQ.requirements.ilike(search_term),
                RFQ.delivery_location.ilike(search_term)
            )
        )
    
    if min_budget is not None:
        query = query.filter(
            or_(
                RFQ.budget_max >= min_budget,
                RFQ.budget_max.is_(None)  # Include open budget RFQs
            )
        )
    
    if max_budget is not None:
        query = query.filter(
            or_(
                RFQ.budget_min <= max_budget,
                RFQ.budget_min.is_(None)
            )
        )
    
    if delivery_days is not None:
        min_delivery_date = date.today() + timedelta(days=delivery_days)
        query = query.filter(RFQ.delivery_date >= min_delivery_date)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply sorting
    if sort_by == "delivery_date":
        query = query.order_by(RFQ.delivery_date.asc())
    elif sort_by == "budget_max":
        query = query.order_by(RFQ.budget_max.desc().nullslast())
    else:
        query = query.order_by(RFQ.created_at.desc())
    
    # Apply pagination
    offset = (page - 1) * limit
    rfqs = query.offset(offset).limit(limit).all()
    
    # Format response
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
                "budget_range": _format_budget_range(rfq),
                "requirements": rfq.requirements,
                "days_until_deadline": (rfq.deadline - date.today()).days if rfq.deadline else None,
                "days_until_delivery": (rfq.delivery_date - date.today()).days if rfq.delivery_date else None,
                "quote_count": len(rfq.quotes),
                "buyer_company": rfq.company.name if rfq.company else "Private Buyer",
                "created_at": rfq.created_at.isoformat(),
                "is_urgent": _is_urgent_rfq(rfq)
            }
            for rfq in rfqs
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": (total_count + limit - 1) // limit
        },
        "filters_applied": {
            "category": category,
            "search": search,
            "min_budget": min_budget,
            "max_budget": max_budget,
            "delivery_days": delivery_days
        }
    }


@router.get("/rfqs/{rfq_id}")
async def get_rfq_details(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed RFQ information for quote submission"""
    # Verify supplier access
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=403, detail="Supplier profile not found")
    
    # Get RFQ with related data
    rfq = db.query(RFQ).options(
        joinedload(RFQ.company),
        joinedload(RFQ.quotes),
        joinedload(RFQ.user)
    ).filter(RFQ.id == rfq_id).first()
    
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    # Check if supplier already quoted
    existing_quote = db.query(Quote).filter(
        Quote.rfq_id == rfq_id,
        Quote.supplier_id == supplier.id
    ).first()
    
    # Get competitor quote count (not details)
    competitor_quotes = db.query(Quote).filter(
        Quote.rfq_id == rfq_id,
        Quote.supplier_id != supplier.id,
        Quote.status != "draft"
    ).count()
    
    return {
        "rfq": {
            "id": rfq.id,
            "rfq_number": rfq.rfq_number,
            "product_name": rfq.product_name,
            "category": rfq.category,
            "quantity": rfq.quantity,
            "delivery_date": rfq.delivery_date.isoformat() if rfq.delivery_date else None,
            "delivery_location": rfq.delivery_location,
            "budget_range": _format_budget_range(rfq),
            "requirements": rfq.requirements,
            "status": rfq.status,
            "deadline": rfq.deadline.isoformat() if rfq.deadline else None,
            "days_until_deadline": (rfq.deadline - date.today()).days if rfq.deadline else None,
            "created_at": rfq.created_at.isoformat()
        },
        "buyer": {
            "company_name": rfq.company.name if rfq.company else "Private Buyer",
            "location": rfq.company.city if rfq.company else None,
            "is_verified": rfq.company.is_verified if rfq.company else False
        },
        "competition": {
            "total_quotes": competitor_quotes,
            "has_quoted": existing_quote is not None,
            "quote_id": existing_quote.id if existing_quote else None,
            "quote_status": existing_quote.status if existing_quote else None
        },
        "can_quote": rfq.status in ["sent", "quoted"] and not existing_quote and rfq.deadline >= date.today()
    }


@router.post("/quotes/submit")
async def submit_quote(
    rfq_id: int = Form(...),
    price_per_unit: float = Form(...),
    total_price: float = Form(...),
    currency: str = Form("USD"),
    delivery_time: str = Form(...),
    payment_terms: str = Form(...),
    notes: Optional[str] = Form(None),
    minimum_order_quantity: Optional[float] = Form(None),
    validity_days: int = Form(30),
    attachments: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit a quote for an RFQ"""
    # Verify supplier access
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=403, detail="Supplier profile not found")
    
    # Verify RFQ exists and is open
    rfq = db.query(RFQ).filter(RFQ.id == rfq_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    if rfq.status not in ["sent", "quoted"]:
        raise HTTPException(status_code=400, detail="RFQ is not open for quotes")
    
    if rfq.deadline and rfq.deadline < date.today():
        raise HTTPException(status_code=400, detail="RFQ deadline has passed")
    
    # Check if already quoted
    existing_quote = db.query(Quote).filter(
        Quote.rfq_id == rfq_id,
        Quote.supplier_id == supplier.id
    ).first()
    
    if existing_quote:
        raise HTTPException(status_code=400, detail="You have already submitted a quote for this RFQ")
    
    # Create quote
    quote = Quote(
        rfq_id=rfq_id,
        supplier_id=supplier.id,
        price_per_unit=price_per_unit,
        total_price=total_price,
        currency=currency,
        delivery_time=delivery_time,
        payment_terms=payment_terms,
        notes=notes,
        status="submitted",
        unit_price=price_per_unit  # Duplicate for backward compatibility
    )
    
    db.add(quote)
    
    # Update RFQ status if first quote
    if rfq.status == "sent":
        rfq.status = "quoted"
    
    # Create notification for buyer
    notification_service = NotificationService(db)
    notification_service.create_notification(
        user_id=rfq.user_id,
        title="New Quote Received",
        message=f"You have received a new quote for RFQ {rfq.rfq_number} from {supplier.name}",
        type="quote",
        entity_type="quote",
        entity_id=quote.id
    )
    
    # Send email notification
    try:
        email_service = EmailService()
        if rfq.user and rfq.user.email:
            await email_service.send_quote_notification(
                buyer_email=rfq.user.email,
                rfq_number=rfq.rfq_number,
                supplier_name=supplier.name,
                quote_amount=total_price
            )
    except Exception as e:
        # Log but don't fail the quote submission
        print(f"Failed to send email notification: {str(e)}")
    
    db.commit()
    db.refresh(quote)
    
    return {
        "success": True,
        "quote_id": quote.id,
        "message": "Quote submitted successfully",
        "quote": {
            "id": quote.id,
            "rfq_number": rfq.rfq_number,
            "total_price": float(quote.total_price),
            "delivery_time": quote.delivery_time,
            "status": quote.status
        }
    }


@router.get("/quotes")
async def get_supplier_quotes(
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all quotes submitted by the supplier"""
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=403, detail="Supplier profile not found")
    
    # Base query
    query = db.query(Quote).options(
        joinedload(Quote.rfq),
        joinedload(Quote.supplier)
    ).filter(Quote.supplier_id == supplier.id)
    
    # Apply filters
    if status:
        query = query.filter(Quote.status == status)
    
    if date_from:
        query = query.filter(Quote.created_at >= date_from)
    
    if date_to:
        query = query.filter(Quote.created_at <= date_to + timedelta(days=1))
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * limit
    quotes = query.order_by(Quote.created_at.desc()).offset(offset).limit(limit).all()
    
    # Calculate statistics
    total_value = db.query(func.sum(Quote.total_price)).filter(
        Quote.supplier_id == supplier.id
    ).scalar() or 0
    
    won_quotes = db.query(Quote).filter(
        Quote.supplier_id == supplier.id,
        Quote.status == "accepted"
    ).count()
    
    return {
        "items": [
            {
                "id": quote.id,
                "rfq_number": quote.rfq.rfq_number,
                "product_name": quote.rfq.product_name,
                "quantity": quote.rfq.quantity,
                "price_per_unit": float(quote.price_per_unit) if quote.price_per_unit else None,
                "total_price": float(quote.total_price) if quote.total_price else None,
                "delivery_time": quote.delivery_time,
                "status": quote.status,
                "created_at": quote.created_at.isoformat(),
                "buyer_company": quote.rfq.company.name if quote.rfq.company else "Private Buyer"
            }
            for quote in quotes
        ],
        "pagination": {
            "page": page,
            "limit": limit,
            "total_count": total_count,
            "total_pages": (total_count + limit - 1) // limit
        },
        "statistics": {
            "total_quotes": total_count,
            "won_quotes": won_quotes,
            "win_rate": (won_quotes / total_count * 100) if total_count > 0 else 0,
            "total_quoted_value": float(total_value),
            "pending_quotes": db.query(Quote).filter(
                Quote.supplier_id == supplier.id,
                Quote.status == "pending"
            ).count()
        }
    }


@router.put("/quotes/{quote_id}")
async def update_quote(
    quote_id: int,
    price_per_unit: Optional[float] = Form(None),
    total_price: Optional[float] = Form(None),
    delivery_time: Optional[str] = Form(None),
    payment_terms: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a quote (only if still pending)"""
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=403, detail="Supplier profile not found")
    
    # Get quote
    quote = db.query(Quote).filter(
        Quote.id == quote_id,
        Quote.supplier_id == supplier.id
    ).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    if quote.status != "pending":
        raise HTTPException(status_code=400, detail="Can only update pending quotes")
    
    # Update fields
    if price_per_unit is not None:
        quote.price_per_unit = price_per_unit
        quote.unit_price = price_per_unit
    
    if total_price is not None:
        quote.total_price = total_price
    
    if delivery_time is not None:
        quote.delivery_time = delivery_time
    
    if payment_terms is not None:
        quote.payment_terms = payment_terms
    
    if notes is not None:
        quote.notes = notes
    
    quote.status = "submitted"  # Mark as submitted after update
    
    # Notify buyer of update
    notification_service = NotificationService(db)
    notification_service.create_notification(
        user_id=quote.rfq.user_id,
        title="Quote Updated",
        message=f"Supplier {supplier.name} has updated their quote for RFQ {quote.rfq.rfq_number}",
        type="quote",
        entity_type="quote",
        entity_id=quote.id
    )
    
    db.commit()
    
    return {
        "success": True,
        "message": "Quote updated successfully",
        "quote_id": quote.id
    }


@router.get("/dashboard/stats")
async def get_supplier_dashboard_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get supplier dashboard statistics"""
    if not current_user.company_id:
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    supplier = db.query(Supplier).filter(Supplier.company_id == current_user.company_id).first()
    if not supplier:
        raise HTTPException(status_code=403, detail="Supplier profile not found")
    
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Get quote statistics
    total_quotes = db.query(Quote).filter(
        Quote.supplier_id == supplier.id,
        Quote.created_at >= from_date
    ).count()
    
    won_quotes = db.query(Quote).filter(
        Quote.supplier_id == supplier.id,
        Quote.status == "accepted",
        Quote.created_at >= from_date
    ).count()
    
    # Get RFQ opportunities
    available_rfqs = db.query(RFQ).filter(
        RFQ.status.in_(["sent", "quoted"]),
        RFQ.deadline >= date.today()
    ).count()
    
    # Get revenue statistics
    revenue_query = db.query(func.sum(Quote.total_price)).filter(
        Quote.supplier_id == supplier.id,
        Quote.status == "accepted",
        Quote.created_at >= from_date
    ).scalar() or 0
    
    # Average response time (placeholder - would need actual tracking)
    avg_response_time = 24  # hours
    
    # Recent activity
    recent_quotes = db.query(Quote).filter(
        Quote.supplier_id == supplier.id
    ).order_by(Quote.created_at.desc()).limit(5).all()
    
    # Top categories
    category_stats = db.query(
        RFQ.category,
        func.count(Quote.id).label('quote_count'),
        func.sum(case((Quote.status == "accepted", 1), else_=0)).label('won_count')
    ).join(
        Quote, Quote.rfq_id == RFQ.id
    ).filter(
        Quote.supplier_id == supplier.id,
        Quote.created_at >= from_date
    ).group_by(RFQ.category).all()
    
    return {
        "period": {
            "days": days,
            "from_date": from_date.isoformat(),
            "to_date": datetime.utcnow().isoformat()
        },
        "summary": {
            "total_quotes_submitted": total_quotes,
            "quotes_won": won_quotes,
            "win_rate": (won_quotes / total_quotes * 100) if total_quotes > 0 else 0,
            "available_rfqs": available_rfqs,
            "revenue_won": float(revenue_query),
            "avg_response_time_hours": avg_response_time,
            "supplier_rating": float(supplier.rating) if supplier.rating else 0
        },
        "recent_activity": [
            {
                "id": quote.id,
                "rfq_number": quote.rfq.rfq_number,
                "product": quote.rfq.product_name,
                "amount": float(quote.total_price) if quote.total_price else 0,
                "status": quote.status,
                "date": quote.created_at.isoformat()
            }
            for quote in recent_quotes
        ],
        "top_categories": [
            {
                "category": cat[0] or "Uncategorized",
                "total_quotes": cat[1],
                "won_quotes": cat[2],
                "win_rate": (cat[2] / cat[1] * 100) if cat[1] > 0 else 0
            }
            for cat in category_stats[:5]
        ]
    }


# Helper functions

def _format_budget_range(rfq: RFQ) -> str:
    """Format budget range for display"""
    if rfq.budget_min and rfq.budget_max:
        return f"${rfq.budget_min:,.0f} - ${rfq.budget_max:,.0f}"
    elif rfq.budget_min:
        return f"Min ${rfq.budget_min:,.0f}"
    elif rfq.budget_max:
        return f"Max ${rfq.budget_max:,.0f}"
    else:
        return "Open Budget"


def _is_urgent_rfq(rfq: RFQ) -> bool:
    """Check if RFQ should be marked as urgent"""
    if not rfq.deadline:
        return False
    
    days_until_deadline = (rfq.deadline - date.today()).days
    days_until_delivery = (rfq.delivery_date - date.today()).days if rfq.delivery_date else 999
    
    return days_until_deadline <= 2 or days_until_delivery <= 7


def include_supplier_api_routes(app):
    """Include supplier API routes in the main app"""
    app.include_router(router)