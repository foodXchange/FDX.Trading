from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import BaseSchema

class SupplierStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

class SupplierProductCreate(BaseModel):
    """Schema for creating a supplier product"""
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")
    unit_price: float = Field(..., gt=0, description="Unit price")
    currency: str = Field(default="USD", max_length=3, description="Currency code")
    min_order_quantity: Optional[int] = Field(None, ge=1, description="Minimum order quantity")
    lead_time_days: Optional[int] = Field(None, ge=0, description="Lead time in days")
    is_available: bool = Field(default=True, description="Product availability")

class SupplierProductUpdate(BaseModel):
    """Schema for updating a supplier product"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    category: Optional[str] = Field(None, min_length=1, max_length=100, description="Product category")
    unit_price: Optional[float] = Field(None, gt=0, description="Unit price")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    min_order_quantity: Optional[int] = Field(None, ge=1, description="Minimum order quantity")
    lead_time_days: Optional[int] = Field(None, ge=0, description="Lead time in days")
    is_available: Optional[bool] = Field(None, description="Product availability")

class SupplierProductResponse(BaseSchema):
    """Schema for supplier product response"""
    id: int
    supplier_id: int
    name: str
    description: Optional[str]
    category: str
    unit_price: float
    currency: str
    min_order_quantity: Optional[int]
    lead_time_days: Optional[int]
    is_available: bool
    created_at: datetime
    updated_at: datetime

class SupplierCertificationCreate(BaseModel):
    """Schema for creating a supplier certification"""
    name: str = Field(..., min_length=1, max_length=255, description="Certification name")
    issuing_body: str = Field(..., min_length=1, max_length=255, description="Issuing body")
    certificate_number: Optional[str] = Field(None, max_length=100, description="Certificate number")
    issue_date: Optional[datetime] = Field(None, description="Issue date")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")
    is_valid: bool = Field(default=True, description="Certification validity")

class SupplierCertificationUpdate(BaseModel):
    """Schema for updating a supplier certification"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Certification name")
    issuing_body: Optional[str] = Field(None, min_length=1, max_length=255, description="Issuing body")
    certificate_number: Optional[str] = Field(None, max_length=100, description="Certificate number")
    issue_date: Optional[datetime] = Field(None, description="Issue date")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")
    is_valid: Optional[bool] = Field(None, description="Certification validity")

class SupplierCertificationResponse(BaseSchema):
    """Schema for supplier certification response"""
    id: int
    supplier_id: int
    name: str
    issuing_body: str
    certificate_number: Optional[str]
    issue_date: Optional[datetime]
    expiry_date: Optional[datetime]
    is_valid: bool
    created_at: datetime
    updated_at: datetime

class SupplierCreate(BaseModel):
    """Schema for creating a new supplier"""
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    website: Optional[str] = Field(None, max_length=255, description="Company website")
    address: Optional[str] = Field(None, description="Company address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    categories: Optional[List[str]] = Field(default=[], description="Product categories")
    status: SupplierStatus = Field(default=SupplierStatus.PENDING, description="Supplier status")
    
    @validator('website')
    def validate_website(cls, v):
        """Validate website URL format"""
        if v and not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

class SupplierUpdate(BaseModel):
    """Schema for updating a supplier"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Company name")
    email: Optional[EmailStr] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, max_length=50, description="Contact phone")
    website: Optional[str] = Field(None, max_length=255, description="Company website")
    address: Optional[str] = Field(None, description="Company address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    country: Optional[str] = Field(None, max_length=100, description="Country")
    categories: Optional[List[str]] = Field(None, description="Product categories")
    status: Optional[SupplierStatus] = Field(None, description="Supplier status")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Supplier rating")
    response_rate: Optional[int] = Field(None, ge=0, le=100, description="Response rate percentage")
    average_response_time: Optional[float] = Field(None, ge=0, description="Average response time in hours")
    is_verified: Optional[bool] = Field(None, description="Verification status")
    compliance_notes: Optional[str] = Field(None, description="Compliance notes")

class SupplierResponse(BaseSchema):
    """Schema for supplier response"""
    id: int
    company_name: str
    email: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    address: Optional[str]
    city: Optional[str]
    country: Optional[str]
    categories: Optional[List[str]]
    status: SupplierStatus
    rating: Optional[float]
    response_rate: Optional[int]
    average_response_time: Optional[float]
    ai_enriched: Optional[bool]
    enrichment_data: Optional[Dict[str, Any]]
    last_enrichment: Optional[datetime]
    enrichment_confidence: Optional[float]
    is_verified: Optional[bool]
    verified_date: Optional[datetime]
    compliance_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    products: Optional[List[SupplierProductResponse]] = []
    certifications: Optional[List[SupplierCertificationResponse]] = []

class SupplierList(BaseSchema):
    """Schema for supplier list response"""
    id: int
    company_name: str
    email: Optional[str]
    city: Optional[str]
    country: Optional[str]
    categories: Optional[List[str]]
    status: SupplierStatus
    rating: Optional[float]
    response_rate: Optional[int]
    is_verified: Optional[bool]
    created_at: datetime

class SupplierSearch(BaseModel):
    """Schema for supplier search parameters"""
    query: Optional[str] = Field(None, description="Search query")
    categories: Optional[List[str]] = Field(None, description="Filter by categories")
    countries: Optional[List[str]] = Field(None, description="Filter by countries")
    status: Optional[SupplierStatus] = Field(None, description="Filter by status")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Minimum rating")
    verified_only: Optional[bool] = Field(None, description="Show only verified suppliers") 