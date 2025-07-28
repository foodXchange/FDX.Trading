#!/usr/bin/env python3
"""
Hybrid startup script that tries FastAPI first, falls back to Flask
"""

import os
import sys
import subprocess

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def try_fastapi():
    """Try to start FastAPI with uvicorn"""
    try:
        port = os.environ.get("PORT", "8000")
        print(f"Attempting to start FastAPI on port {port}...")
        
        # Try importing to check if dependencies are available
        import uvicorn
        from foodxchange.main import app
        
        # If imports succeed, run uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(port), log_level="info")
        return True
        
    except ImportError as e:
        print(f"FastAPI startup failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error starting FastAPI: {e}")
        return False

def start_flask():
    """Fallback to Flask app"""
    try:
        print("Starting Flask fallback app...")
        port = os.environ.get("PORT", "8000")
        
        # Import and run the Flask app
        from app import app
        app.run(host="0.0.0.0", port=int(port))
        
    except Exception as e:
        print(f"Flask startup also failed: {e}")
        # Last resort - basic HTTP server
        start_basic_server()

def start_basic_server():
    """Ultra-basic HTTP server as last resort"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ['/', '/health', '/health/simple']:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "ok", "message": "Basic server running"}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
                
        def log_message(self, format, *args):
            return  # Suppress logs
    
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Starting basic HTTP server on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    # Try FastAPI first
    if not try_fastapi():
        # If FastAPI fails, fall back to Flask
        start_flask()