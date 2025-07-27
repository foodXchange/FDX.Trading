#!/usr/bin/env python
"""
Simple FastAPI application for Azure deployment
"""
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import the main app
from app.main import app as main_app

# Create a simple wrapper app
app = FastAPI(title="FoodXchange", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include the main app routes
app.include_router(main_app)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Simple root endpoint"""
    return """
    <html>
        <head>
            <title>FoodXchange</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 50px; text-align: center; }
                h1 { color: #ff6b35; }
                .status { background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>🍎 FoodXchange</h1>
            <div class="status">
                <h2>✅ Application Running Successfully!</h2>
                <p>Azure deployment is working correctly.</p>
            </div>
            <p><a href="/health">Health Check</a> | <a href="/docs">API Documentation</a></p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "FoodXchange is running successfully"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 