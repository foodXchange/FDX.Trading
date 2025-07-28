"""
Order-related Pydantic schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

from foodxchange.models.order import OrderStatus, PaymentStatus


class OrderItemBase(BaseModel):
    """Base schema for order items"""
    product_id: Optional[int] = None
    product_name: str
    product_sku: Optional[str] = None
    product_description: Optional[str] = None
    quantity: float = Field(..., gt=0)
    unit: str
    unit_price: int = Field(..., ge=0, description="Price in cents")
    total_amount: int = Field(..., ge=0, description="Total in cents")
    currency: Optional[str] = "USD"
    specifications: Optional[dict] = None
    requested_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None


class OrderItemCreate(OrderItemBase):
    """Schema for creating order items"""
    pass


class OrderItemUpdate(BaseModel):
    """Schema for updating order items"""
    quantity: Optional[float] = Field(None, gt=0)
    unit_price: Optional[int] = Field(None, ge=0)
    total_amount: Optional[int] = Field(None, ge=0)
    requested_delivery_date: Optional[datetime] = None
    notes: Optional[str] = None
    supplier_notes: Optional[str] = None


class OrderItemResponse(OrderItemBase):
    """Schema for order item responses"""
    id: int
    order_id: int
    quantity_shipped: float = 0
    quantity_received: float = 0
    quantity_invoiced: float = 0
    supplier_notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    """Base schema for orders"""
    po_number: Optional[str] = None
    buyer_company_id: int
    supplier_company_id: int
    buyer_contact_id: Optional[int] = None
    supplier_contact_id: Optional[int] = None
    rfq_id: Optional[int] = None
    quote_id: Optional[int] = None
    
    subtotal: int = Field(..., ge=0, description="Subtotal in cents")
    tax_amount: Optional[int] = Field(0, ge=0, description="Tax in cents")
    shipping_amount: Optional[int] = Field(0, ge=0, description="Shipping in cents")
    discount_amount: Optional[int] = Field(0, ge=0, description="Discount in cents")
    total_amount: int = Field(..., ge=0, description="Total in cents")
    currency: Optional[str] = "USD"
    
    payment_terms: Optional[str] = None
    payment_method: Optional[str] = None
    payment_due_date: Optional[datetime] = None
    
    requested_delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None
    
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    special_requirements: Optional[str] = None


class OrderCreate(OrderBase):
    """Schema for creating orders"""
    items: List[OrderItemCreate] = Field(..., min_items=1)


class OrderUpdate(BaseModel):
    """Schema for updating orders"""
    po_number: Optional[str] = None
    payment_terms: Optional[str] = None
    payment_method: Optional[str] = None
    payment_due_date: Optional[datetime] = None
    
    requested_delivery_date: Optional[datetime] = None
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None
    shipping_method: Optional[str] = None
    
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    special_requirements: Optional[str] = None
    
    tax_amount: Optional[int] = Field(None, ge=0)
    shipping_amount: Optional[int] = Field(None, ge=0)
    discount_amount: Optional[int] = Field(None, ge=0)


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: OrderStatus
    reason: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Schema for order responses"""
    id: int
    order_number: str
    status: OrderStatus
    payment_status: PaymentStatus
    
    tracking_number: Optional[str] = None
    shipping_method: Optional[str] = None
    
    order_date: datetime
    confirmed_date: Optional[datetime] = None
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    cancelled_date: Optional[datetime] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Include relationships
    items: Optional[List[OrderItemResponse]] = None
    buyer_company: Optional[dict] = None
    supplier_company: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """Schema for order list responses (simplified)"""
    id: int
    order_number: str
    po_number: Optional[str] = None
    status: OrderStatus
    payment_status: PaymentStatus
    
    buyer_company_id: int
    supplier_company_id: int
    buyer_company_name: Optional[str] = None
    supplier_company_name: Optional[str] = None
    
    total_amount: int
    currency: str
    
    order_date: datetime
    requested_delivery_date: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class OrderStatusHistoryResponse(BaseModel):
    """Schema for order status history"""
    id: int
    order_id: int
    from_status: Optional[str] = None
    to_status: str
    changed_by_user_id: Optional[int] = None
    changed_by_name: Optional[str] = None
    changed_by_role: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)