Write-Host "🚀 Starting Food Xchange Platform (Simplified Version)" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Kill any existing Python processes
Write-Host "Stopping any existing Python processes..." -ForegroundColor Yellow
taskkill /f /im python.exe 2>$null

# Wait a moment
Start-Sleep -Seconds 2

# Start the simplified server
Write-Host "Starting simplified server..." -ForegroundColor Yellow
Write-Host "Using: python -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload" -ForegroundColor Cyan

python -m uvicorn app.main_simple:app --host 0.0.0.0 --port 8000 --reload

Write-Host "✅ Server started successfully!" -ForegroundColor Green
Write-Host "🌐 Access your platform at: http://localhost:8000" -ForegroundColor Cyan 