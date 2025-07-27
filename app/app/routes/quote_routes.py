"""
Quote management routes - Enhanced version
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.auth import get_current_user, get_current_user_context
from app.models.user import User
from app.models.rfq import RFQ
from app.models.quote import Quote
from app.models.supplier import Supplier
from app.models.company import Company
from app.schemas.quote import QuoteCreate, QuoteUpdate, QuoteResponse, QuoteComparison
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/quotes", tags=["quotes"])
notification_service = NotificationService()


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
    sort_by: str = Query("score", description="Sort by: score, price, delivery_time, supplier_rating"),
    include_analytics: bool = Query(True, description="Include detailed analytics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive quote comparison data for an RFQ"""
    rfq = db.query(RFQ).filter(
        RFQ.id == rfq_id,
        RFQ.user_id == current_user.id
    ).first()
    
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    # Get quotes with supplier information
    quotes = db.query(Quote).join(Supplier).filter(
        Quote.rfq_id == rfq_id,
        Quote.status != "rejected"
    ).all()
    
    if not quotes:
        return {
            "rfq": {
                "id": rfq.id,
                "rfq_number": rfq.rfq_number,
                "product_name": rfq.product_name,
                "quantity": rfq.quantity,
                "delivery_date": rfq.delivery_date.isoformat() if rfq.delivery_date else None
            },
            "quotes": [],
            "statistics": {},
            "recommendations": []
        }
    
    # Calculate comparison metrics
    prices = [float(q.total_price) for q in quotes if q.total_price]
    unit_prices = [float(q.price_per_unit) for q in quotes if q.price_per_unit]
    
    # Build quote comparison data
    quote_data = []
    for quote in quotes:
        supplier = quote.supplier
        quote_info = {
            "id": quote.id,
            "supplier_id": quote.supplier_id,
            "supplier_name": supplier.company_name if supplier else "Unknown",
            "supplier_rating": float(supplier.rating) if supplier and supplier.rating else 0,
            "supplier_response_rate": float(supplier.response_rate) if supplier and supplier.response_rate else 0,
            "price_per_unit": float(quote.price_per_unit) if quote.price_per_unit else None,
            "total_price": float(quote.total_price) if quote.total_price else None,
            "currency": quote.currency,
            "delivery_time": quote.delivery_time,
            "payment_terms": quote.payment_terms,
            "notes": quote.notes,
            "status": quote.status,
            "created_at": quote.created_at.isoformat(),
            "score": calculate_enhanced_quote_score(quote, prices, unit_prices, rfq)
        }
        
        # Add quality indicators
        quote_info["quality_indicators"] = {
            "has_competitive_price": is_competitive_price(quote.total_price, prices) if quote.total_price else False,
            "fast_delivery": is_fast_delivery(quote.delivery_time),
            "complete_information": calculate_completeness_score(quote),
            "trusted_supplier": supplier.rating >= 4.0 if supplier and supplier.rating else False
        }
        
        quote_data.append(quote_info)
    
    # Sort quotes
    if sort_by == "price":
        quote_data.sort(key=lambda x: x["total_price"] or float('inf'))
    elif sort_by == "delivery_time":
        quote_data.sort(key=lambda x: parse_delivery_days(x["delivery_time"]))
    elif sort_by == "supplier_rating":
        quote_data.sort(key=lambda x: x["supplier_rating"], reverse=True)
    else:  # Default to score
        quote_data.sort(key=lambda x: x["score"], reverse=True)
    
    # Build statistics
    statistics = {
        "total_quotes": len(quotes),
        "average_total_price": sum(prices) / len(prices) if prices else 0,
        "min_total_price": min(prices) if prices else 0,
        "max_total_price": max(prices) if prices else 0,
        "price_range": max(prices) - min(prices) if prices else 0,
        "average_delivery_days": calculate_average_delivery_days(quotes),
        "supplier_count": len(set(q.supplier_id for q in quotes)),
        "competitive_quotes": len([q for q in quote_data if q["quality_indicators"]["has_competitive_price"]])
    }
    
    # Generate recommendations
    recommendations = generate_quote_recommendations(quote_data, rfq)
    
    result = {
        "rfq": {
            "id": rfq.id,
            "rfq_number": rfq.rfq_number,
            "product_name": rfq.product_name,
            "quantity": rfq.quantity,
            "delivery_date": rfq.delivery_date.isoformat() if rfq.delivery_date else None,
            "budget_min": float(rfq.budget_min) if rfq.budget_min else None,
            "budget_max": float(rfq.budget_max) if rfq.budget_max else None
        },
        "quotes": quote_data,
        "statistics": statistics,
        "recommendations": recommendations
    }
    
    # Add detailed analytics if requested
    if include_analytics:
        result["analytics"] = {
            "price_distribution": calculate_price_distribution(prices),
            "delivery_time_analysis": analyze_delivery_times(quotes),
            "supplier_performance": analyze_supplier_performance(quotes),
            "market_insights": generate_market_insights(quote_data, rfq)
        }
    
    return result


@router.post("/", response_model=QuoteResponse)
async def create_quote(
    quote_data: QuoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new quote (suppliers only)"""
    # Verify RFQ exists and is open
    rfq = db.query(RFQ).filter_by(id=quote_data.rfq_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")
    
    if rfq.status != "open":
        raise HTTPException(status_code=400, detail="RFQ is not open for quotes")
    
    # Check if supplier already quoted
    existing_quote = db.query(Quote).filter_by(
        rfq_id=quote_data.rfq_id,
        supplier_id=quote_data.supplier_id
    ).first()
    
    if existing_quote:
        raise HTTPException(status_code=400, detail="Quote already submitted for this RFQ")
    
    # Create quote
    quote = Quote(**quote_data.dict())
    db.add(quote)
    db.commit()
    db.refresh(quote)
    
    # Send notification to buyer
    await notification_service.send_quote_notification(quote, db)
    
    return quote


@router.get("/analytics/dashboard")
async def get_quote_analytics_dashboard(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quote analytics dashboard data"""
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Base query for user's quotes
    if current_user.role == "buyer":
        # Buyer sees quotes for their RFQs
        quotes_query = db.query(Quote).join(RFQ).filter(
            RFQ.user_id == current_user.id,
            Quote.created_at >= from_date
        )
    else:
        # Supplier sees their quotes
        quotes_query = db.query(Quote).filter(
            Quote.supplier_id == current_user.company_id,
            Quote.created_at >= from_date
        )
    
    quotes = quotes_query.all()
    
    # Calculate metrics
    total_quotes = len(quotes)
    accepted_quotes = len([q for q in quotes if q.status == "accepted"])
    rejected_quotes = len([q for q in quotes if q.status == "rejected"])
    pending_quotes = len([q for q in quotes if q.status == "pending"])
    
    # Win rate calculation
    win_rate = (accepted_quotes / total_quotes * 100) if total_quotes > 0 else 0
    
    # Average response time (for suppliers)
    avg_response_time = calculate_average_response_time(quotes)
    
    # Quote value metrics
    quote_values = [float(q.total_price) for q in quotes if q.total_price]
    total_quoted_value = sum(quote_values)
    avg_quote_value = total_quoted_value / len(quote_values) if quote_values else 0
    
    return {
        "period": {
            "days": days,
            "from_date": from_date.isoformat(),
            "to_date": datetime.utcnow().isoformat()
        },
        "summary": {
            "total_quotes": total_quotes,
            "accepted_quotes": accepted_quotes,
            "rejected_quotes": rejected_quotes,
            "pending_quotes": pending_quotes,
            "win_rate": round(win_rate, 1),
            "total_quoted_value": total_quoted_value,
            "average_quote_value": avg_quote_value,
            "average_response_time_hours": avg_response_time
        },
        "trends": calculate_quote_trends(quotes, days),
        "top_categories": get_top_quoted_categories(quotes, db),
        "performance_metrics": calculate_performance_metrics(quotes, current_user.role)
    }


# Enhanced scoring and analytics functions

def calculate_enhanced_quote_score(quote: Quote, all_prices: List[float], unit_prices: List[float], rfq: RFQ) -> float:
    """Calculate enhanced score for quote based on multiple factors"""
    score = 0.0
    
    # Price competitiveness (35% weight)
    if quote.total_price and all_prices:
        min_price = min(all_prices)
        max_price = max(all_prices)
        if max_price > min_price:
            price_score = 1 - ((float(quote.total_price) - min_price) / (max_price - min_price))
            score += price_score * 35
        else:
            score += 35
    
    # Delivery performance (25% weight)
    delivery_score = calculate_delivery_score(quote.delivery_time, rfq.delivery_date)
    score += delivery_score * 0.25
    
    # Supplier reliability (20% weight)
    supplier_score = calculate_supplier_score(quote.supplier)
    score += supplier_score * 0.20
    
    # Payment terms (10% weight)
    payment_score = calculate_payment_terms_score(quote.payment_terms)
    score += payment_score * 0.10
    
    # Completeness and quality (10% weight)
    completeness_score = calculate_completeness_score(quote)
    score += completeness_score * 0.10
    
    return round(score, 1)


def calculate_delivery_score(delivery_time: str, required_date: datetime) -> float:
    """Calculate delivery score based on timeline"""
    if not delivery_time:
        return 50  # Medium score for missing info
    
    try:
        days = parse_delivery_days(delivery_time)
        if required_date:
            days_until_needed = (required_date - datetime.utcnow()).days
            if days <= days_until_needed:
                if days <= 3:
                    return 100
                elif days <= 7:
                    return 85
                elif days <= 14:
                    return 70
                else:
                    return 55
            else:
                return 20  # Too slow
        else:
            # No specific date required, score by general speed
            if days <= 3:
                return 100
            elif days <= 7:
                return 80
            elif days <= 14:
                return 60
            else:
                return 40
    except:
        return 50


def calculate_supplier_score(supplier: Supplier) -> float:
    """Calculate supplier reliability score"""
    if not supplier:
        return 50
    
    score = 50  # Base score
    
    # Rating contribution (40%)
    if supplier.rating:
        rating_score = (float(supplier.rating) / 5.0) * 40
        score += rating_score - 20  # Adjust from base
    
    # Response rate contribution (30%)
    if supplier.response_rate:
        response_score = float(supplier.response_rate) * 30
        score += response_score - 15
    
    # Verification status (30%)
    if supplier.is_verified:
        score += 15
    
    return min(100, max(0, score))


def calculate_payment_terms_score(payment_terms: str) -> float:
    """Calculate payment terms attractiveness score"""
    if not payment_terms:
        return 50
    
    terms_lower = payment_terms.lower()
    
    # Preferred terms get higher scores
    if "net 30" in terms_lower or "30 days" in terms_lower:
        return 100
    elif "net 15" in terms_lower or "15 days" in terms_lower:
        return 80
    elif "net 60" in terms_lower or "60 days" in terms_lower:
        return 60
    elif "cod" in terms_lower or "cash on delivery" in terms_lower:
        return 40
    elif "advance" in terms_lower or "prepaid" in terms_lower:
        return 20
    else:
        return 60  # Default for other terms


def calculate_completeness_score(quote: Quote) -> float:
    """Calculate how complete the quote information is"""
    fields = [
        quote.price_per_unit is not None,
        quote.total_price is not None,
        quote.delivery_time is not None,
        quote.payment_terms is not None,
        quote.notes is not None and len(quote.notes.strip()) > 10,
        quote.currency is not None
    ]
    
    return (sum(fields) / len(fields)) * 100


def is_competitive_price(price: float, all_prices: List[float]) -> bool:
    """Check if price is competitive (within bottom 50% of range)"""
    if not price or not all_prices or len(all_prices) < 2:
        return False
    
    sorted_prices = sorted(all_prices)
    median_index = len(sorted_prices) // 2
    median_price = sorted_prices[median_index]
    
    return price <= median_price


def is_fast_delivery(delivery_time: str) -> bool:
    """Check if delivery is considered fast (7 days or less)"""
    try:
        days = parse_delivery_days(delivery_time)
        return days <= 7
    except:
        return False


def parse_delivery_days(delivery_time: str) -> int:
    """Parse delivery time string to extract number of days"""
    if not delivery_time:
        return 999  # Very high number for sorting
    
    import re
    
    # Look for patterns like "3 days", "1 week", "2-3 days"
    delivery_lower = delivery_time.lower()
    
    # Handle weeks
    week_match = re.search(r'(\d+)\s*week', delivery_lower)
    if week_match:
        return int(week_match.group(1)) * 7
    
    # Handle days
    day_match = re.search(r'(\d+)(?:-\d+)?\s*day', delivery_lower)
    if day_match:
        return int(day_match.group(1))
    
    # Handle just numbers
    number_match = re.search(r'(\d+)', delivery_lower)
    if number_match:
        return int(number_match.group(1))
    
    return 999  # Default high value


def calculate_average_delivery_days(quotes: List[Quote]) -> float:
    """Calculate average delivery days across quotes"""
    days_list = []
    for quote in quotes:
        if quote.delivery_time:
            try:
                days = parse_delivery_days(quote.delivery_time)
                if days < 999:  # Valid parsed value
                    days_list.append(days)
            except:
                continue
    
    return sum(days_list) / len(days_list) if days_list else 0


def generate_quote_recommendations(quote_data: List[Dict], rfq: RFQ) -> List[Dict[str, Any]]:
    """Generate recommendations based on quote analysis"""
    recommendations = []
    
    if not quote_data:
        return recommendations
    
    # Best overall quote
    best_quote = max(quote_data, key=lambda x: x["score"])
    recommendations.append({
        "type": "best_overall",
        "title": "Recommended Choice",
        "quote_id": best_quote["id"],
        "reason": f"Highest overall score ({best_quote['score']}/100) considering price, delivery, and supplier reliability",
        "priority": "high"
    })
    
    # Lowest price quote
    price_quotes = [q for q in quote_data if q["total_price"]]
    if price_quotes:
        lowest_price = min(price_quotes, key=lambda x: x["total_price"])
        if lowest_price["id"] != best_quote["id"]:
            recommendations.append({
                "type": "lowest_price",
                "title": "Budget Option",
                "quote_id": lowest_price["id"],
                "reason": f"Lowest price at ${lowest_price['total_price']:.2f}",
                "priority": "medium"
            })
    
    # Fastest delivery quote
    fast_quotes = [q for q in quote_data if q["quality_indicators"]["fast_delivery"]]
    if fast_quotes:
        fastest = min(fast_quotes, key=lambda x: parse_delivery_days(x["delivery_time"]))
        if fastest["id"] not in [best_quote["id"], lowest_price["id"] if price_quotes else None]:
            recommendations.append({
                "type": "fastest_delivery",
                "title": "Express Option",
                "quote_id": fastest["id"],
                "reason": f"Fastest delivery in {fastest['delivery_time']}",
                "priority": "medium"
            })
    
    # Trusted supplier quote
    trusted_quotes = [q for q in quote_data if q["quality_indicators"]["trusted_supplier"]]
    if trusted_quotes:
        most_trusted = max(trusted_quotes, key=lambda x: x["supplier_rating"])
        existing_ids = [r["quote_id"] for r in recommendations]
        if most_trusted["id"] not in existing_ids:
            recommendations.append({
                "type": "trusted_supplier",
                "title": "Reliable Supplier",
                "quote_id": most_trusted["id"],
                "reason": f"Highly rated supplier ({most_trusted['supplier_rating']:.1f}/5.0 stars)",
                "priority": "low"
            })
    
    return recommendations


def calculate_price_distribution(prices: List[float]) -> Dict[str, Any]:
    """Calculate price distribution statistics"""
    if not prices:
        return {}
    
    sorted_prices = sorted(prices)
    n = len(sorted_prices)
    
    return {
        "min": sorted_prices[0],
        "max": sorted_prices[-1],
        "median": sorted_prices[n // 2],
        "q1": sorted_prices[n // 4],
        "q3": sorted_prices[3 * n // 4],
        "mean": sum(prices) / len(prices),
        "std_dev": calculate_std_deviation(prices)
    }


def calculate_std_deviation(values: List[float]) -> float:
    """Calculate standard deviation"""
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5


def analyze_delivery_times(quotes: List[Quote]) -> Dict[str, Any]:
    """Analyze delivery time patterns"""
    delivery_days = []
    for quote in quotes:
        if quote.delivery_time:
            try:
                days = parse_delivery_days(quote.delivery_time)
                if days < 999:
                    delivery_days.append(days)
            except:
                continue
    
    if not delivery_days:
        return {}
    
    return {
        "average_days": sum(delivery_days) / len(delivery_days),
        "min_days": min(delivery_days),
        "max_days": max(delivery_days),
        "fast_delivery_count": len([d for d in delivery_days if d <= 7]),
        "standard_delivery_count": len([d for d in delivery_days if 7 < d <= 14]),
        "slow_delivery_count": len([d for d in delivery_days if d > 14])
    }


def analyze_supplier_performance(quotes: List[Quote]) -> Dict[str, Any]:
    """Analyze supplier performance metrics"""
    suppliers = [q.supplier for q in quotes if q.supplier]
    
    if not suppliers:
        return {}
    
    ratings = [float(s.rating) for s in suppliers if s.rating]
    response_rates = [float(s.response_rate) for s in suppliers if s.response_rate]
    verified_count = sum(1 for s in suppliers if s.is_verified)
    
    return {
        "total_suppliers": len(suppliers),
        "average_rating": sum(ratings) / len(ratings) if ratings else 0,
        "average_response_rate": sum(response_rates) / len(response_rates) if response_rates else 0,
        "verified_suppliers": verified_count,
        "verification_rate": (verified_count / len(suppliers) * 100) if suppliers else 0
    }


def generate_market_insights(quote_data: List[Dict], rfq: RFQ) -> Dict[str, Any]:
    """Generate market insights from quote data"""
    if not quote_data:
        return {}
    
    total_quotes = len(quote_data)
    competitive_quotes = len([q for q in quote_data if q["quality_indicators"]["has_competitive_price"]])
    fast_delivery_quotes = len([q for q in quote_data if q["quality_indicators"]["fast_delivery"]])
    
    insights = {
        "market_competition": "high" if total_quotes >= 5 else "medium" if total_quotes >= 3 else "low",
        "price_competitiveness": (competitive_quotes / total_quotes * 100) if total_quotes > 0 else 0,
        "delivery_options": "excellent" if fast_delivery_quotes >= 3 else "good" if fast_delivery_quotes >= 1 else "limited",
        "recommendations": []
    }
    
    # Add specific insights
    if insights["market_competition"] == "high":
        insights["recommendations"].append("Strong competition - good negotiating position")
    
    if insights["price_competitiveness"] > 60:
        insights["recommendations"].append("Multiple competitive price options available")
    
    if fast_delivery_quotes == 0:
        insights["recommendations"].append("Consider extending delivery timeline for better prices")
    
    return insights


def calculate_average_response_time(quotes: List[Quote]) -> float:
    """Calculate average response time for quotes (placeholder)"""
    # This would require RFQ creation time vs quote creation time
    # For now, return a placeholder value
    return 24.0  # 24 hours average


def calculate_quote_trends(quotes: List[Quote], days: int) -> Dict[str, Any]:
    """Calculate quote trends over time period"""
    # Group quotes by day
    daily_counts = {}
    for quote in quotes:
        day = quote.created_at.date()
        daily_counts[day] = daily_counts.get(day, 0) + 1
    
    # Calculate trend
    recent_half = days // 2
    from_date = datetime.utcnow() - timedelta(days=days)
    mid_date = datetime.utcnow() - timedelta(days=recent_half)
    
    early_period_quotes = [q for q in quotes if from_date <= q.created_at < mid_date]
    recent_period_quotes = [q for q in quotes if q.created_at >= mid_date]
    
    early_count = len(early_period_quotes)
    recent_count = len(recent_period_quotes)
    
    if early_count > 0:
        trend_percentage = ((recent_count - early_count) / early_count) * 100
    else:
        trend_percentage = 100 if recent_count > 0 else 0
    
    return {
        "daily_average": len(quotes) / days if days > 0 else 0,
        "trend_direction": "up" if trend_percentage > 10 else "down" if trend_percentage < -10 else "stable",
        "trend_percentage": round(trend_percentage, 1),
        "recent_period_count": recent_count,
        "early_period_count": early_count
    }


def get_top_quoted_categories(quotes: List[Quote], db: Session) -> List[Dict[str, Any]]:
    """Get top categories by quote volume"""
    # Get RFQ categories for quotes
    rfq_ids = [q.rfq_id for q in quotes if q.rfq_id]
    rfqs = db.query(RFQ).filter(RFQ.id.in_(rfq_ids)).all()
    
    category_counts = {}
    for rfq in rfqs:
        if rfq.category:
            category_counts[rfq.category] = category_counts.get(rfq.category, 0) + 1
    
    # Sort by count and return top 5
    sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return [
        {"category": category, "quote_count": count}
        for category, count in sorted_categories
    ]


def calculate_performance_metrics(quotes: List[Quote], user_role: str) -> Dict[str, Any]:
    """Calculate role-specific performance metrics"""
    if user_role == "supplier":
        # Supplier metrics
        total_quotes = len(quotes)
        won_quotes = len([q for q in quotes if q.status == "accepted"])
        avg_quote_value = sum(float(q.total_price) for q in quotes if q.total_price) / total_quotes if total_quotes > 0 else 0
        
        return {
            "win_rate": (won_quotes / total_quotes * 100) if total_quotes > 0 else 0,
            "quotes_per_week": total_quotes / 4.3,  # Approximate weeks in month
            "average_quote_value": avg_quote_value,
            "response_time_rating": "good"  # Placeholder
        }
    else:
        # Buyer metrics
        rfq_count = len(set(q.rfq_id for q in quotes if q.rfq_id))
        avg_quotes_per_rfq = len(quotes) / rfq_count if rfq_count > 0 else 0
        
        return {
            "rfqs_created": rfq_count,
            "average_quotes_per_rfq": avg_quotes_per_rfq,
            "supplier_engagement": "high" if avg_quotes_per_rfq >= 3 else "medium" if avg_quotes_per_rfq >= 2 else "low",
            "decision_rate": len([q for q in quotes if q.status in ["accepted", "rejected"]]) / len(quotes) * 100 if quotes else 0
        }


def calculate_quote_score(quote: Quote, all_prices: List[float]) -> float:
    """Legacy quote scoring function - kept for backward compatibility"""
    return calculate_enhanced_quote_score(quote, all_prices, [], None)


def include_quote_routes(app):
    """Include quote routes in the main app"""
    app.include_router(router)