#!/usr/bin/env python3
"""
Ultra-minimal Azure App Service entry point
No dependencies except standard library
"""
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "FoodXchange API is running",
                "path": self.path,
                "python_version": sys.version
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logs"""
        pass

def main():
    """Start the server"""
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Starting minimal server on port {port}")
    server.serve_forever()

if __name__ == '__main__':
    main()