"""
Custom exceptions and error handling for FoodXchange
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException


class FoodXchangeError(Exception):
    """Base exception for FoodXchange application"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(FoodXchangeError):
    """Raised when input validation fails"""
    pass


class AuthenticationError(FoodXchangeError):
    """Raised when authentication fails"""
    pass


class AuthorizationError(FoodXchangeError):
    """Raised when authorization fails"""
    pass


class ResourceNotFoundError(FoodXchangeError):
    """Raised when a requested resource is not found"""
    pass


class ServiceUnavailableError(FoodXchangeError):
    """Raised when an external service is unavailable"""
    pass


class BusinessLogicError(FoodXchangeError):
    """Raised when business logic validation fails"""
    pass


class DatabaseError(FoodXchangeError):
    """Raised when database operations fail"""
    pass


class FileStorageError(FoodXchangeError):
    """Raised when file storage operations fail"""
    pass


class AIServiceError(FoodXchangeError):
    """Raised when AI services fail"""
    pass


class CacheError(FoodXchangeError):
    """Raised when cache operations fail"""
    pass


# HTTP Exception mapping
EXCEPTION_TO_HTTP_STATUS = {
    ValidationError: 400,
    AuthenticationError: 401,
    AuthorizationError: 403,
    ResourceNotFoundError: 404,
    BusinessLogicError: 422,
    ServiceUnavailableError: 503,
    DatabaseError: 500,
    FileStorageError: 500,
    AIServiceError: 502,
    CacheError: 500,
    FoodXchangeError: 500,
}


def get_http_status_for_exception(exc: Exception) -> int:
    """Get appropriate HTTP status code for exception"""
    for exc_type, status_code in EXCEPTION_TO_HTTP_STATUS.items():
        if isinstance(exc, exc_type):
            return status_code
    return 500


def create_http_exception(exc: FoodXchangeError) -> HTTPException:
    """Convert FoodXchange exception to HTTP exception"""
    status_code = get_http_status_for_exception(exc)
    
    detail = {
        "error_code": exc.error_code,
        "message": exc.message,
        "details": exc.details
    }
    
    return HTTPException(status_code=status_code, detail=detail)