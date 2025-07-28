from fastapi import FastAPI, Request
from fastapi.responses import Response
import os

app = FastAPI()

@app.get("/")
@app.head("/")
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"message": "FoodXchange API", "status": "running"}

@app.get("/health")
@app.head("/health")
async def health(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)