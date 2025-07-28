#!/usr/bin/env python
"""
Simple health check module for Azure App Service
No external dependencies to ensure it works during startup
"""
import os
import platform
from datetime import datetime

def get_simple_health():
    """Return basic health check without external dependencies"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FoodXchange",
        "version": "1.0.0",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "environment": os.getenv('FLASK_ENV', 'production'),
        "port": os.getenv('PORT', os.getenv('HTTP_PLATFORM_PORT', '8000'))
    }

def get_advanced_health():
    """Advanced health check with minimal system info"""
    try:
        import psutil
        system_info = {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
        }
    except ImportError:
        system_info = {
            "cpu_count": "unknown",
            "memory_info": "psutil not available"
        }
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "FoodXchange",
        "version": "1.0.0",
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "environment": os.getenv('FLASK_ENV', 'production'),
        "system": system_info,
        "database": "not_checked",  # Skip database check for startup
        "monitoring": {
            "sentry": "configured" if os.getenv('SENTRY_DSN') else "not_configured",
            "azure_monitor": "unknown"
        }
    }