#!/usr/bin/env python
"""
Minimal FastAPI application for Azure App Service startup
This version removes complex imports that might fail during startup
"""
import os
import logging
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create minimal FastAPI app
app = FastAPI(title="FoodXchange API - Minimal")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health endpoints that don't require database or complex imports
@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/health/simple")
async def health_simple():
    """Simple health check for basic uptime monitoring"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/health/advanced")
async def health_advanced():
    """Advanced health check with system information but no database"""
    try:
        # Try to get system info but don't fail if psutil is not available
        try:
            import psutil
            system_info = {
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "memory_percent": psutil.virtual_memory().percent,
            }
        except ImportError:
            system_info = {"status": "psutil not available"}
        
        response = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "FoodXchange",
            "version": "1.0.0",
            "environment": os.getenv('FLASK_ENV', 'production'),
            "system": system_info,
            "database": "not_checked",  # Skip database check for reliability
            "monitoring": {
                "sentry": "configured" if os.getenv('SENTRY_DSN') else "not_configured"
            }
        }
        return response
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/health/readiness")
async def health_readiness():
    """Kubernetes readiness probe endpoint"""
    return {"status": "ready", "timestamp": datetime.now().isoformat()}

@app.get("/health/liveness")
async def health_liveness():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "FoodXchange API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "health_advanced": "/health/advanced",
            "health_simple": "/health/simple"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all exceptions gracefully"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url.path)
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get('PORT', os.environ.get('HTTP_PLATFORM_PORT', '8000')))
    uvicorn.run(app, host="0.0.0.0", port=port)