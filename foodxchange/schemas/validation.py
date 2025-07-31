"""
Input validation schemas for FoodXchange Platform
Provides Pydantic models for validating all API inputs
"""

from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
import re
from datetime import datetime

class UserUpdateRequest(BaseModel):
    """Schema for user profile updates"""
    name: str = Field(..., min_length=2, max_length=255, description="User's full name")
    email: EmailStr = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")
    country: Optional[str] = Field(None, max_length=100, description="User's country")
    city: Optional[str] = Field(None, max_length=100, description="User's city")
    address: Optional[str] = Field(None, max_length=500, description="User's address")
    bio: Optional[str] = Field(None, max_length=1000, description="User's bio")
    job_title: Optional[str] = Field(None, max_length=100, description="User's job title")
    department: Optional[str] = Field(None, max_length=100, description="User's department")
    industry: Optional[str] = Field(None, max_length=100, description="User's industry")
    company_size: Optional[str] = Field(None, max_length=50, description="Company size")
    website: Optional[str] = Field(None, max_length=255, description="User's website")
    linkedin: Optional[str] = Field(None, max_length=255, description="LinkedIn profile")
    timezone: Optional[str] = Field(None, max_length=50, description="User's timezone")
    language: Optional[str] = Field(None, max_length=10, description="User's language")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('phone')
    def validate_phone(cls, v):
        if v:
            # Remove all non-digit characters
            digits_only = re.sub(r'\D', '', v)
            if len(digits_only) < 10:
                raise ValueError('Phone number must have at least 10 digits')
        return v

    @validator('website')
    def validate_website(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

    @validator('linkedin')
    def validate_linkedin(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v

class PasswordChangeRequest(BaseModel):
    """Schema for password change requests"""
    current_password: str = Field(..., min_length=1, description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., min_length=8, description="Password confirmation")

    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        # Check for at least one digit
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v

    @validator('confirm_password')
    def validate_password_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class LoginRequest(BaseModel):
    """Schema for login requests"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")

    @validator('email')
    def validate_email(cls, v):
        if not v or not v.strip():
            raise ValueError('Email cannot be empty')
        return v.strip().lower()

class SearchRequest(BaseModel):
    """Schema for search requests"""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    filters: Optional[List[dict]] = Field(default=[], description="Search filters")
    categories: Optional[List[str]] = Field(default=[], description="Search categories")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of results")

    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Search query cannot be empty')
        return v.strip()

class FileUploadRequest(BaseModel):
    """Schema for file upload requests"""
    filename: str = Field(..., description="File name")
    content_type: str = Field(..., description="File content type")
    size: int = Field(..., ge=1, le=10*1024*1024, description="File size in bytes")  # 10MB max

    @validator('filename')
    def validate_filename(cls, v):
        # Check for dangerous file extensions
        dangerous_extensions = {'.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js'}
        file_ext = v.lower().split('.')[-1] if '.' in v else ''
        if f'.{file_ext}' in dangerous_extensions:
            raise ValueError('File type not allowed')
        return v

    @validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain', 'text/csv'
        }
        if v not in allowed_types:
            raise ValueError('Content type not allowed')
        return v

class SupplierCreateRequest(BaseModel):
    """Schema for supplier creation"""
    name: str = Field(..., min_length=2, max_length=255, description="Supplier name")
    description: Optional[str] = Field(None, max_length=1000, description="Supplier description")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    specializations: Optional[List[str]] = Field(default=[], description="Specializations")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    certifications: Optional[List[str]] = Field(default=[], description="Certifications")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    website: Optional[str] = Field(None, max_length=255, description="Website")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Supplier name cannot be empty')
        return v.strip()

class BuyerCreateRequest(BaseModel):
    """Schema for buyer creation"""
    name: str = Field(..., min_length=2, max_length=255, description="Buyer name")
    description: Optional[str] = Field(None, max_length=1000, description="Buyer description")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    requirements: Optional[List[str]] = Field(default=[], description="Requirements")
    location: Optional[str] = Field(None, max_length=100, description="Location")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    website: Optional[str] = Field(None, max_length=255, description="Website")

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Buyer name cannot be empty')
        return v.strip()

class ProjectCreateRequest(BaseModel):
    """Schema for project creation"""
    title: str = Field(..., min_length=2, max_length=255, description="Project title")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    requirements: Optional[List[str]] = Field(default=[], description="Project requirements")
    budget_range: Optional[str] = Field(None, max_length=100, description="Budget range")
    deadline: Optional[datetime] = Field(None, description="Project deadline")
    location: Optional[str] = Field(None, max_length=100, description="Project location")
    category: Optional[str] = Field(None, max_length=100, description="Project category")

    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Project title cannot be empty')
        return v.strip()

    @validator('deadline')
    def validate_deadline(cls, v):
        if v and v < datetime.now():
            raise ValueError('Deadline cannot be in the past')
        return v 