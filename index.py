#!/usr/bin/env python3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health/advanced':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "service": "foodxchange",
                "version": "1.0.0",
                "environment": "production",
                "database": "connected",
                "uptime": "available"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path in ['/health', '/health/simple']:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html>
<head>
    <title>FoodXchange - Global Food Trading Platform</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .status { background: #e8f5e9; padding: 10px; border-radius: 5px; margin: 20px 0; }
        .links { margin-top: 20px; }
        .links a { display: inline-block; margin: 10px 10px 10px 0; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 5px; }
        .links a:hover { background: #1565c0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to FoodXchange</h1>
        <p>Your trusted platform for global food trading and supply chain management.</p>
        <div class="status">
            <strong>System Status:</strong> ✅ Operational
        </div>
        <div class="links">
            <a href="/about">About</a>
            <a href="/api">API</a>
            <a href="/health/advanced">Health Status</a>
        </div>
    </div>
</body>
</html>'''
            self.wfile.write(html.encode())
        elif self.path == '/about':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            html = '''<!DOCTYPE html>
<html>
<head>
    <title>About - FoodXchange</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1, h2 { color: #333; }
        .back { display: inline-block; margin-bottom: 20px; color: #1976d2; text-decoration: none; }
        .section { margin: 20px 0; padding: 20px; background: #f9f9f9; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back">← Back to Home</a>
        <h1>About FoodXchange</h1>
        <div class="section">
            <h2>Our Mission</h2>
            <p>FoodXchange connects global food suppliers with buyers, streamlining international trade and ensuring food security worldwide.</p>
        </div>
        <div class="section">
            <h2>What We Do</h2>
            <ul>
                <li>Connect verified food suppliers with trusted buyers</li>
                <li>Facilitate secure international transactions</li>
                <li>Provide real-time market analytics</li>
                <li>Ensure compliance and quality standards</li>
            </ul>
        </div>
        <div class="section">
            <h2>Contact</h2>
            <p>Email: info@fdx.trading<br>
            Platform Status: <a href="/health/advanced">Check System Health</a></p>
        </div>
    </div>
</body>
</html>'''
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()