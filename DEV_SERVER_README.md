# FoodXchange Development Server

This document explains how to start the FoodXchange development server on port 9000 with auto-reload functionality.

## Quick Start Options

### Option 1: FastAPI Server (Recommended)
```bash
# Windows Batch File
start_server_9000.bat

# Or use the quick start
quick_start_9000.bat
```

### Option 2: Flask Server
```bash
# Windows Batch File
start_flask_9000.bat
```

### Option 3: Python Script (Most Flexible)
```bash
# Windows Batch File
dev_server.bat

# Or run directly
foodxchange-env\Scripts\python.exe dev_server.py
```

## Server Details

- **Port**: 9000
- **URL**: http://localhost:9000
- **Auto-reload**: Enabled by default
- **Framework**: FastAPI (primary) or Flask (alternative)

## Command Line Options

When using the Python script (`dev_server.py`), you can customize the server:

```bash
# Start FastAPI server on port 9000 (default)
python dev_server.py

# Start Flask server on port 9000
python dev_server.py --flask

# Start on different port
python dev_server.py --port 8000

# Disable auto-reload
python dev_server.py --no-reload

# Custom host
python dev_server.py --host 127.0.0.1
```

## Environment Setup

The batch files automatically:
1. Check for virtual environment
2. Activate the environment
3. Install missing dependencies
4. Set development environment variables
5. Start the server with auto-reload

## Manual Setup (if needed)

If you prefer to set up manually:

```bash
# Create virtual environment
python -m venv foodxchange-env

# Activate (Windows)
foodxchange-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port 9000 --reload

# Or start Flask server
python app.py
```

## Troubleshooting

### Port Already in Use
If port 9000 is already in use, you can:
1. Kill the process using port 9000
2. Use a different port: `python dev_server.py --port 8000`

### Virtual Environment Issues
If the virtual environment is corrupted:
1. Delete the `foodxchange-env` folder
2. Run `quick_start_9000.bat` to recreate it

### Import Errors
Make sure you're in the project root directory and the virtual environment is activated.

## Health Check

Once the server is running, you can verify it's working:

```bash
curl http://localhost:9000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-01T15:36:44.020223"
}
```

## Development Workflow

1. Start the server using any of the batch files
2. Make changes to your code
3. The server will automatically reload when files change
4. View changes at http://localhost:9000

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running to stop it. 