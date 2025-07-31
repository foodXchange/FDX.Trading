"""
Redis caching middleware for FoodXchange routes
Adds rate limiting and response caching to protect Azure API costs
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import json
import time
import logging
from typing import Callable

from ..services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware for caching responses and rate limiting
    """
    
    def __init__(self, app, rate_limit_enabled: bool = True, 
                 cache_enabled: bool = True, rate_limit_window: int = 60):
        super().__init__(app)
        self.rate_limit_enabled = rate_limit_enabled
        self.cache_enabled = cache_enabled
        self.rate_limit_window = rate_limit_window
        self.redis_service = get_redis_service()
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request with caching and rate limiting"""
        
        # Skip middleware if Redis is not connected
        if not self.redis_service.is_connected():
            return await call_next(request)
        
        # Extract user identifier (from session, IP, or auth)
        user_id = self._get_user_identifier(request)
        
        # Apply rate limiting for AI endpoints
        if self.rate_limit_enabled and self._is_ai_endpoint(request.url.path):
            rate_limit_result = self.redis_service.check_rate_limit(
                user_id=user_id,
                limit_type="ai_api_calls",
                max_requests=100,  # 100 requests per hour
                window_minutes=self.rate_limit_window
            )
            
            if not rate_limit_result["allowed"]:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": rate_limit_result["reason"],
                        "retry_after": rate_limit_result["retry_after"]
                    },
                    headers={
                        "X-RateLimit-Limit": str(rate_limit_result["limit"]),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + rate_limit_result["retry_after"])
                    }
                )
            
            # Add rate limit headers to response
            request.state.rate_limit_headers = {
                "X-RateLimit-Limit": str(rate_limit_result["limit"]),
                "X-RateLimit-Remaining": str(rate_limit_result["remaining"]),
                "X-RateLimit-Reset": str(int(time.time()) + self.rate_limit_window * 60)
            }
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers if available
        if hasattr(request.state, "rate_limit_headers"):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value
        
        return response
    
    def _get_user_identifier(self, request: Request) -> str:
        """Extract user identifier from request"""
        # Try to get from authentication
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Try to get from session
        session_id = request.cookies.get("session_id")
        if session_id:
            return f"session:{session_id}"
        
        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _is_ai_endpoint(self, path: str) -> bool:
        """Check if endpoint uses Azure AI services"""
        ai_endpoints = [
            "/api/product-analysis/analyze",
            "/api/product-analysis/generate-brief",
            "/api/data-import/ai-import",
            "/api/azure-testing",
        ]
        return any(path.startswith(endpoint) for endpoint in ai_endpoints)


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware for caching entire HTTP responses
    Useful for expensive operations that don't change frequently
    """
    
    def __init__(self, app, cache_ttl: int = 300):  # 5 minutes default
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.redis_service = get_redis_service()
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Cache GET responses for configured endpoints"""
        
        # Only cache GET requests
        if request.method != "GET" or not self.redis_service.is_connected():
            return await call_next(request)
        
        # Skip caching for certain paths
        if self._should_skip_cache(request.url.path):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Try to get from cache
        cached_response = self.redis_service.client.get(f"response_cache:{cache_key}")
        if cached_response:
            logger.info(f"Cache HIT for {request.url.path}")
            cached_data = json.loads(cached_response)
            return JSONResponse(
                content=cached_data["content"],
                status_code=cached_data["status_code"],
                headers=cached_data.get("headers", {})
            )
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200 and hasattr(response, "body"):
            try:
                # Read response body
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                # Cache the response
                cache_data = {
                    "content": json.loads(body.decode()),
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                }
                
                self.redis_service.client.setex(
                    f"response_cache:{cache_key}",
                    self.cache_ttl,
                    json.dumps(cache_data)
                )
                
                logger.info(f"Cached response for {request.url.path}")
                
                # Return new response with the body
                return JSONResponse(
                    content=cache_data["content"],
                    status_code=cache_data["status_code"],
                    headers=cache_data["headers"]
                )
                
            except Exception as e:
                logger.error(f"Failed to cache response: {e}")
        
        return response
    
    def _should_skip_cache(self, path: str) -> bool:
        """Determine if path should skip caching"""
        skip_paths = [
            "/api/auth",
            "/api/health",
            "/api/admin",
            "/static",
        ]
        return any(path.startswith(skip) for skip in skip_paths)
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate unique cache key for request"""
        # Include path and query parameters
        key_parts = [
            request.url.path,
            str(sorted(request.query_params.items()))
        ]
        
        # Include user ID if authenticated
        if hasattr(request.state, "user") and request.state.user:
            key_parts.append(f"user:{request.state.user.id}")
        
        return ":".join(key_parts)