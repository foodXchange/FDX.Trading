"""
Authentication dependencies and middleware for FoodXchange
"""

from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from functools import wraps
import logging

from .security import get_jwt_manager, TokenData
from .exceptions import AuthenticationError

logger = logging.getLogger(__name__)


def get_current_user(request: Request) -> Optional[TokenData]:
    """
    Extract and verify JWT token from cookies
    Returns TokenData if valid, None otherwise
    """
    try:
        # Get token from cookie
        access_token = request.cookies.get("access_token")
        if not access_token:
            return None
        
        # Verify token
        jwt_manager = get_jwt_manager()
        token_data = jwt_manager.verify_token(access_token)
        return token_data
        
    except AuthenticationError as e:
        logger.warning(f"Authentication failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return None


def require_auth(func):
    """
    Decorator to require authentication for a route
    Redirects to login page if not authenticated
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            # Check if it's an API request
            if request.url.path.startswith("/api/"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            # For web pages, redirect to login
            return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
        
        # Add user to request state
        request.state.user = user
        return await func(request, *args, **kwargs)
    
    return wrapper


def require_admin(func):
    """
    Decorator to require admin role for a route
    """
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        user = get_current_user(request)
        if not user:
            if request.url.path.startswith("/api/"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
        
        if not user.is_admin:
            if request.url.path.startswith("/api/"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            return RedirectResponse(url="/dashboard?error=unauthorized", status_code=303)
        
        request.state.user = user
        return await func(request, *args, **kwargs)
    
    return wrapper


def require_role(allowed_roles: list):
    """
    Decorator to require specific roles for a route
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user(request)
            if not user:
                if request.url.path.startswith("/api/"):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                return RedirectResponse(url="/login?error=not_authenticated", status_code=303)
            
            if user.role not in allowed_roles and not user.is_admin:
                if request.url.path.startswith("/api/"):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Access denied. Required roles: {', '.join(allowed_roles)}"
                    )
                return RedirectResponse(url="/dashboard?error=unauthorized", status_code=303)
            
            request.state.user = user
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator


class AuthMiddleware:
    """
    Middleware to add user info to all requests
    """
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Create a Request object to access cookies
            from starlette.requests import Request as StarletteRequest
            request = StarletteRequest(scope, receive)
            
            # Get current user
            user = get_current_user(request)
            
            # Add user to scope
            scope["user"] = user
        
        await self.app(scope, receive, send)