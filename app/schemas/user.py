from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .base import BaseSchema

class UserRole(str, Enum):
    ADMIN = "admin"
    BUYER = "buyer"
    SUPPLIER = "supplier"
    COMPLIANCE = "compliance"
    VIEWER = "viewer"

class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    role: UserRole = Field(default=UserRole.BUYER, description="User role")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, min_length=2, max_length=255, description="Full name")
    role: Optional[UserRole] = Field(None, description="User role")
    department: Optional[str] = Field(None, max_length=100, description="Department")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    is_active: Optional[bool] = Field(None, description="Active status")
    preferences: Optional[dict] = Field(None, description="User preferences")

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

class UserResponse(BaseSchema):
    """Schema for user response (excluding sensitive data)"""
    id: int
    email: str
    full_name: str
    role: UserRole
    department: Optional[str]
    phone: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    preferences: Optional[dict]
    created_at: datetime
    updated_at: datetime

class UserList(BaseSchema):
    """Schema for user list response"""
    id: int
    email: str
    full_name: str
    role: UserRole
    department: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

class UserWithToken(BaseModel):
    """Schema for user with JWT token"""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
    expires_in: int 