from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema

class RFQStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    RECEIVING_QUOTES = "receiving_quotes"
    UNDER_REVIEW = "under_review"
    AWARDED = "awarded"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class RFQLineItemCreate(BaseModel):
    """Schema for creating an RFQ line item"""
    product_name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    quantity: int = Field(..., gt=0, description="Required quantity")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")
    estimated_unit_price: Optional[float] = Field(None, ge=0, description="Estimated unit price")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Technical specifications")
    delivery_requirements: Optional[str] = Field(None, description="Delivery requirements")

class RFQLineItemUpdate(BaseModel):
    """Schema for updating an RFQ line item"""
    product_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, min_length=1, max_length=100, description="Product category")
    quantity: Optional[int] = Field(None, gt=0, description="Required quantity")
    unit: Optional[str] = Field(None, min_length=1, max_length=50, description="Unit of measurement")
    estimated_unit_price: Optional[float] = Field(None, ge=0, description="Estimated unit price")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    specifications: Optional[Dict[str, Any]] = Field(None, description="Technical specifications")
    delivery_requirements: Optional[str] = Field(None, description="Delivery requirements")

class RFQLineItemResponse(BaseSchema):
    """Schema for RFQ line item response"""
    id: int
    rfq_id: int
    product_name: str
    description: Optional[str]
    category: str
    quantity: int
    unit: str
    estimated_unit_price: Optional[float]
    currency: str
    specifications: Optional[Dict[str, Any]]
    delivery_requirements: Optional[str]
    created_at: datetime
    updated_at: datetime

class RFQSupplierCreate(BaseModel):
    """Schema for adding a supplier to an RFQ"""
    supplier_id: int = Field(..., description="Supplier ID")
    invited_at: Optional[datetime] = Field(None, description="Invitation timestamp")
    responded_at: Optional[datetime] = Field(None, description="Response timestamp")
    status: str = Field(default="invited", description="Invitation status")

class RFQSupplierUpdate(BaseModel):
    """Schema for updating RFQ supplier status"""
    responded_at: Optional[datetime] = Field(None, description="Response timestamp")
    status: Optional[str] = Field(None, description="Invitation status")
    notes: Optional[str] = Field(None, description="Additional notes")

class RFQSupplierResponse(BaseSchema):
    """Schema for RFQ supplier response"""
    id: int
    rfq_id: int
    supplier_id: int
    supplier_company_name: str
    supplier_email: Optional[str]
    invited_at: Optional[datetime]
    responded_at: Optional[datetime]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

class RFQCreate(BaseModel):
    """Schema for creating a new RFQ"""
    title: str = Field(..., min_length=1, max_length=255, description="RFQ title")
    description: Optional[str] = Field(None, description="RFQ description")
    project_name: Optional[str] = Field(None, max_length=255, description="Project name")
    buyer_id: int = Field(..., description="Buyer ID")
    status: RFQStatus = Field(default=RFQStatus.DRAFT, description="RFQ status")
    submission_deadline: Optional[datetime] = Field(None, description="Submission deadline")
    delivery_deadline: Optional[datetime] = Field(None, description="Delivery deadline")
    budget_range_min: Optional[float] = Field(None, ge=0, description="Minimum budget")
    budget_range_max: Optional[float] = Field(None, ge=0, description="Maximum budget")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    delivery_location: Optional[str] = Field(None, description="Delivery location")
    special_requirements: Optional[str] = Field(None, description="Special requirements")
    terms_and_conditions: Optional[str] = Field(None, description="Terms and conditions")
    
    @validator('submission_deadline', 'delivery_deadline')
    def validate_deadlines(cls, v, values):
        """Validate deadline dates"""
        if v and 'submission_deadline' in values and 'delivery_deadline' in values:
            if values['submission_deadline'] and values['delivery_deadline']:
                if values['submission_deadline'] >= values['delivery_deadline']:
                    raise ValueError('Submission deadline must be before delivery deadline')
        return v
    
    @validator('budget_range_min', 'budget_range_max')
    def validate_budget_range(cls, v, values):
        """Validate budget range"""
        if 'budget_range_min' in values and 'budget_range_max' in values:
            min_budget = values.get('budget_range_min')
            max_budget = values.get('budget_range_max')
            if min_budget and max_budget and min_budget > max_budget:
                raise ValueError('Minimum budget cannot be greater than maximum budget')
        return v

class RFQUpdate(BaseModel):
    """Schema for updating an RFQ"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="RFQ title")
    description: Optional[str] = Field(None, description="RFQ description")
    project_name: Optional[str] = Field(None, max_length=255, description="Project name")
    status: Optional[RFQStatus] = Field(None, description="RFQ status")
    submission_deadline: Optional[datetime] = Field(None, description="Submission deadline")
    delivery_deadline: Optional[datetime] = Field(None, description="Delivery deadline")
    budget_range_min: Optional[float] = Field(None, ge=0, description="Minimum budget")
    budget_range_max: Optional[float] = Field(None, ge=0, description="Maximum budget")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    delivery_location: Optional[str] = Field(None, description="Delivery location")
    special_requirements: Optional[str] = Field(None, description="Special requirements")
    terms_and_conditions: Optional[str] = Field(None, description="Terms and conditions")
    awarded_supplier_id: Optional[int] = Field(None, description="Awarded supplier ID")
    awarded_amount: Optional[float] = Field(None, ge=0, description="Awarded amount")
    award_date: Optional[datetime] = Field(None, description="Award date")

class RFQResponse(BaseSchema):
    """Schema for RFQ response"""
    id: int
    title: str
    description: Optional[str]
    project_name: Optional[str]
    buyer_id: int
    buyer_name: str
    status: RFQStatus
    submission_deadline: Optional[datetime]
    delivery_deadline: Optional[datetime]
    budget_range_min: Optional[float]
    budget_range_max: Optional[float]
    currency: str
    delivery_location: Optional[str]
    special_requirements: Optional[str]
    terms_and_conditions: Optional[str]
    awarded_supplier_id: Optional[int]
    awarded_amount: Optional[float]
    award_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    line_items: Optional[List[RFQLineItemResponse]] = []
    suppliers: Optional[List[RFQSupplierResponse]] = []

class RFQList(BaseSchema):
    """Schema for RFQ list response"""
    id: int
    title: str
    project_name: Optional[str]
    buyer_name: str
    status: RFQStatus
    submission_deadline: Optional[datetime]
    delivery_deadline: Optional[datetime]
    budget_range_min: Optional[float]
    budget_range_max: Optional[float]
    currency: str
    awarded_supplier_id: Optional[int]
    awarded_amount: Optional[float]
    created_at: datetime

class RFQSearch(BaseModel):
    """Schema for RFQ search parameters"""
    query: Optional[str] = Field(None, description="Search query")
    status: Optional[RFQStatus] = Field(None, description="Filter by status")
    buyer_id: Optional[int] = Field(None, description="Filter by buyer")
    categories: Optional[List[str]] = Field(None, description="Filter by product categories")
    min_budget: Optional[float] = Field(None, ge=0, description="Minimum budget")
    max_budget: Optional[float] = Field(None, ge=0, description="Maximum budget")
    deadline_before: Optional[datetime] = Field(None, description="Deadline before date")
    deadline_after: Optional[datetime] = Field(None, description="Deadline after date") 