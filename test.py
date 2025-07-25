#!/usr/bin/env python
"""Ultra simple test - just print and exit"""
import os
import sys

print("=== FoodXchange Test Script ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')[:10]}")
print(f"PORT: {os.environ.get('PORT', 'NOT SET')}")
print("=== Test Complete ===")

# Create a simple HTTP server on the PORT
port = int(os.environ.get('PORT', 8000))
print(f"\nStarting HTTP server on port {port}...")

from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"FoodXchange Test Server Running!")

httpd = HTTPServer(('0.0.0.0', port), SimpleHandler)
print(f"Server running on http://0.0.0.0:{port}")
httpd.serve_forever()