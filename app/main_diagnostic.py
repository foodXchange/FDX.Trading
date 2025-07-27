"""Diagnostic version of main.py to debug Azure deployment issues"""
import os
import sys
import traceback
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="FoodXchange Diagnostic")

# Store diagnostic info
diagnostics = {
    "python_version": sys.version,
    "working_directory": os.getcwd(),
    "python_path": sys.path,
    "environment_variables": {},
    "import_errors": [],
    "startup_errors": []
}

# Check environment variables
critical_vars = [
    "DATABASE_URL",
    "SECRET_KEY", 
    "AZURE_OPENAI_API_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",
    "PORT"
]

for var in critical_vars:
    value = os.getenv(var)
    diagnostics["environment_variables"][var] = "SET" if value else "NOT SET"

# Try imports
imports_to_test = [
    "sqlalchemy",
    "fastapi",
    "uvicorn",
    "psycopg2",
    "azure.storage.blob",
    "openai",
    "pandas",
    "httpx"
]

for module in imports_to_test:
    try:
        __import__(module)
        diagnostics["import_errors"].append(f"{module}: OK")
    except ImportError as e:
        diagnostics["import_errors"].append(f"{module}: FAILED - {str(e)}")

@app.get("/")
async def root():
    """Root endpoint showing diagnostic info"""
    return JSONResponse({
        "status": "diagnostic_mode",
        "message": "FoodXchange is running in diagnostic mode",
        "diagnostics": diagnostics
    })

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "mode": "diagnostic",
        "timestamp": os.environ.get("DEPLOYMENT_TIME", "unknown")
    }

@app.get("/diagnostics")
async def get_diagnostics():
    """Detailed diagnostics"""
    return diagnostics

# Try to load the real app
try:
    # Test database connection
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        from sqlalchemy import create_engine
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            diagnostics["startup_errors"].append("Database connection: OK")
    else:
        diagnostics["startup_errors"].append("Database connection: No DATABASE_URL")
except Exception as e:
    diagnostics["startup_errors"].append(f"Database error: {str(e)}")

# Run with uvicorn if called directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)