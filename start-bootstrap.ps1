# Start FastAPI server with Bootstrap
Write-Host "Starting Food Xchange with Bootstrap..." -ForegroundColor Green
Write-Host "Bootstrap screens will be available at:" -ForegroundColor Cyan
Write-Host "  - http://localhost:8000/bootstrap/rfq" -ForegroundColor White
Write-Host "  - http://localhost:8000/bootstrap/orders" -ForegroundColor White
Write-Host "  - http://localhost:8000/bootstrap/analytics" -ForegroundColor White
Write-Host "  - http://localhost:8000/bootstrap/help" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
