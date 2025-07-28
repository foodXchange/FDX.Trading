#!/usr/bin/env python3
"""
Minimal working application for Azure App Service health endpoint
Fixed version that should work with Azure's Python environment
"""
import os
import json
from datetime import datetime

def application(environ, start_response):
    """WSGI application entry point"""
    path = environ.get('PATH_INFO', '/')
    
    if path in ['/health/simple', '/health']:
        # Health endpoint
        response_data = {
            "status": "ok",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "FoodXchange API"
        }
        response_json = json.dumps(response_data)
        
        status = '200 OK'
        headers = [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(response_json)))
        ]
        start_response(status, headers)
        return [response_json.encode('utf-8')]
    
    elif path == '/':
        # Root endpoint
        html_content = """<!DOCTYPE html>
<html><head><title>FoodXchange</title></head>
<body><h1>FoodXchange API</h1><p>Status: Running</p></body></html>"""
        
        status = '200 OK'
        headers = [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(html_content)))
        ]
        start_response(status, headers)
        return [html_content.encode('utf-8')]
    
    else:
        # 404
        status = '404 Not Found'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'Not Found']

# For Azure - this is the main entry point
app = application

if __name__ == '__main__':
    # For local testing
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('PORT', 8000))
    print(f'Starting server on port {port}...')
    server = make_server('', port, application)
    server.serve_forever()