from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FoodXchange Test</title>
    </head>
    <body>
        <h1>FoodXchange Server is Running!</h1>
        <p>If you can see this, the server is working.</p>
        <a href="/admin">Go to Admin Dashboard</a>
    </body>
    </html>
    """)

@app.get("/admin")
async def admin():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
    </head>
    <body>
        <h1>Admin Dashboard</h1>
        <p>Welcome to the admin area!</p>
        <a href="/">Back to Home</a>
    </body>
    </html>
    """)

if __name__ == "__main__":
    import uvicorn
    print("Starting test server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)