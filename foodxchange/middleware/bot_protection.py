"""
Bot protection middleware to block common bot patterns
"""
from fastapi import Request
from fastapi.responses import JSONResponse
import re

# Common bot patterns to block
BOT_PATTERNS = [
    r'\.php$',
    r'wp-admin',
    r'wp-content',
    r'wp-includes',
    r'wordpress',
    r'\.asp$',
    r'\.aspx$',
    r'phpmyadmin',
    r'\.env',
    r'\.git',
    r'\.svn',
    r'\.htaccess',
    r'\.htpasswd',
    r'\.ini$',
    r'\.log$',
    r'\.bak$',
    r'\.backup$',
    r'\.sql$',
    r'\.zip$',
    r'\.tar\.gz$',
    r'administrator',
    r'admin\.php',
    r'login\.php',
]

async def bot_protection_middleware(request: Request, call_next):
    """Block common bot/scanner requests"""
    path = request.url.path.lower()
    
    # Check if path matches any bot pattern
    for pattern in BOT_PATTERNS:
        if re.search(pattern, path, re.IGNORECASE):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not found"}
            )
    
    # Continue with normal request processing
    response = await call_next(request)
    return response