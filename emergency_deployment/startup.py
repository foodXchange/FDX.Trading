import os
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "FoodXchange is running",
        "status": "online",
        "azure_openai": bool(os.getenv("AZURE_OPENAI_API_KEY"))
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "foodxchange",
        "azure_openai_configured": bool(os.getenv("AZURE_OPENAI_API_KEY"))
    }

@app.get("/health/detailed")
async def health_detailed():
    return JSONResponse({
        "status": "healthy",
        "service": "foodxchange",
        "components": {
            "api": "operational",
            "azure_openai": "configured" if os.getenv("AZURE_OPENAI_API_KEY") else "not_configured"
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
