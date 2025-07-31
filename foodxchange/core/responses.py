"""
Standardized API responses for FoodXchange
"""

from typing import Generic, TypeVar, Optional, Any, Dict, List
from pydantic import BaseModel
import uuid
from datetime import datetime

T = TypeVar('T')


class APIError(BaseModel):
    """Standard API error response"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = datetime.utcnow().isoformat()
    request_id: Optional[str] = None


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool
    data: Optional[T] = None
    error: Optional[APIError] = None
    message: Optional[str] = None
    timestamp: str = datetime.utcnow().isoformat()
    request_id: Optional[str] = None
    
    @classmethod
    def success_response(
        cls, 
        data: T, 
        message: Optional[str] = None, 
        request_id: Optional[str] = None
    ) -> 'APIResponse[T]':
        """Create successful response"""
        return cls(
            success=True,
            data=data,
            message=message,
            request_id=request_id or str(uuid.uuid4())
        )
    
    @classmethod
    def error_response(
        cls,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> 'APIResponse[None]':
        """Create error response"""
        return cls(
            success=False,
            error=APIError(
                error_code=error_code,
                message=message,
                details=details,
                request_id=request_id or str(uuid.uuid4())
            ),
            request_id=request_id or str(uuid.uuid4())
        )


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool


class PaginatedAPIResponse(BaseModel, Generic[T]):
    """Paginated API response"""
    success: bool = True
    data: List[T]
    meta: PaginationMeta
    message: Optional[str] = None
    timestamp: str = datetime.utcnow().isoformat()
    request_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        per_page: int,
        message: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> 'PaginatedAPIResponse[T]':
        """Create paginated response"""
        total_pages = (total + per_page - 1) // per_page
        
        return cls(
            data=items,
            meta=PaginationMeta(
                page=page,
                per_page=per_page,
                total=total,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_prev=page > 1
            ),
            message=message,
            request_id=request_id or str(uuid.uuid4())
        )


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str = datetime.utcnow().isoformat()
    version: str = "1.0.0"
    services: Dict[str, Any] = {}
    uptime: Optional[str] = None


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    field: str
    message: str
    value: Any


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    success: bool = False
    error_code: str = "VALIDATION_ERROR"
    message: str = "Request validation failed"
    errors: List[ValidationErrorDetail]
    timestamp: str = datetime.utcnow().isoformat()
    request_id: Optional[str] = None