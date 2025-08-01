"""Minimal FastAPI server to test if the issue is in our code"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting minimal test server on http://localhost:8004")
    uvicorn.run(app, host="127.0.0.1", port=8004)