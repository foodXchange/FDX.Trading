"""
Custom static file serving with proper headers
"""

from fastapi import Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from typing import Optional
import mimetypes


class StaticFilesWithHeaders(StaticFiles):
    """Enhanced static file serving with proper cache and content-type headers"""
    
    # Define proper content types
    CONTENT_TYPES = {
        '.woff2': 'font/woff2',
        '.woff': 'font/woff',
        '.ttf': 'font/ttf',
        '.otf': 'font/otf',
        '.ico': 'image/x-icon',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp',
    }
    
    # Cache durations (in seconds)
    CACHE_DURATIONS = {
        # Fonts - very long cache
        '.woff2': 31536000,  # 1 year
        '.woff': 31536000,
        '.ttf': 31536000,
        '.otf': 31536000,
        # Images - long cache
        '.ico': 31536000,
        '.png': 2592000,   # 30 days
        '.jpg': 2592000,
        '.jpeg': 2592000,
        '.gif': 2592000,
        '.svg': 2592000,
        '.webp': 2592000,
        # CSS/JS - medium cache
        '.css': 86400,     # 1 day
        '.js': 86400,
        # Others - short cache
        '.json': 3600,     # 1 hour
    }
    
    async def get_response(self, path: str, scope) -> Response:
        """Override to add custom headers"""
        try:
            response = await super().get_response(path, scope)
        except Exception:
            # Return proper 404 for static files
            from starlette.responses import PlainTextResponse
            return PlainTextResponse("Not Found", status_code=404)
        
        # Handle 404 responses for static files
        if response.status_code == 404:
            from starlette.responses import PlainTextResponse
            return PlainTextResponse("Not Found", status_code=404)
        
        if response.status_code == 200:
            # Get file extension
            ext = None
            for possible_ext in self.CONTENT_TYPES:
                if path.endswith(possible_ext):
                    ext = possible_ext
                    break
            
            if ext:
                # Set proper content type
                content_type = self.CONTENT_TYPES.get(ext)
                if content_type:
                    # Remove charset for binary files
                    if ext in ['.woff2', '.woff', '.ttf', '.otf', '.ico', '.png', '.jpg', '.jpeg', '.gif', '.webp']:
                        response.headers['content-type'] = content_type
                    else:
                        response.headers['content-type'] = f'{content_type}; charset=utf-8'
                
                # Set cache headers
                cache_duration = self.CACHE_DURATIONS.get(ext, 3600)
                if cache_duration >= 31536000:  # 1 year or more
                    # Long-lived resources get immutable directive
                    response.headers['cache-control'] = f'public, max-age={cache_duration}, immutable'
                else:
                    response.headers['cache-control'] = f'public, max-age={cache_duration}'
                
                # Add security headers for static resources
                response.headers['x-content-type-options'] = 'nosniff'
                
                # Remove unnecessary headers
                # Use del instead of pop for MutableHeaders compatibility
                if 'x-xss-protection' in response.headers:
                    del response.headers['x-xss-protection']
                if 'content-security-policy' in response.headers:
                    del response.headers['content-security-policy']
                if 'expires' in response.headers:
                    del response.headers['expires']
            
        return response