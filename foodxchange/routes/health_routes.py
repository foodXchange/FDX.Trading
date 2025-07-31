"""Health check routes for monitoring and load balancers"""

from fastapi import APIRouter, Request
from datetime import datetime
import os
import redis
import psutil
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {},
        "resources": {}
    }
    
    # Check Redis connection
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        redis_info = r.info()
        health_status["services"]["redis"] = {
            "status": "healthy",
            "memory": redis_info.get("used_memory_human", "unknown"),
            "connected_clients": redis_info.get("connected_clients", 0),
            "uptime_days": redis_info.get("uptime_in_days", 0)
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"
    
    # Check system resources
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status["resources"] = {
            "cpu": {
                "percent": cpu_percent,
                "status": "healthy" if cpu_percent < 80 else "warning"
            },
            "memory": {
                "percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2),
                "status": "healthy" if memory.percent < 80 else "warning"
            },
            "disk": {
                "percent": disk.percent,
                "free_gb": round(disk.free / (1024**3), 2),
                "status": "healthy" if disk.percent < 80 else "warning"
            }
        }
    except Exception as e:
        logger.error(f"Resource check failed: {e}")
        health_status["resources"] = {"status": "unavailable", "error": str(e)}
    
    # Check Azure AI configuration
    azure_configured = all([
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    ])
    
    health_status["services"]["azure_ai"] = {
        "status": "configured" if azure_configured else "not_configured",
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT", "").split('.')[0] if azure_configured else None
    }
    
    # Check if running in Docker
    health_status["environment"] = {
        "docker": os.path.exists("/.dockerenv"),
        "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
    }
    
    # Determine overall status
    unhealthy_services = [name for name, service in health_status["services"].items() 
                         if service.get("status") == "unhealthy"]
    warning_resources = [name for name, resource in health_status["resources"].items() 
                        if isinstance(resource, dict) and resource.get("status") == "warning"]
    
    if unhealthy_services:
        health_status["status"] = "unhealthy"
        health_status["issues"] = unhealthy_services
    elif warning_resources:
        health_status["status"] = "degraded"
        health_status["warnings"] = warning_resources
    
    return health_status

@router.get("/health/simple")
async def simple_health():
    """Simple health check for basic monitoring"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@router.get("/health/redis")
async def redis_health():
    """Redis-specific health check"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        info = r.info()
        
        return {
            "status": "healthy",
            "memory_usage": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "uptime_days": info.get("uptime_in_days"),
            "version": info.get("redis_version")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }