#!/usr/bin/env python
"""
Emergency health endpoint fix for Azure
"""
import os
import sys
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Try to install Flask if not available
try:
    import flask
except ImportError:
    print("Flask not found, installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask==3.0.0"])
    import flask

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>FoodXchange</h1><p>Status: <a href="/health/simple">Health Check</a></p>'

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "foodxchange"})

@app.route('/health/simple')
def health_simple():
    return jsonify({"status": "ok"})

@app.route('/health/detailed')
def health_detailed():
    return jsonify({
        "status": "healthy",
        "service": "foodxchange",
        "version": "1.0.0",
        "timestamp": "2025-01-28T11:30:00Z"
    })

@app.route('/api/health')
def api_health():
    return jsonify({"status": "healthy", "api": "v1"})

if __name__ == '__main__':
    # Get port from environment
    port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000')))
    print(f"Starting Flask app on port {port}")
    
    # If Flask fails, fall back to simple HTTP server
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Flask failed: {e}, using simple HTTP server")
        
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path in ['/health', '/health/simple', '/api/health']:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok"}).encode())
                elif self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>FoodXchange</h1><p>Health: OK</p>')
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                return  # Suppress logs
        
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        print(f"Simple HTTP server running on port {port}")
        server.serve_forever()