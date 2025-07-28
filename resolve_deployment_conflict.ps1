#!/usr/bin/env pwsh
# Azure App Service Deployment Conflict Resolution Script
# This script resolves 409 deployment conflicts by restarting the service

param(
    [Parameter(Mandatory=$true)]
    [string]$AppName = "foodxchange-app",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroup = "foodxchange-rg"
)

Write-Host "🔧 Resolving deployment conflict for $AppName..." -ForegroundColor Yellow

try {
    # Check if Azure CLI is available
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Azure CLI not found. Please install Azure CLI first." -ForegroundColor Red
        exit 1
    }

    # Stop the app service
    Write-Host "⏹️  Stopping app service..." -ForegroundColor Blue
    az webapp stop --name $AppName --resource-group $ResourceGroup --output none
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠️  Warning: Failed to stop app service. Continuing anyway..." -ForegroundColor Yellow
    }

    # Wait for service to fully stop
    Write-Host "⏳ Waiting 30 seconds for service to stop..." -ForegroundColor Blue
    Start-Sleep -Seconds 30

    # Start the app service
    Write-Host "▶️  Starting app service..." -ForegroundColor Blue
    az webapp start --name $AppName --resource-group $ResourceGroup --output none
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start app service." -ForegroundColor Red
        exit 1
    }

    # Wait for service to be ready
    Write-Host "⏳ Waiting 15 seconds for service to be ready..." -ForegroundColor Blue
    Start-Sleep -Seconds 15

    Write-Host "✅ App service restart completed successfully!" -ForegroundColor Green
    Write-Host "📝 You can now retry your deployment." -ForegroundColor Cyan

} catch {
    Write-Host "❌ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}