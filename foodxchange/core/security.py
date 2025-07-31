"""
Security utilities for JWT tokens and password hashing
"""

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from pydantic import BaseModel

from .exceptions import AuthenticationError, AuthorizationError


class TokenData(BaseModel):
    """JWT token data structure"""
    user_id: int
    email: str
    role: str
    is_admin: bool = False
    exp: Optional[datetime] = None


class JWTManager:
    """JWT token management"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        if not secret_key or len(secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            raise AuthenticationError(f"Failed to create access token: {str(e)}")
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            raise AuthenticationError(f"Failed to create refresh token: {str(e)}")
    
    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                raise AuthenticationError("Invalid token type")
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                raise AuthenticationError("Token has expired")
            
            # Extract user data
            token_data = TokenData(
                user_id=payload.get("user_id"),
                email=payload.get("email"),
                role=payload.get("role", "user"),
                is_admin=payload.get("is_admin", False),
                exp=datetime.fromtimestamp(exp) if exp else None
            )
            
            return token_data
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.PyJWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Token verification failed: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        token_data = self.verify_token(refresh_token, token_type="refresh")
        
        # Create new access token
        new_token_data = {
            "user_id": token_data.user_id,
            "email": token_data.email,
            "role": token_data.role,
            "is_admin": token_data.is_admin
        }
        
        return self.create_access_token(new_token_data)


class PasswordManager:
    """Password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Generate salt and hash password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        if not password or not hashed_password:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special


def get_jwt_manager() -> JWTManager:
    """Get JWT manager instance with secret key from environment"""
    secret_key = os.getenv("SECRET_KEY")
    
    if not secret_key:
        raise ValueError("SECRET_KEY environment variable must be set")
    
    return JWTManager(secret_key)


def get_password_manager() -> PasswordManager:
    """Get password manager instance"""
    return PasswordManager()


# Rate limiting for authentication attempts
class AuthRateLimiter:
    """Rate limiter for authentication attempts"""
    
    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        self.attempts = {}  # In production, use Redis
    
    def is_rate_limited(self, identifier: str) -> bool:
        """Check if identifier is rate limited"""
        now = datetime.utcnow()
        
        if identifier not in self.attempts:
            return False
        
        # Clean old attempts
        cutoff = now - timedelta(minutes=self.window_minutes)
        self.attempts[identifier] = [
            attempt_time for attempt_time in self.attempts[identifier]
            if attempt_time > cutoff
        ]
        
        return len(self.attempts[identifier]) >= self.max_attempts
    
    def record_attempt(self, identifier: str):
        """Record authentication attempt"""
        now = datetime.utcnow()
        
        if identifier not in self.attempts:
            self.attempts[identifier] = []
        
        self.attempts[identifier].append(now)
    
    def clear_attempts(self, identifier: str):
        """Clear attempts for identifier (on successful auth)"""
        self.attempts.pop(identifier, None)