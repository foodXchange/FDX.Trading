"""
Security headers middleware for FoodXchange
Adds important security headers to all responses
"""

from fastapi import Request
from fastapi.responses import Response
import logging

logger = logging.getLogger(__name__)


async def security_headers_middleware(request: Request, call_next):
    """
    Add security headers to all responses
    """
    response = await call_next(request)
    
    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable XSS filter in browsers
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Control referrer information
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Content Security Policy
    # Adjust based on your needs - this is a strict policy
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://fonts.googleapis.com",
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com",
        "img-src 'self' data: https:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'"
    ]
    response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
    
    # Strict Transport Security (only for HTTPS)
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Permissions Policy (formerly Feature Policy)
    permissions = [
        "accelerometer=()",
        "camera=()",
        "geolocation=()",
        "gyroscope=()",
        "magnetometer=()",
        "microphone=()",
        "payment=()",
        "usb=()"
    ]
    response.headers["Permissions-Policy"] = ", ".join(permissions)
    
    # Remove server header if present
    try:
        if "Server" in response.headers:
            del response.headers["Server"]
    except:
        pass  # Some response types don't support header deletion
    
    # Add custom security header
    response.headers["X-Security-Policy"] = "FoodXchange-Secure-v1"
    
    return response


def get_csp_nonce():
    """
    Generate a nonce for Content Security Policy
    Used for inline scripts/styles when needed
    """
    import secrets
    return secrets.token_urlsafe(16)