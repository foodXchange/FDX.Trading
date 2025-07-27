import os
import sys
import importlib
from pathlib import Path

print("=== FoodXchange System Health Check ===\n")

# Check Python version
print(f"Python Version: {sys.version}")

# Check environment files
env_files = ['.env', '.env.blob', 'azure_blob_config.json']
print("\nEnvironment Files:")
for file in env_files:
    exists = "[OK]" if Path(file).exists() else "[MISSING]"
    print(f"  {exists} {file}")

# Check critical directories
directories = ['app', 'app/routes', 'app/services', 'app/models', 'app/templates', 'app/static']
print("\nDirectories:")
for dir_path in directories:
    exists = "[OK]" if Path(dir_path).exists() else "[MISSING]"
    print(f"  {exists} {dir_path}")

# Check key dependencies
print("\nDependencies:")
packages = [
    'fastapi', 'uvicorn', 'httpx', 'azure.storage.blob', 
    'azure.communication.email', 'openai', 'sqlalchemy',
    'pydantic', 'python-multipart', 'python-jose'
]
for package in packages:
    try:
        importlib.import_module(package.split('.')[0])
        print(f"  [OK] {package}")
    except ImportError:
        print(f"  [MISSING] {package}")

# Check main application file
print("\nApplication Files:")
app_files = ['app/main.py', 'app/config.py', 'app/database.py']
for file in app_files:
    if Path(file).exists():
        try:
            # Try to compile the file
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"  [OK] {file} (valid syntax)")
        except SyntaxError as e:
            print(f"  [ERROR] {file} (syntax error: {e})")
    else:
        print(f"  [MISSING] {file} (missing)")

# Check Azure configuration
print("\nAzure Configuration:")
azure_vars = ['AZURE_STORAGE_CONNECTION_STRING', 'AZURE_OPENAI_API_KEY', 'AZURE_COMMUNICATION_CONNECTION_STRING']
for var in azure_vars:
    value = os.getenv(var, '')
    status = "[OK] Set" if value else "[NOT SET]"
    print(f"  {status} {var}")

# Check database
print("\nDatabase:")
db_url = os.getenv('DATABASE_URL', 'sqlite:///./foodxchange.db')
print(f"  URL: {db_url}")
if 'sqlite' in db_url:
    db_file = db_url.replace('sqlite:///', '')
    exists = "[OK]" if Path(db_file).exists() else "[MISSING]"
    print(f"  {exists} SQLite file exists")

print("\n=== Health Check Complete ===")