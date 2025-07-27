# Monitoring System Check Script

Write-Host "=== FoodXchange Monitoring System Check ===" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "https://foodxchange-app.azurewebsites.net"
$endpoints = @(
    @{Name="Health Check"; Url="$baseUrl/health"},
    @{Name="System Status"; Url="$baseUrl/system-status"},
    @{Name="Azure Monitor Status"; Url="$baseUrl/api/monitoring/status"},
    @{Name="Main App"; Url="$baseUrl"}
)

Write-Host "Checking deployment status..." -ForegroundColor Yellow
$deploymentStatus = az webapp deployment list --name foodxchange-app --resource-group foodxchange-rg --query "[0].status" -o tsv
Write-Host "Latest deployment status: $deploymentStatus" -ForegroundColor White
Write-Host ""

Write-Host "Testing monitoring endpoints..." -ForegroundColor Yellow
Write-Host ""

foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $($endpoint.Name)" -ForegroundColor White
    Write-Host "URL: $($endpoint.Url)" -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
        Write-Host "✅ Status: $($response.StatusCode) - $($response.StatusDescription)" -ForegroundColor Green
        
        if ($endpoint.Name -eq "Health Check" -or $endpoint.Name -eq "System Status") {
            $content = $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
            Write-Host "Response:" -ForegroundColor White
            Write-Host $content -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "Checking Azure Monitor Integration..." -ForegroundColor Yellow
$appInsights = az webapp config appsettings list --name foodxchange-app --resource-group foodxchange-rg --query "[?name=='APPLICATIONINSIGHTS_CONNECTION_STRING'].value" -o tsv
if ($appInsights) {
    Write-Host "✅ Application Insights configured" -ForegroundColor Green
} else {
    Write-Host "⚠️  Application Insights not configured" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Checking logs for monitoring messages..." -ForegroundColor Yellow
Write-Host "Run this command to see live logs:" -ForegroundColor White
Write-Host "az webapp log tail --name foodxchange-app --resource-group foodxchange-rg" -ForegroundColor Gray