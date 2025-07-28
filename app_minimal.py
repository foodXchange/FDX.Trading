import os
import sys
from datetime import datetime

# Simple WSGI application for Azure
def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')
    
    if path == '/health/simple' or path == '/health':
        status = '200 OK'
        headers = [('Content-Type', 'application/json')]
        start_response(status, headers)
        return [b'{"status": "ok", "timestamp": "' + datetime.utcnow().isoformat().encode() + b'"}']
    
    elif path == '/':
        status = '200 OK'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        return [b'<html><body><h1>FoodXchange API</h1><p>Status: Running</p></body></html>']
    
    else:
        status = '404 Not Found'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'Not Found']

# For local testing
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    port = int(os.environ.get('PORT', 8000))
    server = make_server('', port, application)
    print(f'Serving on port {port}...')
    server.serve_forever()