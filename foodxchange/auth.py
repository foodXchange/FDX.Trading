"""
Authentication module for FoodXchange Platform
Provides JWT-based user authentication and authorization
"""

import logging
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .core.security import get_jwt_manager, JWTManager, TokenData
from .core.exceptions import AuthenticationError, AuthorizationError

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)


class User(BaseModel):
    """User model"""
    id: int
    email: str
    name: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    is_admin: bool = False
    permissions: list = []


class MockUser:
    """Mock user class for development/testing only"""
    def __init__(self, user_data: dict):
        self.id = user_data.get("id")
        self.email = user_data.get("email")
        self.name = user_data.get("name")
        self.role = user_data.get("role")
        self.is_active = user_data.get("is_active", False)
        self.is_admin = user_data.get("is_admin", False)
        self.permissions = user_data.get("permissions", [])


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> User:
    """
    Get current authenticated user from JWT token
    """
    # Check if we're in development mode
    if os.getenv("ENVIRONMENT", "production").lower() == "development":
        # Return mock admin user for development
        return MockUser({
            "id": 1,
            "email": "admin@fdx.trading",
            "name": "Development Admin",
            "role": "admin",
            "is_active": True,
            "is_admin": True,
            "permissions": ["*"]
        })
    
    if not credentials:
        raise AuthenticationError("Authentication credentials required")
    
    try:
        # Verify JWT token
        jwt_manager = get_jwt_manager()
        token_data = jwt_manager.verify_token(credentials.credentials)
        
        # In production, you would fetch user from database using token_data.user_id
        # For now, create user from token data
        user = User(
            id=token_data.user_id,
            email=token_data.email,
            role=token_data.role,
            is_admin=token_data.is_admin,
            is_active=True  # Would be fetched from database
        )
        
        return user
        
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise AuthenticationError("Invalid authentication credentials")

def get_current_active_user(current_user: MockUser = Depends(get_current_user)) -> MockUser:
    """
    Get current active user
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_admin(current_user: MockUser = Depends(get_current_active_user)) -> MockUser:
    """
    Require admin privileges
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user