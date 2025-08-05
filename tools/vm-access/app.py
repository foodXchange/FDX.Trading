from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from datetime import datetime
import asyncio
import aiohttp
import json

app = FastAPI(title="FoodXchange VM Control Center", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# VM Configuration
VM_CONFIG = {
    "host": "4.206.1.15",
    "services": [
        {
            "name": "FastAPI App (FDX.trading)",
            "url": "http://4.206.1.15",
            "port": 80,
            "icon": "fas fa-globe",
            "description": "Main FoodXchange application with login interface and trading functionality",
            "status": "online",
            "warning": False
        },
        {
            "name": "FDX Crawler (23,206 Suppliers)",
            "url": "http://4.206.1.15:8003",
            "port": 8003,
            "icon": "fas fa-spider",
            "description": "Complete supplier database with advanced search and AI-powered email features",
            "status": "online",
            "warning": False
        },
        {
            "name": "Grafana Monitoring",
            "url": "http://4.206.1.15:3000",
            "port": 3000,
            "icon": "fas fa-chart-line",
            "description": "Advanced system monitoring dashboard with real-time metrics and alerts",
            "status": "blocked",
            "warning": True,
            "warning_message": "Port 3000 blocked by Azure firewall"
        },
        {
            "name": "Netdata Real-time",
            "url": "http://4.206.1.15:19999",
            "port": 19999,
            "icon": "fas fa-tachometer-alt",
            "description": "High-performance real-time system metrics and resource monitoring",
            "status": "blocked",
            "warning": True,
            "warning_message": "Port 19999 blocked by Azure firewall"
        }
    ],
    "ssh": {
        "host": "fdxfounder@4.206.1.15",
        "key": "~/.ssh/fdx_founders_key",
        "command": "ssh -i ~/.ssh/fdx_founders_key fdxfounder@4.206.1.15"
    },
    "credentials": {
        "grafana": {
            "username": "admin",
            "password": "admin"
        }
    }
}

async def check_service_status(service):
    """Check if a service is accessible"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            async with session.get(service["url"]) as response:
                return "online" if response.status < 400 else "offline"
    except:
        return "offline"

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    # Check service statuses
    for service in VM_CONFIG["services"]:
        if not service.get("warning"):
            service["status"] = await check_service_status(service)
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "config": VM_CONFIG,
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.get("/api/services")
async def get_services():
    """API endpoint to get service statuses"""
    # Check all service statuses
    for service in VM_CONFIG["services"]:
        if not service.get("warning"):
            service["status"] = await check_service_status(service)
    
    return {"services": VM_CONFIG["services"]}

@app.get("/api/vm-status")
async def get_vm_status():
    """API endpoint to get VM status"""
    return {
        "vm_status": "Online & Running",
        "network": VM_CONFIG["host"],
        "security": "SSH Key Protected",
        "uptime": "24h 15m 32s"  # This would be fetched from the actual VM
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True) 