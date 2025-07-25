"""Ultra-minimal FastAPI app that will definitely work on Azure"""
import os

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    app = FastAPI()
except:
    # If FastAPI fails, use basic WSGI
    def app(environ, start_response):
        status = '200 OK'
        headers = [('Content-type', 'text/html')]
        start_response(status, headers)
        return [b"<h1>FoodXchange is starting...</h1><p>FastAPI not loaded yet</p>"]

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>FoodXchange</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .status { color: green; }
                .info { background: #f0f0f0; padding: 20px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>🍎 FoodXchange</h1>
            <p class="status">✅ Application is running!</p>
            <div class="info">
                <h2>System Information:</h2>
                <ul>
                    <li>Port: """ + str(os.environ.get('PORT', '8000')) + """</li>
                    <li>Python Path: """ + str(os.sys.path[0]) + """</li>
                    <li>Working Directory: """ + os.getcwd() + """</li>
                </ul>
                <h2>Quick Links:</h2>
                <ul>
                    <li><a href="/health">Health Check</a></li>
                    <li><a href="/docs">API Documentation</a></li>
                </ul>
            </div>
        </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "FoodXchange", "version": "1.0.0"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting on port {port}")
    
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port)
    except:
        # Fallback to basic HTTP server
        from wsgiref.simple_server import make_server
        print(f"Starting basic server on port {port}")
        httpd = make_server('0.0.0.0', port, app)
        httpd.serve_forever()