"""
Development authentication configuration
Only loaded when ENVIRONMENT=development
"""
import os
from typing import Dict, Any


def get_development_users() -> Dict[str, Dict[str, Any]]:
    """
    Get development users from environment variables
    Falls back to secure defaults if not set
    """
    if os.getenv("ENVIRONMENT", "production").lower() != "development":
        return {}
    
    return {
        os.getenv("DEV_ADMIN_EMAIL", "admin@fdx.trading"): {
            "password": os.getenv("DEV_ADMIN_PASSWORD", "FDX2030!"),
            "role": "admin",
            "user_id": 1
        },
        os.getenv("DEV_USER_EMAIL", "user@fdx.trading"): {
            "password": os.getenv("DEV_USER_PASSWORD", "user123"),
            "role": "user", 
            "user_id": 2
        },
        os.getenv("DEV_DEMO_EMAIL", "demo@fdx.trading"): {
            "password": os.getenv("DEV_DEMO_PASSWORD", "demo123"),
            "role": "user",
            "user_id": 3
        }
    }


def is_development_mode() -> bool:
    """Check if running in development mode"""
    return os.getenv("ENVIRONMENT", "production").lower() == "development"