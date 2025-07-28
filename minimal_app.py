from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {"message": "FoodXchange API", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("minimal_app:app", host="0.0.0.0", port=port)