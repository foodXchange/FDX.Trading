from fastapi import FastAPI, Request
from fastapi.responses import Response
from datetime import datetime
import os

app = FastAPI()

# Health endpoint with HEAD support for Azure
@app.api_route("/health", methods=["GET", "HEAD"])
async def health(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Root endpoint with HEAD support
@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"message": "FoodXchange API", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

# Middleware to handle any other HEAD requests
@app.middleware("http")
async def handle_head_requests(request: Request, call_next):
    if request.method == "HEAD":
        request._method = "GET"
        response = await call_next(request)
        if response.status_code < 400:
            response.body = b""
            response.headers["content-length"] = "0"
        return response
    return await call_next(request)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("minimal_app:app", host="0.0.0.0", port=port)