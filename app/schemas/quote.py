from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema

class QuoteStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    NEGOTIATING = "negotiating"
    EXPIRED = "expired"

class QuoteItemCreate(BaseModel):
    """Schema for creating a quote item"""
    rfq_line_item_id: int = Field(..., description="RFQ line item ID")
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    quantity: int = Field(..., gt=0, description="Offered quantity")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")
    unit_price: float = Field(..., gt=0, description="Unit price")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    total_price: Optional[float] = Field(None, ge=0, description="Total price for this item")
    lead_time_days: Optional[int] = Field(None, ge=0, description="Lead time in days")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Product specifications")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @validator('total_price', pre=True, always=True)
    def calculate_total_price(cls, v, values):
        """Calculate total price if not provided"""
        if v is None and 'quantity' in values and 'unit_price' in values:
            return values['quantity'] * values['unit_price']
        return v

class QuoteItemUpdate(BaseModel):
    """Schema for updating a quote item"""
    product_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    quantity: Optional[int] = Field(None, gt=0, description="Offered quantity")
    unit: Optional[str] = Field(None, min_length=1, max_length=50, description="Unit of measurement")
    unit_price: Optional[float] = Field(None, gt=0, description="Unit price")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    total_price: Optional[float] = Field(None, ge=0, description="Total price for this item")
    lead_time_days: Optional[int] = Field(None, ge=0, description="Lead time in days")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Product specifications")
    notes: Optional[str] = Field(None, description="Additional notes")

class QuoteItemResponse(BaseSchema):
    """Schema for quote item response"""
    id: int
    quote_id: int
    rfq_line_item_id: int
    product_name: str
    description: Optional[str]
    quantity: int
    unit: str
    unit_price: float
    currency: str
    total_price: float
    lead_time_days: Optional[int]
    specifications: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class QuoteCreate(BaseModel):
    """Schema for creating a new quote"""
    rfq_id: int = Field(..., description="RFQ ID")
    supplier_id: int = Field(..., description="Supplier ID")
    status: QuoteStatus = Field(default=QuoteStatus.DRAFT, description="Quote status")
    total_amount: Optional[float] = Field(None, ge=0, description="Total quote amount")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    valid_until: Optional[datetime] = Field(None, description="Quote validity period")
    delivery_time_days: Optional[int] = Field(None, ge=0, description="Total delivery time in days")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    delivery_terms: Optional[str] = Field(None, description="Delivery terms")
    warranty_terms: Optional[str] = Field(None, description="Warranty terms")
    additional_notes: Optional[str] = Field(None, description="Additional notes")
    attachments: Optional[List[str]] = Field(default=[], description="Attachment file names")
    
    @validator('total_amount', pre=True, always=True)
    def calculate_total_amount(cls, v, values):
        """Calculate total amount from items if not provided"""
        if v is None and 'items' in values:
            return sum(item.get('total_price', 0) for item in values['items'])
        return v

class QuoteUpdate(BaseModel):
    """Schema for updating a quote"""
    status: Optional[QuoteStatus] = Field(None, description="Quote status")
    total_amount: Optional[float] = Field(None, ge=0, description="Total quote amount")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    valid_until: Optional[datetime] = Field(None, description="Quote validity period")
    delivery_time_days: Optional[int] = Field(None, ge=0, description="Total delivery time in days")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    delivery_terms: Optional[str] = Field(None, description="Delivery terms")
    warranty_terms: Optional[str] = Field(None, description="Warranty terms")
    additional_notes: Optional[str] = Field(None, description="Additional notes")
    attachments: Optional[List[str]] = Field(None, description="Attachment file names")
    buyer_notes: Optional[str] = Field(None, description="Buyer notes")
    evaluation_score: Optional[float] = Field(None, ge=0, le=100, description="Evaluation score")
    evaluation_notes: Optional[str] = Field(None, description="Evaluation notes")

class QuoteResponse(BaseSchema):
    """Schema for quote response"""
    id: int
    rfq_id: int
    rfq_title: str
    supplier_id: int
    supplier_company_name: str
    supplier_email: Optional[str]
    status: QuoteStatus
    total_amount: float
    currency: str
    valid_until: Optional[datetime]
    delivery_time_days: Optional[int]
    payment_terms: Optional[str]
    delivery_terms: Optional[str]
    warranty_terms: Optional[str]
    additional_notes: Optional[str]
    attachments: Optional[List[str]]
    buyer_notes: Optional[str]
    evaluation_score: Optional[float]
    evaluation_notes: Optional[str]
    submitted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    items: Optional[List[QuoteItemResponse]] = []

class QuoteList(BaseSchema):
    """Schema for quote list response"""
    id: int
    rfq_id: int
    rfq_title: str
    supplier_company_name: str
    status: QuoteStatus
    total_amount: float
    currency: str
    valid_until: Optional[datetime]
    delivery_time_days: Optional[int]
    evaluation_score: Optional[float]
    submitted_at: Optional[datetime]
    created_at: datetime

class QuoteComparison(BaseModel):
    """Schema for quote comparison"""
    rfq_id: int
    rfq_title: str
    quotes: List[QuoteResponse]
    comparison_metrics: Dict[str, Any]

class QuoteSearch(BaseModel):
    """Schema for quote search parameters"""
    query: Optional[str] = Field(None, description="Search query")
    rfq_id: Optional[int] = Field(None, description="Filter by RFQ")
    supplier_id: Optional[int] = Field(None, description="Filter by supplier")
    status: Optional[QuoteStatus] = Field(None, description="Filter by status")
    min_amount: Optional[float] = Field(None, ge=0, description="Minimum amount")
    max_amount: Optional[float] = Field(None, ge=0, description="Maximum amount")
    currency: Optional[str] = Field(None, description="Filter by currency")
    valid_after: Optional[datetime] = Field(None, description="Valid after date")
    valid_before: Optional[datetime] = Field(None, description="Valid before date")
    submitted_after: Optional[datetime] = Field(None, description="Submitted after date")
    submitted_before: Optional[datetime] = Field(None, description="Submitted before date") 