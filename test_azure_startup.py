"""Test script to verify Azure startup configuration"""
import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

print("=== Testing Azure Startup Configuration ===")

# Test 1: Environment loading
print("\n1. Testing environment loading...")
from app.load_all_env import load_all_env_files
configs = load_all_env_files()

# Test 2: Import application
print("\n2. Testing application import...")
try:
    from app.main import app
    print("[OK] Application imported successfully")
except Exception as e:
    print(f"[ERROR] Failed to import application: {e}")
    sys.exit(1)

# Test 3: Check configuration
print("\n3. Testing configuration...")
from app.config import get_settings
settings = get_settings()

config_status = {
    "Database": bool(settings.database_url),
    "Azure OpenAI": bool(settings.azure_openai_api_key),
    "Azure Blob Storage": bool(settings.azure_storage_connection_string),
    "Email Service": bool(settings.azure_email_connection_string or settings.smtp_host)
}

for service, configured in config_status.items():
    status = "[OK]" if configured else "[MISSING]"
    print(f"{status} {service}")

# Test 4: Check critical services
print("\n4. Testing service initialization...")
try:
    from app.services.blob_storage_service import BlobStorageService
    blob_service = BlobStorageService()
    if blob_service.is_configured():
        print("[OK] Blob Storage Service initialized")
    else:
        print("[WARNING] Blob Storage Service not configured")
except Exception as e:
    print(f"[ERROR] Blob Storage Service error: {e}")

print("\n=== Configuration test complete ===")
print("If all critical services show [OK], the app should deploy successfully.")