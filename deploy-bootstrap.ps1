# Bootstrap Deployment Script for Food Xchange
# This script deploys and tests the Bootstrap implementation

Write-Host "Deploying Bootstrap for Food Xchange..." -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "app/main.py")) {
    Write-Host "❌ Error: Please run this script from the FoodXchange root directory" -ForegroundColor Red
    exit 1
}

# Check if Bootstrap routes file exists
if (!(Test-Path "app/routes/bootstrap_routes.py")) {
    Write-Host "❌ Error: Bootstrap routes file not found. Please run setup-bootstrap.ps1 first." -ForegroundColor Red
    exit 1
}

# Check if Bootstrap templates exist
$requiredTemplates = @(
    "app/templates/bootstrap/base.html",
    "app/templates/bootstrap/rfq-form.html",
    "app/templates/bootstrap/order-management.html",
    "app/templates/bootstrap/analytics.html",
    "app/templates/bootstrap/help.html"
)

$missingTemplates = @()
foreach ($template in $requiredTemplates) {
    if (!(Test-Path $template)) {
        $missingTemplates += $template
    }
}

if ($missingTemplates.Count -gt 0) {
    Write-Host "❌ Error: Missing Bootstrap templates:" -ForegroundColor Red
    foreach ($template in $missingTemplates) {
        Write-Host "  - $template" -ForegroundColor Red
    }
    Write-Host "Please run setup-bootstrap.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "All Bootstrap files found" -ForegroundColor Green

# Check if FastAPI is installed
try {
    python -c "import fastapi" 2>$null
    Write-Host "FastAPI is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: FastAPI not found. Installing..." -ForegroundColor Yellow
    pip install fastapi uvicorn jinja2
}

# Check if uvicorn is installed
try {
    python -c "import uvicorn" 2>$null
    Write-Host "Uvicorn is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Uvicorn not found. Installing..." -ForegroundColor Yellow
    pip install uvicorn
}

# Create a simple test script
$testScript = @"
import requests
import time
import sys

def test_bootstrap_endpoints():
    base_url = "http://localhost:8000"
    endpoints = [
        "/bootstrap/rfq",
        "/bootstrap/orders", 
        "/bootstrap/analytics",
        "/bootstrap/help"
    ]
    
    print("🧪 Testing Bootstrap endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print("\n🎉 Bootstrap deployment test complete!")

if __name__ == "__main__":
    test_bootstrap_endpoints()
"@

$testScript | Out-File -FilePath "test_bootstrap_deployment.py" -Encoding UTF8

Write-Host "Created deployment test script" -ForegroundColor Green

# Create a startup script
$startupScript = @"
# Start FastAPI server with Bootstrap
Write-Host "🚀 Starting Food Xchange with Bootstrap..." -ForegroundColor Green
Write-Host "📱 Bootstrap screens will be available at:" -ForegroundColor Cyan
Write-Host "  - http://localhost:8000/bootstrap/rfq" -ForegroundColor White
Write-Host "  - http://localhost:8000/bootstrap/orders" -ForegroundColor White
Write-Host "  - http://localhost:8000/bootstrap/analytics" -ForegroundColor White
Write-Host "  - http://localhost:8000/bootstrap/help" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
"@

$startupScript | Out-File -FilePath "start-bootstrap.ps1" -Encoding UTF8

Write-Host "Created startup script" -ForegroundColor Green

# Summary
Write-Host "`n🎉 Bootstrap Deployment Ready!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Start the server: .\start-bootstrap.ps1" -ForegroundColor White
Write-Host "  2. Open your browser and visit:" -ForegroundColor White
Write-Host "     - http://localhost:8000/bootstrap/rfq" -ForegroundColor White
Write-Host "     - http://localhost:8000/bootstrap/orders" -ForegroundColor White
Write-Host "     - http://localhost:8000/bootstrap/analytics" -ForegroundColor White
Write-Host "     - http://localhost:8000/bootstrap/help" -ForegroundColor White
Write-Host "  3. Test the deployment: python test_bootstrap_deployment.py" -ForegroundColor White
Write-Host ""
Write-Host "All Bootstrap screens are now integrated with your FastAPI backend!" -ForegroundColor Yellow
Write-Host "You can now work on and customize the Bootstrap screens." -ForegroundColor Yellow 