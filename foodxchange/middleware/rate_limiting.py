"""
Rate Limiting Middleware for FoodXchange Platform
Provides protection against abuse and DoS attacks
"""

import time
import logging
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis
from foodxchange.config import get_settings

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation using Redis or in-memory storage"""
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client = None
        self.memory_storage = {}
        
        # Initialize Redis if available
        if self.settings.redis_url:
            try:
                self.redis_client = redis.from_url(self.settings.redis_url)
                self.redis_client.ping()
                logger.info("✅ Rate limiter using Redis")
            except Exception as e:
                logger.warning(f"Redis not available for rate limiting, using memory: {e}")
                self.redis_client = None
        else:
            logger.info("Rate limiter using in-memory storage")
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _get_user_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting"""
        # Try to get user ID from session
        user_id = request.session.get("user_id")
        if user_id:
            return f"user:{user_id}"
        
        # Fallback to IP address
        return f"ip:{self._get_client_ip(request)}"
    
    def _get_rate_limit_key(self, identifier: str, endpoint: str) -> str:
        """Generate Redis key for rate limiting"""
        return f"rate_limit:{identifier}:{endpoint}"
    
    def _check_rate_limit_redis(self, key: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """Check rate limit using Redis"""
        try:
            current_time = int(time.time())
            window_start = current_time - window
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window)
            
            results = pipe.execute()
            current_count = results[1]
            
            # Check if limit exceeded
            if current_count >= limit:
                return False, current_count, window
            
            return True, current_count + 1, window
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fallback to memory storage
            return self._check_rate_limit_memory(key, limit, window)
    
    def _check_rate_limit_memory(self, key: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """Check rate limit using in-memory storage"""
        current_time = time.time()
        
        if key not in self.memory_storage:
            self.memory_storage[key] = []
        
        # Remove old entries
        self.memory_storage[key] = [
            timestamp for timestamp in self.memory_storage[key]
            if current_time - timestamp < window
        ]
        
        current_count = len(self.memory_storage[key])
        
        # Check if limit exceeded
        if current_count >= limit:
            return False, current_count, window
        
        # Add current request
        self.memory_storage[key].append(current_time)
        
        return True, current_count + 1, window
    
    def check_rate_limit(self, request: Request, limit: int, window: int) -> Tuple[bool, int, int]:
        """Check if request is within rate limit"""
        identifier = self._get_user_identifier(request)
        endpoint = request.url.path
        key = self._get_rate_limit_key(identifier, endpoint)
        
        if self.redis_client:
            return self._check_rate_limit_redis(key, limit, window)
        else:
            return self._check_rate_limit_memory(key, limit, window)

# Global rate limiter instance
rate_limiter = RateLimiter()

# Rate limit configurations
RATE_LIMITS = {
    "default": {"limit": 100, "window": 3600},  # 100 requests per hour
    "auth": {"limit": 5, "window": 300},        # 5 login attempts per 5 minutes
    "search": {"limit": 50, "window": 300},     # 50 searches per 5 minutes
    "upload": {"limit": 10, "window": 3600},    # 10 uploads per hour
    "api": {"limit": 1000, "window": 3600},     # 1000 API calls per hour
}

def get_rate_limit_config(endpoint: str) -> Dict[str, int]:
    """Get rate limit configuration for endpoint"""
    if "auth" in endpoint or "login" in endpoint:
        return RATE_LIMITS["auth"]
    elif "search" in endpoint:
        return RATE_LIMITS["search"]
    elif "upload" in endpoint or "import" in endpoint:
        return RATE_LIMITS["upload"]
    elif "api" in endpoint:
        return RATE_LIMITS["api"]
    else:
        return RATE_LIMITS["default"]

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    try:
        # Get rate limit configuration
        config = get_rate_limit_config(request.url.path)
        limit = config["limit"]
        window = config["window"]
        
        # Check rate limit
        allowed, current_count, reset_window = rate_limiter.check_rate_limit(
            request, limit, window
        )
        
        if not allowed:
            # Rate limit exceeded
            retry_after = reset_window
            
            logger.warning(
                f"Rate limit exceeded for {request.url.path} - "
                f"IP: {rate_limiter._get_client_ip(request)}, "
                f"Count: {current_count}/{limit}"
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {limit} per {window} seconds",
                    "retry_after": retry_after,
                    "current_count": current_count,
                    "limit": limit
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        
        remaining = max(0, limit - current_count)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + window)
        
        return response
        
    except Exception as e:
        logger.error(f"Rate limiting middleware error: {e}")
        # Continue without rate limiting if there's an error
        return await call_next(request)

def rate_limit_decorator(limit: int, window: int):
    """Decorator for applying rate limiting to specific endpoints"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            allowed, current_count, reset_window = rate_limiter.check_rate_limit(
                request, limit, window
            )
            
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Limit: {limit} per {window} seconds"
                )
            
            return await func(request, *args, **kwargs)
        
        return wrapper
    return decorator 