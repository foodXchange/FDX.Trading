import os
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from datetime import datetime

app = FastAPI()

# Health endpoints with HEAD support for Azure
@app.api_route("/health", methods=["GET", "HEAD"])
@app.api_route("/health/simple", methods=["GET", "HEAD"]) 
@app.api_route("/health/detailed", methods=["GET", "HEAD"])
@app.api_route("/health/advanced", methods=["GET", "HEAD"])
async def health(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200, headers={"content-length": "0"})
    return JSONResponse({"status": "healthy", "timestamp": datetime.now().isoformat()})

# Root endpoint with HEAD support
@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200, headers={"content-length": "0"})
    return JSONResponse({
        "message": "FoodXchange API",
        "version": "1.0.0", 
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("final_app:app", host="0.0.0.0", port=port)