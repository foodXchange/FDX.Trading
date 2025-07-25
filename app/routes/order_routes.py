"""
Order management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.order_item import OrderItem
from app.models.order_status_history import OrderStatusHistory
from app.models.company import Company
from app.models.user import User
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse,
    OrderItemCreate, OrderItemUpdate, OrderItemResponse,
    OrderStatusUpdate, OrderStatusHistoryResponse
)
from app.auth import get_current_user
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/api/orders", tags=["orders"])
notification_service = NotificationService()


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order"""
    # Verify buyer company exists
    buyer_company = db.query(Company).filter_by(id=order_data.buyer_company_id).first()
    if not buyer_company:
        raise HTTPException(status_code=404, detail="Buyer company not found")
    
    # Verify supplier company exists
    supplier_company = db.query(Company).filter_by(id=order_data.supplier_company_id).first()
    if not supplier_company:
        raise HTTPException(status_code=404, detail="Supplier company not found")
    
    # Generate order number
    order_number = f"PO-{datetime.utcnow().strftime('%Y%m%d')}-{db.query(Order).count() + 1:04d}"
    
    # Create order
    order = Order(
        order_number=order_number,
        po_number=order_data.po_number,
        buyer_company_id=order_data.buyer_company_id,
        supplier_company_id=order_data.supplier_company_id,
        buyer_contact_id=order_data.buyer_contact_id,
        supplier_contact_id=order_data.supplier_contact_id,
        rfq_id=order_data.rfq_id,
        quote_id=order_data.quote_id,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.PENDING,
        subtotal=order_data.subtotal,
        tax_amount=order_data.tax_amount or 0,
        shipping_amount=order_data.shipping_amount or 0,
        discount_amount=order_data.discount_amount or 0,
        total_amount=order_data.total_amount,
        currency=order_data.currency or "USD",
        payment_terms=order_data.payment_terms,
        payment_method=order_data.payment_method,
        payment_due_date=order_data.payment_due_date,
        requested_delivery_date=order_data.requested_delivery_date,
        delivery_address=order_data.delivery_address,
        delivery_instructions=order_data.delivery_instructions,
        notes=order_data.notes,
        internal_notes=order_data.internal_notes,
        special_requirements=order_data.special_requirements
    )
    
    db.add(order)
    db.flush()  # Get order ID
    
    # Add order items
    for item_data in order_data.items:
        item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            product_name=item_data.product_name,
            product_sku=item_data.product_sku,
            product_description=item_data.product_description,
            quantity=item_data.quantity,
            unit=item_data.unit,
            unit_price=item_data.unit_price,
            total_amount=item_data.total_amount,
            currency=item_data.currency or "USD",
            specifications=item_data.specifications,
            requested_delivery_date=item_data.requested_delivery_date
        )
        db.add(item)
    
    # Create initial status history
    history = OrderStatusHistory(
        order_id=order.id,
        from_status=None,
        to_status=OrderStatus.PENDING.value,
        changed_by_user_id=current_user.id,
        changed_by_name=current_user.name,
        changed_by_role=current_user.role,
        reason="Order created"
    )
    db.add(history)
    
    db.commit()
    db.refresh(order)
    
    # Send notifications
    await notification_service.send_order_created_notification(order, db)
    
    return order


@router.get("/", response_model=List[OrderListResponse])
async def list_orders(
    status: Optional[OrderStatus] = None,
    payment_status: Optional[PaymentStatus] = None,
    buyer_company_id: Optional[int] = None,
    supplier_company_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List orders with filters"""
    query = db.query(Order)
    
    # Apply filters based on user role
    if current_user.company_id:
        # Filter by user's company
        query = query.filter(
            (Order.buyer_company_id == current_user.company_id) |
            (Order.supplier_company_id == current_user.company_id)
        )
    
    # Apply additional filters
    if status:
        query = query.filter(Order.status == status)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    if buyer_company_id:
        query = query.filter(Order.buyer_company_id == buyer_company_id)
    if supplier_company_id:
        query = query.filter(Order.supplier_company_id == supplier_company_id)
    if from_date:
        query = query.filter(Order.order_date >= from_date)
    if to_date:
        query = query.filter(Order.order_date <= to_date)
    
    # Pagination
    offset = (page - 1) * limit
    orders = query.offset(offset).limit(limit).all()
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order details"""
    order = db.query(Order).filter_by(id=order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.company_id:
        if order.buyer_company_id != current_user.company_id and \
           order.supplier_company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order details"""
    order = db.query(Order).filter_by(id=order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.company_id:
        if order.buyer_company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Only buyer can update order")
    
    # Update fields
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status"""
    order = db.query(Order).filter_by(id=order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions based on status change
    if current_user.company_id:
        if status_update.status in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING, OrderStatus.SHIPPED]:
            # Supplier actions
            if order.supplier_company_id != current_user.company_id:
                raise HTTPException(status_code=403, detail="Only supplier can perform this action")
        elif status_update.status in [OrderStatus.CANCELLED]:
            # Both can cancel
            if order.buyer_company_id != current_user.company_id and \
               order.supplier_company_id != current_user.company_id:
                raise HTTPException(status_code=403, detail="Access denied")
        elif status_update.status in [OrderStatus.DELIVERED, OrderStatus.COMPLETED]:
            # Buyer confirms delivery
            if order.buyer_company_id != current_user.company_id:
                raise HTTPException(status_code=403, detail="Only buyer can confirm delivery")
    
    # Create status history
    history = OrderStatusHistory(
        order_id=order.id,
        from_status=order.status.value,
        to_status=status_update.status.value,
        changed_by_user_id=current_user.id,
        changed_by_name=current_user.name,
        changed_by_role=current_user.role,
        reason=status_update.reason,
        notes=status_update.notes
    )
    db.add(history)
    
    # Update order status
    old_status = order.status
    order.status = status_update.status
    order.updated_at = datetime.utcnow()
    
    # Update status dates
    if status_update.status == OrderStatus.CONFIRMED:
        order.confirmed_date = datetime.utcnow()
    elif status_update.status == OrderStatus.SHIPPED:
        order.shipped_date = datetime.utcnow()
    elif status_update.status == OrderStatus.DELIVERED:
        order.delivered_date = datetime.utcnow()
    elif status_update.status == OrderStatus.COMPLETED:
        order.completed_date = datetime.utcnow()
    elif status_update.status == OrderStatus.CANCELLED:
        order.cancelled_date = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    # Send notifications
    await notification_service.send_order_status_notification(order, old_status, db)
    
    return order


@router.get("/{order_id}/items", response_model=List[OrderItemResponse])
async def get_order_items(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order items"""
    order = db.query(Order).filter_by(id=order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.company_id:
        if order.buyer_company_id != current_user.company_id and \
           order.supplier_company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    items = db.query(OrderItem).filter_by(order_id=order_id).all()
    return items


@router.post("/{order_id}/items", response_model=OrderItemResponse)
async def add_order_item(
    order_id: int,
    item_data: OrderItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to order"""
    order = db.query(Order).filter_by(id=order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions and status
    if current_user.company_id:
        if order.buyer_company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Only buyer can add items")
    
    if order.status not in [OrderStatus.DRAFT, OrderStatus.PENDING]:
        raise HTTPException(status_code=400, detail="Cannot add items to confirmed order")
    
    # Create item
    item = OrderItem(
        order_id=order.id,
        product_id=item_data.product_id,
        product_name=item_data.product_name,
        product_sku=item_data.product_sku,
        product_description=item_data.product_description,
        quantity=item_data.quantity,
        unit=item_data.unit,
        unit_price=item_data.unit_price,
        total_amount=item_data.total_amount,
        currency=item_data.currency or order.currency,
        specifications=item_data.specifications,
        requested_delivery_date=item_data.requested_delivery_date
    )
    
    db.add(item)
    
    # Update order totals
    order.subtotal += item.total_amount
    order.total_amount = order.subtotal + order.tax_amount + order.shipping_amount - order.discount_amount
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    
    return item


@router.put("/{order_id}/items/{item_id}", response_model=OrderItemResponse)
async def update_order_item(
    order_id: int,
    item_id: int,
    item_update: OrderItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order item"""
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    item = db.query(OrderItem).filter_by(id=item_id, order_id=order_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    # Check permissions and status
    if current_user.company_id:
        if order.buyer_company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Only buyer can update items")
    
    if order.status not in [OrderStatus.DRAFT, OrderStatus.PENDING]:
        raise HTTPException(status_code=400, detail="Cannot update items in confirmed order")
    
    # Update item
    old_amount = item.total_amount
    update_data = item_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    item.updated_at = datetime.utcnow()
    
    # Update order totals if amount changed
    if item.total_amount != old_amount:
        order.subtotal = order.subtotal - old_amount + item.total_amount
        order.total_amount = order.subtotal + order.tax_amount + order.shipping_amount - order.discount_amount
        order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/{order_id}/items/{item_id}")
async def delete_order_item(
    order_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete order item"""
    order = db.query(Order).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    item = db.query(OrderItem).filter_by(id=item_id, order_id=order_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")
    
    # Check permissions and status
    if current_user.company_id:
        if order.buyer_company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Only buyer can delete items")
    
    if order.status not in [OrderStatus.DRAFT, OrderStatus.PENDING]:
        raise HTTPException(status_code=400, detail="Cannot delete items from confirmed order")
    
    # Update order totals
    order.subtotal -= item.total_amount
    order.total_amount = order.subtotal + order.tax_amount + order.shipping_amount - order.discount_amount
    order.updated_at = datetime.utcnow()
    
    db.delete(item)
    db.commit()
    
    return {"detail": "Item deleted successfully"}


@router.get("/{order_id}/history", response_model=List[OrderStatusHistoryResponse])
async def get_order_history(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order status history"""
    order = db.query(Order).filter_by(id=order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check permissions
    if current_user.company_id:
        if order.buyer_company_id != current_user.company_id and \
           order.supplier_company_id != current_user.company_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    history = db.query(OrderStatusHistory).filter_by(order_id=order_id).order_by(
        OrderStatusHistory.created_at.desc()
    ).all()
    
    return history


@router.get("/analytics/summary")
async def get_order_analytics(
    from_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    to_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order analytics summary"""
    # Default to last 30 days if no dates provided
    if not to_date:
        to_date = datetime.utcnow()
    if not from_date:
        from_date = to_date - timedelta(days=30)
    
    query = db.query(Order).filter(
        Order.order_date >= from_date,
        Order.order_date <= to_date
    )
    
    # Filter by user's company
    if current_user.company_id:
        query = query.filter(
            (Order.buyer_company_id == current_user.company_id) |
            (Order.supplier_company_id == current_user.company_id)
        )
    
    orders = query.all()
    
    # Calculate analytics
    total_orders = len(orders)
    total_value = sum(order.total_amount for order in orders)
    
    # Status breakdown
    status_counts = {}
    for status in OrderStatus:
        count = len([o for o in orders if o.status == status])
        if count > 0:
            status_counts[status.value] = count
    
    # Payment status breakdown
    payment_status_counts = {}
    for status in PaymentStatus:
        count = len([o for o in orders if o.payment_status == status])
        if count > 0:
            payment_status_counts[status.value] = count
    
    # Average order value
    avg_order_value = total_value / total_orders if total_orders > 0 else 0
    
    # Top suppliers (if buyer) or top buyers (if supplier)
    if current_user.company_id:
        if current_user.role == "buyer":
            # Top suppliers
            supplier_orders = {}
            for order in orders:
                if order.buyer_company_id == current_user.company_id:
                    supplier_id = order.supplier_company_id
                    if supplier_id not in supplier_orders:
                        supplier_orders[supplier_id] = {"count": 0, "value": 0}
                    supplier_orders[supplier_id]["count"] += 1
                    supplier_orders[supplier_id]["value"] += order.total_amount
            
            top_partners = sorted(
                supplier_orders.items(), 
                key=lambda x: x[1]["value"], 
                reverse=True
            )[:5]
        else:
            # Top buyers
            buyer_orders = {}
            for order in orders:
                if order.supplier_company_id == current_user.company_id:
                    buyer_id = order.buyer_company_id
                    if buyer_id not in buyer_orders:
                        buyer_orders[buyer_id] = {"count": 0, "value": 0}
                    buyer_orders[buyer_id]["count"] += 1
                    buyer_orders[buyer_id]["value"] += order.total_amount
            
            top_partners = sorted(
                buyer_orders.items(), 
                key=lambda x: x[1]["value"], 
                reverse=True
            )[:5]
    else:
        top_partners = []
    
    return {
        "period": {
            "from": from_date.isoformat(),
            "to": to_date.isoformat()
        },
        "summary": {
            "total_orders": total_orders,
            "total_value": total_value / 100,  # Convert from cents
            "average_order_value": avg_order_value / 100,
            "currency": "USD"
        },
        "status_breakdown": status_counts,
        "payment_status_breakdown": payment_status_counts,
        "top_partners": [
            {
                "company_id": partner_id,
                "order_count": data["count"],
                "total_value": data["value"] / 100
            }
            for partner_id, data in top_partners
        ]
    }