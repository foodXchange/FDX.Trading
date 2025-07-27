# Basic Sentry middleware
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

class SentryMiddleware(BaseHTTPMiddleware):
    """Basic Sentry middleware for request tracking"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Sentry middleware caught error: {e}")
            raise

class SentryUserMiddleware(BaseHTTPMiddleware):
    """Basic Sentry user middleware"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response

def db_monitor():
    """Basic database monitoring function"""
    return {"status": "monitoring_disabled"} 