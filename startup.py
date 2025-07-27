import subprocess
import sys

# Run the FastAPI app with gunicorn
subprocess.run([
    sys.executable, "-m", "gunicorn",
    "-w", "4",
    "-k", "uvicorn.workers.UvicornWorker",
    "app.main:app",
    "--bind", "0.0.0.0:8000"
])