"""
Global error handlers for FastAPI application
"""

import logging
import traceback
from typing import Union
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from .exceptions import FoodXchangeError, get_http_status_for_exception
from .responses import APIResponse, APIError, ValidationErrorResponse, ValidationErrorDetail

logger = logging.getLogger(__name__)


def add_request_id_to_request(request: Request) -> str:
    """Add unique request ID to request state"""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    return request_id


async def foodxchange_exception_handler(request: Request, exc: FoodXchangeError) -> JSONResponse:
    """Handle custom FoodXchange exceptions"""
    request_id = getattr(request.state, 'request_id', None)
    
    logger.error(
        f"FoodXchange error: {exc.error_code} - {exc.message}",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    status_code = get_http_status_for_exception(exc)
    
    response = APIResponse.error_response(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response.dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> Union[JSONResponse, HTMLResponse]:
    """Handle FastAPI HTTP exceptions"""
    from fastapi.responses import HTMLResponse
    request_id = getattr(request.state, 'request_id', None)
    
    # Special handling for 401 on product-analysis page
    if (exc.status_code == 401 and 
        request.url.path == "/product-analysis/" and
        request.method == "GET"):
        
        accept_header = request.headers.get("accept", "")
        is_browser = "text/html" in accept_header or not accept_header.startswith("application/json")
        
        if is_browser:
            logger.info("Returning HTML redirect for unauthenticated product-analysis access")
            return HTMLResponse(content="""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Redirecting to Login...</title>
                <meta http-equiv="refresh" content="0; url=/login?next=/product-analysis/">
                <script>window.location.href = '/login?next=/product-analysis/';</script>
            </head>
            <body>
                <p>You need to be logged in to access this page. Redirecting to login...</p>
                <p>If you are not redirected, <a href="/login?next=/product-analysis/">click here</a>.</p>
            </body>
            </html>
            """, status_code=200)  # Use 200 to ensure browser processes the redirect
    
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Handle different detail formats
    if isinstance(exc.detail, dict):
        error_code = exc.detail.get('error_code', f'HTTP_{exc.status_code}')
        message = exc.detail.get('message', str(exc.detail))
        details = exc.detail.get('details')
    else:
        error_code = f'HTTP_{exc.status_code}'
        message = str(exc.detail)
        details = None
    
    response = APIResponse.error_response(
        error_code=error_code,
        message=message,
        details=details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.dict()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    request_id = getattr(request.state, 'request_id', None)
    
    logger.warning(
        f"Validation error: {len(exc.errors())} errors",
        extra={
            "request_id": request_id,
            "errors": exc.errors(),
            "path": request.url.path,
            "method": request.method
        }
    )
    
    # Convert Pydantic errors to our format
    validation_errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        validation_errors.append(
            ValidationErrorDetail(
                field=field,
                message=error["msg"],
                value=error.get("input", "")
            )
        )
    
    response = ValidationErrorResponse(
        errors=validation_errors,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=422,
        content=response.dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    request_id = getattr(request.state, 'request_id', None)
    
    logger.error(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        },
        exc_info=True
    )
    
    # Don't expose internal error details in production
    import os
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    
    if debug_mode:
        error_details = {
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc()
        }
        message = f"Internal server error: {str(exc)}"
    else:
        error_details = None
        message = "An internal server error occurred"
    
    response = APIResponse.error_response(
        error_code="INTERNAL_SERVER_ERROR",
        message=message,
        details=error_details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=500,
        content=response.dict()
    )


def setup_error_handlers(app: FastAPI) -> None:
    """Setup all error handlers for the FastAPI application"""
    
    # Custom FoodXchange exceptions
    app.add_exception_handler(FoodXchangeError, foodxchange_exception_handler)
    
    # FastAPI HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    
    # Validation errors
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Catch-all for unhandled exceptions
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Error handlers configured successfully")


# Middleware to add request ID to all requests
async def request_id_middleware(request: Request, call_next):
    """Middleware to add request ID to all requests"""
    request_id = add_request_id_to_request(request)
    
    # Add to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response