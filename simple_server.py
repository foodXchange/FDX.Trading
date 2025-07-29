#!/usr/bin/env python3
"""
Simple HTTP server for testing
"""
import http.server
import socketserver

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>FoodXchange Test Server</title>
            </head>
            <body>
                <h1>FoodXchange Server is Running!</h1>
                <p>If you can see this, the server is working on port 8080.</p>
                <a href="/admin">Go to Admin Dashboard</a>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        elif self.path == '/admin':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Admin Dashboard</title>
            </head>
            <body>
                <h1>Admin Dashboard</h1>
                <p>Welcome to the admin area!</p>
                <a href="/">Back to Home</a>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        else:
            super().do_GET()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"Admin access: http://localhost:{PORT}/admin")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()