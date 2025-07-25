#!/usr/bin/env python
"""
Production startup script for FoodXchange
Handles imports gracefully and provides fallback
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to start the full FastAPI app
try:
    logger.info("Attempting to import FastAPI app...")
    from app.main import app
    logger.info("FastAPI app imported successfully!")
    
    # Run with uvicorn
    if __name__ == "__main__":
        import uvicorn
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting FastAPI app on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
        
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.info("Falling back to simple WSGI app...")
    
    # Fallback to simple WSGI app
    def application(environ, start_response):
        path = environ.get('PATH_INFO', '/')
        
        if path == '/':
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [f"""
            <html>
            <head><title>FoodXchange</title></head>
            <body style="font-family: Arial; padding: 50px;">
                <h1>🍎 FoodXchange</h1>
                <p style="color: orange;">Running in fallback mode due to import error:</p>
                <pre style="background: #f0f0f0; padding: 10px;">{str(e)}</pre>
                <p>The application is running but some features may be limited.</p>
                <hr>
                <p><a href="/health">Health Check</a></p>
            </body>
            </html>
            """.encode()]
        
        elif path == '/health':
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [b'{"status": "healthy", "mode": "fallback"}']
        
        else:
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return [b'Not Found']
    
    # For gunicorn
    app = application
    
    # Run simple server if called directly
    if __name__ == "__main__":
        from wsgiref.simple_server import make_server
        port = int(os.environ.get("PORT", 8000))
        logger.info(f"Starting fallback server on port {port}")
        httpd = make_server('0.0.0.0', port, application)
        httpd.serve_forever()