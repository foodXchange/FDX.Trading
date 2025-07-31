"""
Reusable decorators for FoodXchange
"""

import functools
import logging
import time
import asyncio
from typing import Callable, Any, Dict, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from .exceptions import (
    FoodXchangeError, ValidationError, AuthenticationError, 
    AuthorizationError, ResourceNotFoundError, ServiceUnavailableError,
    BusinessLogicError, DatabaseError, FileStorageError, AIServiceError,
    get_http_status_for_exception, create_http_exception
)
from .responses import APIResponse, APIError

logger = logging.getLogger(__name__)


def handle_service_errors(func: Callable) -> Callable:
    """Decorator to handle service-level errors consistently"""
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FoodXchangeError as e:
            logger.error(f"Service error in {func.__name__}: {e}")
            raise create_http_exception(e)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Internal server error in {func.__name__}"
            )
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FoodXchangeError as e:
            logger.error(f"Service error in {func.__name__}: {e}")
            raise create_http_exception(e)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, 
                detail=f"Internal server error in {func.__name__}"
            )
    
    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time"""
    
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed in {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def cache_result(ttl: int = 3600, key_func: Optional[Callable] = None):
    """Decorator to cache function results"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache (this would need cache provider injection)
            # For now, just execute the function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def validate_permissions(required_permissions: list):
    """Decorator to validate user permissions"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs or request
            user = None
            request = None
            
            for arg in args:
                if hasattr(arg, 'user'):
                    user = arg.user
                    break
                elif isinstance(arg, Request):
                    request = arg
                    break
            
            if 'current_user' in kwargs:
                user = kwargs['current_user']
            
            if not user:
                raise AuthenticationError("User authentication required")
            
            # Check permissions (mock implementation)
            if hasattr(user, 'permissions'):
                user_permissions = user.permissions
                if not all(perm in user_permissions for perm in required_permissions):
                    raise AuthorizationError(
                        f"Required permissions: {required_permissions}",
                        details={"required": required_permissions, "user_permissions": user_permissions}
                    )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def rate_limit(max_calls: int = 100, window_seconds: int = 3600):
    """Decorator to apply rate limiting"""
    
    def decorator(func: Callable) -> Callable:
        call_counts = {}
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user identifier
            user_id = "anonymous"
            
            for arg in args:
                if hasattr(arg, 'user') and hasattr(arg.user, 'id'):
                    user_id = str(arg.user.id)
                    break
            
            if 'current_user' in kwargs and hasattr(kwargs['current_user'], 'id'):
                user_id = str(kwargs['current_user'].id)
            
            # Simple in-memory rate limiting (should use Redis in production)
            now = time.time()
            if user_id not in call_counts:
                call_counts[user_id] = []
            
            # Clean old calls
            call_counts[user_id] = [
                call_time for call_time in call_counts[user_id] 
                if now - call_time < window_seconds
            ]
            
            # Check rate limit
            if len(call_counts[user_id]) >= max_calls:
                raise ServiceUnavailableError(
                    f"Rate limit exceeded: {max_calls} calls per {window_seconds} seconds"
                )
            
            # Record this call
            call_counts[user_id].append(now)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """Decorator to retry function on failure with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed for {func.__name__}")
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator