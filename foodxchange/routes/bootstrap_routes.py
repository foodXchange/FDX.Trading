from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Any
import json

router = APIRouter(prefix="/bootstrap", tags=["bootstrap"])
templates = Jinja2Templates(directory="foodxchange/templates")

# Bootstrap Routes
@router.get("/rfq", response_class=HTMLResponse)
async def rfq_form(request: Request):
    """RFQ Creation Form"""
    return templates.TemplateResponse(
        "bootstrap/rfq-form.html",
        {"request": request, "title": "Create RFQ"}
    )

@router.get("/orders", response_class=HTMLResponse)
async def order_management(request: Request):
    """Order Management Interface"""
    return templates.TemplateResponse(
        "bootstrap/order-management.html",
        {"request": request, "title": "Order Management"}
    )

@router.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard(request: Request):
    """Analytics Dashboard"""
    return templates.TemplateResponse(
        "bootstrap/analytics.html",
        {"request": request, "title": "Analytics Dashboard"}
    )

@router.get("/help", response_class=HTMLResponse)
async def help_support(request: Request):
    """Help & Support Center"""
    return templates.TemplateResponse(
        "bootstrap/help.html",
        {"request": request, "title": "Help & Support"}
    )

# API Endpoints for Bootstrap Screens

@router.post("/api/rfq")
async def create_rfq(rfq_data: Dict[str, Any]):
    """Create a new RFQ"""
    try:
        # Validate required fields
        required_fields = ['productCategory', 'quantity', 'unit', 'deliveryDate', 'budget', 'companyName', 'contactName', 'email', 'phone']
        for field in required_fields:
            if not rfq_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Here you would typically save to database
        # For now, return success response
        return {
            "success": True,
            "message": "RFQ created successfully",
            "rfq_id": "RFQ-" + str(hash(str(rfq_data)))[:8]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/orders")
async def get_orders():
    """Get orders for order management"""
    # Mock data - replace with database query
    orders = [
        {
            "id": "ORD-001",
            "date": "2024-01-15",
            "customer": "ABC Restaurant",
            "products": [{"name": "Organic Rice", "quantity": 100, "price": 2.50}],
            "total": 250.00,
            "status": "pending"
        },
        {
            "id": "ORD-002",
            "date": "2024-01-14",
            "customer": "XYZ Catering",
            "products": [{"name": "Fresh Vegetables", "quantity": 50, "price": 1.75}],
            "total": 87.50,
            "status": "confirmed"
        },
        {
            "id": "ORD-003",
            "date": "2024-01-13",
            "customer": "City Market",
            "products": [{"name": "Dairy Products", "quantity": 200, "price": 3.20}],
            "total": 640.00,
            "status": "shipped"
        }
    ]
    return {"orders": orders}

@router.get("/api/orders/{order_id}")
async def get_order_details(order_id: str):
    """Get specific order details"""
    # Mock data - replace with database query
    order = {
        "id": order_id,
        "date": "2024-01-15",
        "customer": "ABC Restaurant",
        "email": "contact@abcrestaurant.com",
        "phone": "+1-555-0123",
        "status": "pending",
        "total": 250.00,
        "products": [
            {"name": "Organic Rice", "quantity": 100, "price": 2.50},
            {"name": "Fresh Vegetables", "quantity": 25, "price": 1.75}
        ]
    }
    return {"order": order}

@router.post("/api/orders/{order_id}/cancel")
async def cancel_order(order_id: str, cancel_data: Dict[str, Any]):
    """Cancel an order"""
    try:
        # Here you would typically update database
        return {
            "success": True,
            "message": f"Order {order_id} cancelled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/analytics/metrics")
async def get_analytics_metrics():
    """Get analytics metrics"""
    return {
        "totalRevenue": 45678,
        "totalOrders": 1234,
        "activeSuppliers": 89,
        "pendingRFQs": 23
    }

@router.get("/api/analytics/order-status")
async def get_order_status_distribution():
    """Get order status distribution"""
    return [
        {"status": "pending", "count": 45, "percentage": 15},
        {"status": "confirmed", "count": 120, "percentage": 40},
        {"status": "shipped", "count": 90, "percentage": 30},
        {"status": "delivered", "count": 30, "percentage": 10},
        {"status": "cancelled", "count": 15, "percentage": 5}
    ]

@router.get("/api/analytics/recent-activity")
async def get_recent_activity():
    """Get recent activity"""
    return [
        {
            "title": "New RFQ Created",
            "description": "ABC Restaurant created RFQ for organic rice",
            "time": "2 hours ago"
        },
        {
            "title": "Order Shipped",
            "description": "Order ORD-003 has been shipped to City Market",
            "time": "4 hours ago"
        },
        {
            "title": "New Supplier Registered",
            "description": "Fresh Foods Co. joined the platform",
            "time": "6 hours ago"
        },
        {
            "title": "Payment Received",
            "description": "Payment received for order ORD-002",
            "time": "1 day ago"
        }
    ]

@router.post("/api/support/contact")
async def submit_support_contact(contact_data: Dict[str, Any]):
    """Submit support contact form"""
    try:
        # Validate required fields
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not contact_data.get(field):
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Here you would typically save to database and send email
        return {
            "success": True,
            "message": "Support request submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Additional API endpoints for dropdowns and form data

@router.get("/api/categories")
async def get_product_categories():
    """Get product categories for RFQ form"""
    return [
        {"value": "grains", "label": "Grains"},
        {"value": "dairy", "label": "Dairy"},
        {"value": "meat", "label": "Meat"},
        {"value": "produce", "label": "Produce"},
        {"value": "beverages", "label": "Beverages"},
        {"value": "frozen", "label": "Frozen Foods"},
        {"value": "organic", "label": "Organic"},
        {"value": "kosher", "label": "Kosher"}
    ]

@router.get("/api/units")
async def get_units():
    """Get units for RFQ form"""
    return [
        {"value": "kg", "label": "Kilograms (kg)"},
        {"value": "lbs", "label": "Pounds (lbs)"},
        {"value": "cases", "label": "Cases"},
        {"value": "pallets", "label": "Pallets"},
        {"value": "units", "label": "Units"}
    ] 