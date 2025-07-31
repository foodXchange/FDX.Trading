"""
Pytest configuration and fixtures for FoodXchange tests
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient

# Set environment for testing
import os
os.environ["ENVIRONMENT"] = "testing"
os.environ["SECRET_KEY"] = "test-secret-key-for-jwt-tokens-minimum-32-chars"
os.environ["DEBUG"] = "True"

from foodxchange.main import app
from foodxchange.core.interfaces import CacheProvider, AIClient
from foodxchange.core.providers import InMemoryCacheProvider, AzureAIClient


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> TestClient:
    """Create test client for FastAPI app"""
    return TestClient(app)


@pytest.fixture
async def mock_cache_provider() -> AsyncGenerator[CacheProvider, None]:
    """Mock cache provider for testing"""
    cache = InMemoryCacheProvider(max_size=100)
    yield cache


@pytest.fixture
async def mock_ai_client() -> AsyncGenerator[AIClient, None]:
    """Mock AI client for testing"""
    mock_client = AsyncMock(spec=AIClient)
    
    # Setup default return values
    mock_client.analyze_product.return_value = {
        "product_name": "Test Product",
        "category": "Food & Beverage",
        "confidence": 0.95,
        "description": "Test product description",
        "nutritional_info": {
            "calories": 150,
            "protein": "5g",
            "carbs": "30g"
        }
    }
    
    mock_client.extract_text.return_value = "Sample extracted text"
    
    yield mock_client


@pytest.fixture
def mock_user_data():
    """Mock user data for testing"""
    return {
        "id": 1,
        "email": "test@foodxchange.com",
        "name": "Test User",
        "role": "user",
        "is_active": True,
        "is_admin": False,
        "permissions": ["read", "write"]
    }


@pytest.fixture
def admin_user_data():
    """Mock admin user data for testing"""
    return {
        "id": 1,
        "email": "admin@foodxchange.com",
        "name": "Admin User",
        "role": "admin",
        "is_active": True,
        "is_admin": True,
        "permissions": ["*"]
    }


@pytest.fixture
def sample_product_data():
    """Sample product data for testing"""
    return {
        "name": "Organic Tomatoes",
        "category": "Vegetables",
        "price": 2.99,
        "unit": "lb",
        "supplier_id": 1,
        "description": "Fresh organic tomatoes",
        "certifications": ["Organic", "Non-GMO"]
    }


@pytest.fixture
def sample_image_data():
    """Sample image data for testing"""
    # Simple 1x1 PNG image data
    return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'