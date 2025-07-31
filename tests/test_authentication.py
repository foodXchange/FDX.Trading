"""
Tests for authentication system
"""

import pytest
from unittest.mock import patch
from fastapi import HTTPException

from foodxchange.core.security import JWTManager, PasswordManager, AuthRateLimiter
from foodxchange.core.exceptions import AuthenticationError
from foodxchange.auth import get_current_user


class TestJWTManager:
    """Test JWT token management"""
    
    def test_create_and_verify_access_token(self):
        """Test creating and verifying access tokens"""
        jwt_manager = JWTManager("test-secret-key-minimum-32-characters")
        
        # Create token
        data = {"user_id": 1, "email": "test@example.com", "role": "user"}
        token = jwt_manager.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token
        token_data = jwt_manager.verify_token(token)
        assert token_data.user_id == 1
        assert token_data.email == "test@example.com"
        assert token_data.role == "user"
    
    def test_invalid_token_raises_error(self):
        """Test that invalid tokens raise AuthenticationError"""
        jwt_manager = JWTManager("test-secret-key-minimum-32-characters")
        
        with pytest.raises(AuthenticationError):
            jwt_manager.verify_token("invalid-token")
    
    def test_secret_key_validation(self):
        """Test that short secret keys are rejected"""
        with pytest.raises(ValueError, match="SECRET_KEY must be at least 32 characters"):
            JWTManager("short-key")


class TestPasswordManager:
    """Test password hashing and verification"""
    
    def test_hash_and_verify_password(self):
        """Test password hashing and verification"""
        password = "TestPassword123!"
        
        # Hash password
        hashed = PasswordManager.hash_password(password)
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password
        
        # Verify correct password
        assert PasswordManager.verify_password(password, hashed) == True
        
        # Verify incorrect password
        assert PasswordManager.verify_password("wrong-password", hashed) == False
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        # Valid strong password
        assert PasswordManager.validate_password_strength("StrongP@ss123") == True
        
        # Too short
        assert PasswordManager.validate_password_strength("Sh0rt!") == False
        
        # Missing uppercase
        assert PasswordManager.validate_password_strength("weak@pass123") == False
        
        # Missing lowercase
        assert PasswordManager.validate_password_strength("WEAK@PASS123") == False
        
        # Missing digit
        assert PasswordManager.validate_password_strength("WeakP@ss") == False
        
        # Missing special character
        assert PasswordManager.validate_password_strength("WeakPass123") == False


class TestAuthRateLimiter:
    """Test authentication rate limiting"""
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        limiter = AuthRateLimiter(max_attempts=3, window_minutes=15)
        identifier = "test@example.com:192.168.1.1"
        
        # Should not be rate limited initially
        assert limiter.is_rate_limited(identifier) == False
        
        # Record attempts up to limit
        for _ in range(3):
            limiter.record_attempt(identifier)
        
        # Should be rate limited now
        assert limiter.is_rate_limited(identifier) == True
        
        # Clear attempts
        limiter.clear_attempts(identifier)
        assert limiter.is_rate_limited(identifier) == False


class TestAuthentication:
    """Test authentication functions"""
    
    @patch.dict('os.environ', {'ENVIRONMENT': 'development'})
    def test_get_current_user_development(self):
        """Test get_current_user in development mode"""
        user = get_current_user(None)
        
        assert user.email == "admin@foodxchange.com"
        assert user.is_admin == True
        assert user.role == "admin"
    
    @patch.dict('os.environ', {'ENVIRONMENT': 'production'})
    def test_get_current_user_production_no_credentials(self):
        """Test get_current_user in production without credentials"""
        with pytest.raises(AuthenticationError, match="Authentication credentials required"):
            get_current_user(None)
    
    def test_user_model_creation(self):
        """Test User model creation"""
        from foodxchange.auth import User
        
        user_data = {
            "id": 1,
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "is_admin": False
        }
        
        user = User(**user_data)
        assert user.id == 1
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.role == "user"
        assert user.is_admin == False
        assert user.is_active == True  # Default value