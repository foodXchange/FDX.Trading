"""
Quote management routes
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.auth import get_current_user, get_current_user_context
from app.models.user import User
from app.models.rfq import RFQ
from app.models.quote import Quote
from app.models.supplier import Supplier

router = APIRouter(prefix="/api/quotes", tags=["quotes"])


@router.get("/", response_model=List[dict])
async def get_quotes(
    rfq_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quotes with filters"""
    # Base query - only quotes for user's RFQs
    query = db.query(Quote).join(RFQ).filter(RFQ.user_id == current_user.id)
    
    if rfq_id:
        query = query.filter(Quote.rfq_id == rfq_id)
    if supplier_id:
        query = query.filter(Quote.supplier_id == supplier_id)
    if status:
        query = query.filter(Quote.status == status)
    
    quotes = query.order_by(Quote.created_at.desc()).all()
    
    return [
        {
            "id": quote.id,
            "rfq_id": quote.rfq_id,
            "rfq_number": quote.rfq.rfq_number,
            "product_name": quote.rfq.product_name,
            "supplier_id": quote.supplier_id,
            "supplier_name": quote.supplier.name if quote.supplier else "Unknown",
            "price_per_unit": float(quote.price_per_unit) if quote.price_per_unit else None,
            "total_price": float(quote.total_price) if quote.total_price else None,
            "currency": quote.currency,
            "delivery_time": quote.delivery_time,
            "payment_terms": quote.payment_terms,
            "status": quote.status,
            "created_at": quote.created_at.isoformat()
        }
        for quote in quotes
    ]


@router.put("/{quote_id}")
async def update_quote(
    quote_id: int,
    price_per_unit: Optional[float] = None,
    total_price: Optional[float] = None,
    currency: Optional[str] = None,
    delivery_time: Optional[str] = None,
    payment_terms: Optional[str] = None,
    notes: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a quote (supplier or admin only)"""
    # For now, allow any authenticated user to update quotes
    # In production, check if user is supplier or admin
    
    quote = db.query(Quote).filter(Quote.id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Update fields if provided
    if price_per_unit is not None:
        quote.price_per_unit = price_per_unit
    if total_price is not None:
        quote.total_price = total_price
    if currency:
        quote.currency = currency
    if delivery_time:
        quote.delivery_time = delivery_time
    if payment_terms:
        quote.payment_terms = payment_terms
    if notes:
        quote.notes = notes
    if status:
        quote.status = status
    
    db.commit()
    db.refresh(quote)
    
    return {"message": "Quote updated successfully", "quote_id": quote.id}


@router.post("/{quote_id}/accept")
async def accept_quote(
    quote_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept a quote and close the RFQ"""
    quote = db.query(Quote).join(RFQ).filter(
        Quote.id == quote_id,
        RFQ.user_id == current_user.id
    ).first()
    
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Update quote status
    quote.status = "accepted"
    
    # Update RFQ status
    quote.rfq.status = "closed"
    
    # Reject other quotes for this RFQ
    db.query(Quote).filter(
        Quote.rfq_id == quote.rfq_id,
        Quote.id != quote_id
    ).update({"status": "rejected"})
    
    db.commit()
    
    return {
        "message": "Quote accepted successfully",
        "quote_id": quote.id,
        "rfq_id": quote.rfq_id
    }


@router.get("/comparison/{rfq_id}")
async def compare_quotes(
    rfq_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quote comparison data for an RFQ"""
    rfq = db.query(RFQ).filter(
        RFQ.id == rfq_id,
        RFQ.user_id == current_user.id
    ).first()
    
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    quotes = db.query(Quote).filter(
        Quote.rfq_id == rfq_id,
        Quote.status != "rejected"
    ).all()
    
    # Calculate comparison metrics
    prices = [float(q.price_per_unit) for q in quotes if q.price_per_unit]
    
    comparison = {
        "rfq": {
            "id": rfq.id,
            "rfq_number": rfq.rfq_number,
            "product_name": rfq.product_name,
            "quantity": rfq.quantity
        },
        "quotes": [
            {
                "id": quote.id,
                "supplier_name": quote.supplier.name if quote.supplier else "Unknown",
                "price_per_unit": float(quote.price_per_unit) if quote.price_per_unit else None,
                "total_price": float(quote.total_price) if quote.total_price else None,
                "currency": quote.currency,
                "delivery_time": quote.delivery_time,
                "payment_terms": quote.payment_terms,
                "notes": quote.notes,
                "status": quote.status,
                "score": calculate_quote_score(quote, prices)
            }
            for quote in quotes
        ],
        "statistics": {
            "total_quotes": len(quotes),
            "average_price": sum(prices) / len(prices) if prices else 0,
            "min_price": min(prices) if prices else 0,
            "max_price": max(prices) if prices else 0,
            "price_range": max(prices) - min(prices) if prices else 0
        }
    }
    
    # Sort quotes by score
    comparison["quotes"].sort(key=lambda x: x["score"], reverse=True)
    
    return comparison


def calculate_quote_score(quote: Quote, all_prices: List[float]) -> float:
    """Calculate a score for a quote based on various factors"""
    score = 0.0
    
    # Price score (40% weight)
    if quote.price_per_unit and all_prices:
        min_price = min(all_prices)
        max_price = max(all_prices)
        if max_price > min_price:
            price_score = 1 - ((float(quote.price_per_unit) - min_price) / (max_price - min_price))
            score += price_score * 40
        else:
            score += 40  # All prices are the same
    
    # Delivery time score (30% weight)
    if quote.delivery_time:
        try:
            days = int(quote.delivery_time.split()[0])
            if days <= 3:
                score += 30
            elif days <= 7:
                score += 20
            elif days <= 14:
                score += 10
        except:
            score += 15  # Default if can't parse
    
    # Payment terms score (20% weight)
    if quote.payment_terms:
        if "net 30" in quote.payment_terms.lower():
            score += 20
        elif "net 15" in quote.payment_terms.lower():
            score += 15
        elif "cod" in quote.payment_terms.lower():
            score += 5
        else:
            score += 10
    
    # Completeness score (10% weight)
    completeness = sum([
        1 if quote.price_per_unit else 0,
        1 if quote.total_price else 0,
        1 if quote.delivery_time else 0,
        1 if quote.payment_terms else 0,
        1 if quote.notes else 0
    ])
    score += (completeness / 5) * 10
    
    return round(score, 1)


def include_quote_routes(app):
    """Include quote routes in the main app"""
    app.include_router(router)