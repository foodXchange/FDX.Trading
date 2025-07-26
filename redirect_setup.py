# Add this to your main FastAPI application

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.middleware("http")
async def redirect_middleware(request: Request, call_next):
    # Get the host from the request
    host = request.headers.get("host", "")
    
    # Redirect www to non-www
    if host.startswith("www.fdx.trading"):
        url = str(request.url)
        new_url = url.replace("www.fdx.trading", "fdx.trading")
        return RedirectResponse(url=new_url, status_code=301)
    
    # Redirect HTTP to HTTPS
    if request.url.scheme == "http":
        url = str(request.url)
        new_url = url.replace("http://", "https://")
        return RedirectResponse(url=new_url, status_code=301)
    
    response = await call_next(request)
    return response

# Your existing routes go here... 