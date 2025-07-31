"""
Concrete implementations of core interfaces
"""

import redis.asyncio as redis
import json
import logging
from typing import Optional, Dict, Any, Generic, TypeVar
from .interfaces import CacheProvider, AIClient, FileStorageProvider
import aiofiles
import os
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RedisCacheProvider(CacheProvider):
    """Redis implementation of cache provider"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[redis.Redis] = None
    
    async def _get_redis(self) -> redis.Redis:
        """Get or create Redis connection"""
        if self._redis is None:
            self._redis = redis.from_url(self.redis_url, decode_responses=True)
        return self._redis
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis cache"""
        try:
            redis_client = await self._get_redis()
            return await redis_client.get(key)
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        """Set value in Redis cache with TTL"""
        try:
            redis_client = await self._get_redis()
            await redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
    
    async def delete(self, key: str) -> None:
        """Delete key from Redis cache"""
        try:
            redis_client = await self._get_redis()
            await redis_client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern"""
        try:
            redis_client = await self._get_redis()
            keys = await redis_client.keys(pattern)
            if keys:
                return await redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern {pattern}: {e}")
            return 0


class InMemoryCacheProvider(CacheProvider):
    """In-memory implementation for testing/development"""
    
    def __init__(self, max_size: int = 1000):
        from cachetools import TTLCache
        self._cache = TTLCache(maxsize=max_size, ttl=3600)
    
    async def get(self, key: str) -> Optional[str]:
        return self._cache.get(key)
    
    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        self._cache[key] = value
    
    async def delete(self, key: str) -> None:
        self._cache.pop(key, None)
    
    async def clear_pattern(self, pattern: str) -> int:
        # Simple pattern matching for in-memory cache
        import fnmatch
        keys_to_delete = [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]
        for key in keys_to_delete:
            del self._cache[key]
        return len(keys_to_delete)


class AzureAIClient(AIClient):
    """Azure AI Vision implementation"""
    
    def __init__(self, endpoint: str, api_key: str, deployment_name: str = "gpt-4"):
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment_name = deployment_name
    
    async def analyze_product(self, image_data: bytes, **kwargs) -> Dict[str, Any]:
        """Analyze product using Azure AI Vision"""
        try:
            # Mock implementation - replace with actual Azure AI Vision calls
            return {
                "product_name": "Sample Product",
                "category": "Food & Beverage",
                "confidence": 0.95,
                "description": "AI-generated product description",
                "nutritional_info": {
                    "calories": 150,
                    "protein": "5g",
                    "carbs": "30g"
                },
                "certifications": ["Organic", "Non-GMO"],
                "analysis_timestamp": "2024-01-01T12:00:00Z"
            }
        except Exception as e:
            logger.error(f"Error analyzing product: {e}")
            raise
    
    async def extract_text(self, image_data: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            # Mock implementation - replace with actual OCR calls
            return "Sample extracted text from image"
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise


class LocalFileStorageProvider(FileStorageProvider):
    """Local filesystem storage implementation"""
    
    def __init__(self, base_path: str = "uploads", base_url: str = "/static/uploads"):
        self.base_path = Path(base_path)
        self.base_url = base_url
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file_data: bytes, filename: str, folder: str = "") -> str:
        """Save file to local filesystem"""
        try:
            # Create unique filename to prevent conflicts
            file_ext = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Create folder path
            folder_path = self.base_path / folder if folder else self.base_path
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = folder_path / unique_filename
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_data)
            
            # Return relative path
            relative_path = file_path.relative_to(self.base_path)
            return str(relative_path)
            
        except Exception as e:
            logger.error(f"Error saving file {filename}: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from local filesystem"""
        try:
            full_path = self.base_path / file_path
            if full_path.exists():
                full_path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    async def get_file_url(self, file_path: str) -> str:
        """Get public URL for file"""
        return f"{self.base_url}/{file_path}"


class ServiceResult(Generic[T]):
    """Standard service result wrapper"""
    
    def __init__(self, data: Optional[T] = None, error: Optional[str] = None, success: Optional[bool] = None):
        self.data = data
        self.error = error
        self.success = success if success is not None else (error is None)
    
    @classmethod
    def success(cls, data: T) -> 'ServiceResult[T]':
        """Create successful result"""
        return cls(data=data, success=True)
    
    @classmethod
    def failure(cls, error: str) -> 'ServiceResult[T]':
        """Create failed result"""
        return cls(error=error, success=False)
    
    def is_success(self) -> bool:
        return self.success
    
    def is_failure(self) -> bool:
        return not self.success