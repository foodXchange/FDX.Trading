"""
Authentication module for FoodXchange Platform
Provides user authentication and authorization functionality
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# Mock user data for development
MOCK_USERS = {
    "admin@foodxchange.com": {
        "id": 1,
        "email": "admin@foodxchange.com",
        "name": "Admin User",
        "role": "admin",
        "is_active": True,
        "is_admin": True
    },
    "user@foodxchange.com": {
        "id": 2,
        "email": "user@foodxchange.com",
        "name": "Regular User",
        "role": "user",
        "is_active": True,
        "is_admin": False
    }
}

# Security scheme
security = HTTPBearer(auto_error=False)

class MockUser:
    """Mock user class for development"""
    def __init__(self, user_data: dict):
        self.id = user_data.get("id")
        self.email = user_data.get("email")
        self.name = user_data.get("name")
        self.role = user_data.get("role")
        self.is_active = user_data.get("is_active", False)
        self.is_admin = user_data.get("is_admin", False)

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> MockUser:
    """
    Get current authenticated user
    For development, returns a mock admin user
    """
    # In production, this would validate JWT tokens or session data
    # For now, return a mock admin user
    mock_user_data = MOCK_USERS["admin@foodxchange.com"]
    return MockUser(mock_user_data)

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