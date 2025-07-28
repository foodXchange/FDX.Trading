from fastapi import FastAPI, Request
from fastapi.responses import Response
from datetime import datetime
import os

app = FastAPI()

# Main health endpoint with HEAD support
@app.api_route("/health", methods=["GET", "HEAD"])
async def health(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Alternative health endpoints Azure might check
@app.api_route("/health/simple", methods=["GET", "HEAD"])
async def health_simple(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "ok"}

@app.api_route("/health/detailed", methods=["GET", "HEAD"])
async def health_detailed(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "foodxchange",
        "version": "1.0.0"
    }

@app.api_route("/health/advanced", methods=["GET", "HEAD"])
async def health_advanced(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "operational",
            "database": "not_configured",
            "cache": "not_configured"
        }
    }

# Root endpoint with HEAD support
@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {
        "message": "FoodXchange API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

# Middleware to handle HEAD requests for any GET endpoint
@app.middleware("http")
async def handle_head_requests(request: Request, call_next):
    # If it's a HEAD request and we don't have a specific handler
    if request.method == "HEAD":
        # Check if there's a corresponding GET endpoint
        request._method = "GET"
        response = await call_next(request)
        # If successful, return empty body for HEAD
        if response.status_code < 400:
            response.body = b""
            response.headers["content-length"] = "0"
        return response
    return await call_next(request)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)