"""
Supplier portal routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from foodxchange.database import get_db
from foodxchange.auth import get_current_user, optional_user
from foodxchange.models.user import User
from foodxchange.models.rfq import RFQ
from foodxchange.models.quote import Quote
from foodxchange.models.supplier import Supplier
from foodxchange.models.company import Company
from foodxchange.schemas.supplier import SupplierResponse, SupplierUpdate
from foodxchange.services.notification_service import NotificationService

router = APIRouter(prefix="/supplier", tags=["supplier"])
templates = Jinja2Templates(directory="foodxchange/templates")
notification_service = NotificationService()


@router.get("/portal", response_class=HTMLResponse)
async def supplier_portal(
    request: Request,
    current_user: User = Depends(optional_user)
):
    """Supplier portal main page"""
    return templates.TemplateResponse(
        "supplier_portal.html",
        {"request": request, "user": current_user}
    )


@router.get("/api/dashboard")
async def get_supplier_dashboard(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get supplier dashboard data"""
    if current_user.role != "supplier":
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    # Get supplier info
    supplier = db.query(Supplier).filter_by(
        company_id=current_user.company_id
    ).first()
    
    if not supplier:
        # Create supplier record if doesn't exist
        company = db.query(Company).filter_by(id=current_user.company_id).first()
        supplier = Supplier(
            company_id=current_user.company_id,
            company_name=company.name if company else current_user.name,
            email=current_user.email,
            status="active",
            is_verified=False
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
    
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Get quotes statistics
    quotes_query = db.query(Quote).filter(
        Quote.supplier_id == supplier.id,
        Quote.created_at >= from_date
    )
    
    quotes = quotes_query.all()
    total_quotes = len(quotes)
    accepted_quotes = len([q for q in quotes if q.status == "accepted"])
    pending_quotes = len([q for q in quotes if q.status == "pending"])
    rejected_quotes = len([q for q in quotes if q.status == "rejected"])
    
    # Calculate win rate
    decided_quotes = accepted_quotes + rejected_quotes
    win_rate = (accepted_quotes / decided_quotes * 100) if decided_quotes > 0 else 0
    
    # Calculate total quoted value
    total_value = sum(float(q.total_price) for q in quotes if q.total_price)
    avg_quote_value = total_value / total_quotes if total_quotes > 0 else 0
    
    # Get available RFQs count
    available_rfqs = db.query(RFQ).filter_by(status="open").count()
    
    # Monthly trends (last 6 months)
    monthly_data = []
    for i in range(6):
        month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        month_quotes = [q for q in quotes if month_start <= q.created_at < month_end]
        month_accepted = len([q for q in month_quotes if q.status == "accepted"])
        
        monthly_data.append({
            "month": month_start.strftime("%b %Y"),
            "quotes": len(month_quotes),
            "accepted": month_accepted,
            "win_rate": (month_accepted / len(month_quotes) * 100) if month_quotes else 0
        })
    
    monthly_data.reverse()  # Show oldest to newest
    
    return {
        "summary": {
            "total_quotes": total_quotes,
            "accepted_quotes": accepted_quotes,
            "pending_quotes": pending_quotes,
            "rejected_quotes": rejected_quotes,
            "win_rate": round(win_rate, 1),
            "total_quoted_value": total_value,
            "average_quote_value": avg_quote_value,
            "available_rfqs": available_rfqs
        },
        "supplier_info": {
            "id": supplier.id,
            "company_name": supplier.company_name,
            "rating": float(supplier.rating) if supplier.rating else 0,
            "response_rate": float(supplier.response_rate) if supplier.response_rate else 0,
            "is_verified": supplier.is_verified,
            "categories": supplier.categories or []
        },
        "trends": monthly_data,
        "period": {
            "days": days,
            "from_date": from_date.isoformat(),
            "to_date": datetime.utcnow().isoformat()
        }
    }


@router.get("/api/available-rfqs")
async def get_available_rfqs(
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("newest", description="Sort by: newest, deadline, budget"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available RFQs for suppliers"""
    if current_user.role != "supplier":
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    # Get supplier info
    supplier = db.query(Supplier).filter_by(
        company_id=current_user.company_id
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier profile not found")
    
    # Base query - only open RFQs
    query = db.query(RFQ).filter_by(status="open")
    
    # Apply filters
    if category:
        query = query.filter(RFQ.category == category)
    
    if search:
        query = query.filter(
            (RFQ.product_name.ilike(f"%{search}%")) |
            (RFQ.requirements.ilike(f"%{search}%"))
        )
    
    # Exclude RFQs where supplier already submitted quotes
    existing_quote_rfqs = db.query(Quote.rfq_id).filter_by(supplier_id=supplier.id).subquery()
    query = query.filter(~RFQ.id.in_(existing_quote_rfqs))
    
    # Sort
    if sort_by == "deadline":
        query = query.order_by(RFQ.delivery_date.asc())
    elif sort_by == "budget":
        query = query.order_by(RFQ.budget_max.desc().nulls_last())
    else:  # newest
        query = query.order_by(RFQ.created_at.desc())
    
    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    rfqs = query.offset(offset).limit(limit).all()
    
    # Format response
    rfq_list = []
    for rfq in rfqs:
        rfq_data = {
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
            "days_remaining": (rfq.delivery_date - datetime.utcnow()).days if rfq.delivery_date else None
        }
        rfq_list.append(rfq_data)
    
    return {
        "rfqs": rfq_list,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }


@router.get("/api/my-quotes")
async def get_my_quotes(
    status: Optional[str] = None,
    rfq_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get supplier's submitted quotes"""
    if current_user.role != "supplier":
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    # Get supplier info
    supplier = db.query(Supplier).filter_by(
        company_id=current_user.company_id
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier profile not found")
    
    # Base query
    query = db.query(Quote).filter_by(supplier_id=supplier.id)
    
    # Apply filters
    if status:
        query = query.filter(Quote.status == status)
    if rfq_id:
        query = query.filter(Quote.rfq_id == rfq_id)
    
    # Order by newest first
    query = query.order_by(Quote.created_at.desc())
    
    # Pagination
    total = query.count()
    offset = (page - 1) * limit
    quotes = query.offset(offset).limit(limit).all()
    
    # Format response with RFQ details
    quotes_list = []
    for quote in quotes:
        rfq = quote.rfq
        quote_data = {
            "id": quote.id,
            "rfq_id": quote.rfq_id,
            "rfq_number": rfq.rfq_number if rfq else None,
            "product_name": rfq.product_name if rfq else None,
            "quantity": rfq.quantity if rfq else None,
            "price_per_unit": float(quote.price_per_unit) if quote.price_per_unit else None,
            "total_price": float(quote.total_price) if quote.total_price else None,
            "currency": quote.currency,
            "delivery_time": quote.delivery_time,
            "payment_terms": quote.payment_terms,
            "notes": quote.notes,
            "status": quote.status,
            "created_at": quote.created_at.isoformat(),
            "buyer_feedback": getattr(quote, 'buyer_notes', None)
        }
        quotes_list.append(quote_data)
    
    return {
        "quotes": quotes_list,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }


@router.get("/api/profile")
async def get_supplier_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get supplier profile information"""
    if current_user.role != "supplier":
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    # Get supplier and company info
    supplier = db.query(Supplier).filter_by(
        company_id=current_user.company_id
    ).first()
    
    company = db.query(Company).filter_by(id=current_user.company_id).first()
    
    if not supplier:
        # Create basic supplier record
        supplier = Supplier(
            company_id=current_user.company_id,
            company_name=company.name if company else current_user.name,
            email=current_user.email,
            status="active"
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
    
    # Calculate performance metrics
    total_quotes = db.query(Quote).filter_by(supplier_id=supplier.id).count()
    accepted_quotes = db.query(Quote).filter_by(
        supplier_id=supplier.id, 
        status="accepted"
    ).count()
    
    win_rate = (accepted_quotes / total_quotes * 100) if total_quotes > 0 else 0
    
    # Get recent activity
    recent_quotes = db.query(Quote).filter_by(
        supplier_id=supplier.id
    ).order_by(Quote.created_at.desc()).limit(5).all()
    
    return {
        "supplier": {
            "id": supplier.id,
            "company_name": supplier.company_name,
            "email": supplier.email,
            "phone": supplier.phone,
            "website": supplier.website,
            "address": supplier.address,
            "city": supplier.city,
            "country": supplier.country,
            "categories": supplier.categories or [],
            "specialties": supplier.specialties or [],
            "certifications": supplier.certifications or [],
            "rating": float(supplier.rating) if supplier.rating else 0,
            "response_rate": float(supplier.response_rate) if supplier.response_rate else 0,
            "is_verified": supplier.is_verified,
            "status": supplier.status
        },
        "company": {
            "id": company.id if company else None,
            "name": company.name if company else None,
            "legal_name": company.legal_name if company else None,
            "registration_number": company.registration_number if company else None,
            "website": company.website if company else None,
            "phone": company.phone if company else None,
            "address": {
                "line1": company.address_line1 if company else None,
                "line2": company.address_line2 if company else None,
                "city": company.city if company else None,
                "state": company.state_province if company else None,
                "postal_code": company.postal_code if company else None,
                "country": company.country if company else None
            } if company else None
        },
        "performance": {
            "total_quotes": total_quotes,
            "accepted_quotes": accepted_quotes,
            "win_rate": round(win_rate, 1),
            "average_response_time": 24.0  # Placeholder
        },
        "recent_activity": [
            {
                "quote_id": q.id,
                "rfq_number": q.rfq.rfq_number if q.rfq else None,
                "product_name": q.rfq.product_name if q.rfq else None,
                "status": q.status,
                "submitted_at": q.created_at.isoformat()
            }
            for q in recent_quotes
        ]
    }


@router.put("/api/profile")
async def update_supplier_profile(
    profile_data: SupplierUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update supplier profile"""
    if current_user.role != "supplier":
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    # Get supplier record
    supplier = db.query(Supplier).filter_by(
        company_id=current_user.company_id
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier profile not found")
    
    # Update supplier fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(supplier, field):
            setattr(supplier, field, value)
    
    supplier.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(supplier)
    
    return {"message": "Profile updated successfully", "supplier_id": supplier.id}


@router.get("/api/categories")
async def get_product_categories(db: Session = Depends(get_db)):
    """Get available product categories"""
    # Get categories from existing RFQs
    categories = db.query(RFQ.category).filter(
        RFQ.category.isnot(None)
    ).distinct().all()
    
    category_list = [cat[0] for cat in categories if cat[0]]
    
    # Add common food categories if not present
    common_categories = [
        "fruits", "vegetables", "grains", "dairy", "meat", 
        "seafood", "beverages", "spices", "oils", "nuts"
    ]
    
    for cat in common_categories:
        if cat not in category_list:
            category_list.append(cat)
    
    return {"categories": sorted(category_list)}


@router.get("/api/performance-metrics")
async def get_performance_metrics(
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed performance metrics for supplier"""
    if current_user.role != "supplier":
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    # Parse period
    period_days = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}.get(period, 30)
    from_date = datetime.utcnow() - timedelta(days=period_days)
    
    # Get supplier
    supplier = db.query(Supplier).filter_by(
        company_id=current_user.company_id
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier profile not found")
    
    # Get quotes in period
    quotes = db.query(Quote).filter(
        Quote.supplier_id == supplier.id,
        Quote.created_at >= from_date
    ).all()
    
    # Calculate metrics
    total_quotes = len(quotes)
    accepted_quotes = len([q for q in quotes if q.status == "accepted"])
    pending_quotes = len([q for q in quotes if q.status == "pending"])
    rejected_quotes = len([q for q in quotes if q.status == "rejected"])
    
    # Win rate
    decided_quotes = accepted_quotes + rejected_quotes
    win_rate = (accepted_quotes / decided_quotes * 100) if decided_quotes > 0 else 0
    
    # Quote values
    quote_values = [float(q.total_price) for q in quotes if q.total_price]
    total_value = sum(quote_values)
    avg_value = total_value / len(quote_values) if quote_values else 0
    
    # Category breakdown
    category_stats = {}
    for quote in quotes:
        if quote.rfq and quote.rfq.category:
            cat = quote.rfq.category
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "accepted": 0}
            category_stats[cat]["total"] += 1
            if quote.status == "accepted":
                category_stats[cat]["accepted"] += 1
    
    # Add win rates to categories
    for cat, stats in category_stats.items():
        stats["win_rate"] = (stats["accepted"] / stats["total"] * 100) if stats["total"] > 0 else 0
    
    # Weekly trends
    weekly_trends = []
    for week_offset in range(min(8, period_days // 7)):  # Max 8 weeks
        week_start = datetime.utcnow() - timedelta(weeks=week_offset+1)
        week_end = datetime.utcnow() - timedelta(weeks=week_offset)
        
        week_quotes = [q for q in quotes if week_start <= q.created_at < week_end]
        week_accepted = len([q for q in week_quotes if q.status == "accepted"])
        
        weekly_trends.insert(0, {  # Insert at beginning for chronological order
            "week": week_start.strftime("%m/%d"),
            "quotes": len(week_quotes),
            "accepted": week_accepted,
            "win_rate": (week_accepted / len(week_quotes) * 100) if week_quotes else 0
        })
    
    return {
        "period": period,
        "summary": {
            "total_quotes": total_quotes,
            "accepted_quotes": accepted_quotes,
            "pending_quotes": pending_quotes,
            "rejected_quotes": rejected_quotes,
            "win_rate": round(win_rate, 1),
            "total_value": total_value,
            "average_value": avg_value
        },
        "category_performance": [
            {
                "category": cat,
                "total_quotes": stats["total"],
                "accepted_quotes": stats["accepted"],
                "win_rate": round(stats["win_rate"], 1)
            }
            for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]["total"], reverse=True)
        ],
        "weekly_trends": weekly_trends,
        "benchmarks": {
            "industry_avg_win_rate": 25.0,  # Placeholder industry benchmark
            "industry_avg_response_time": 48.0,  # Hours
            "your_ranking": "Top 30%"  # Placeholder ranking
        }
    }


@router.post("/api/quotes/{quote_id}/withdraw")
async def withdraw_quote(
    quote_id: int,
    reason: str = "Withdrawn by supplier",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Withdraw a submitted quote (if still pending)"""
    if current_user.role != "supplier":
        raise HTTPException(status_code=403, detail="Supplier access required")
    
    # Get supplier
    supplier = db.query(Supplier).filter_by(
        company_id=current_user.company_id
    ).first()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier profile not found")
    
    # Get quote
    quote = db.query(Quote).filter_by(
        id=quote_id,
        supplier_id=supplier.id
    ).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    if quote.status != "pending":
        raise HTTPException(status_code=400, detail="Can only withdraw pending quotes")
    
    # Update quote status
    quote.status = "withdrawn"
    quote.notes = f"{quote.notes}\n\nWithdrawn: {reason}" if quote.notes else f"Withdrawn: {reason}"
    
    db.commit()
    
    # Send notification to buyer
    if quote.rfq and quote.rfq.user_id:
        await notification_service.create_notification(
            user_id=quote.rfq.user_id,
            notification_type="quote_withdrawn",
            title=f"Quote Withdrawn for {quote.rfq.product_name}",
            message=f"Supplier has withdrawn their quote. Reason: {reason}",
            entity_type="quote",
            entity_id=quote.id,
            db=db
        )
    
    return {"message": "Quote withdrawn successfully", "quote_id": quote.id}