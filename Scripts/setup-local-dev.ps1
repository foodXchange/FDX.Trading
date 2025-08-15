# Local Development Setup Script
# Sets up user secrets for secure local development

param(
    [switch]$UseAzureSql,
    [switch]$UseLocalDb
)

Write-Host "Setting up local development environment..." -ForegroundColor Green

# Initialize user secrets
Write-Host "Initializing user secrets..." -ForegroundColor Yellow
Set-Location "src\FoodXchange.Api"
dotnet user-secrets init

if ($UseAzureSql) {
    Write-Host "Configuring Azure SQL connection..." -ForegroundColor Yellow
    
    # Prompt for authentication method
    Write-Host "Choose authentication method:" -ForegroundColor Cyan
    Write-Host "1. Azure AD (recommended - uses your Azure CLI login)"
    Write-Host "2. SQL Authentication (requires password)"
    
    $choice = Read-Host "Enter choice (1 or 2)"
    
    if ($choice -eq "1") {
        # Azure AD authentication
        $connectionString = "Server=tcp:fdx-sql-prod.database.windows.net,1433;Database=fdxdb;Encrypt=True;TrustServerCertificate=False;Authentication=Active Directory Default"
        dotnet user-secrets set "ConnectionStrings:Sql" $connectionString
        Write-Host "Configured for Azure AD authentication" -ForegroundColor Green
        Write-Host "Make sure you're logged in with: az login" -ForegroundColor Yellow
    }
    else {
        # SQL Authentication - NEVER commit the password
        Write-Host "WARNING: Only use SQL auth for local development!" -ForegroundColor Red
        $password = Read-Host -Prompt "Enter SQL Password" -AsSecureString
        $passwordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
        
        $connectionString = "Server=tcp:fdx-sql-prod.database.windows.net,1433;Database=fdxdb;User ID=fdxadmin;Password=$passwordPlain;Encrypt=True;TrustServerCertificate=False;"
        dotnet user-secrets set "ConnectionStrings:Sql" $connectionString
        Write-Host "Configured for SQL authentication" -ForegroundColor Green
        Write-Host "Password stored in user secrets (not in source control)" -ForegroundColor Yellow
    }
}
else {
    Write-Host "Using LocalDB for development" -ForegroundColor Yellow
    # LocalDB is already configured in appsettings.Development.json
}

# Set Azure OpenAI credentials (optional)
$configureAi = Read-Host "Configure Azure OpenAI? (y/n)"
if ($configureAi -eq "y") {
    $endpoint = Read-Host "Enter Azure OpenAI Endpoint (e.g., https://xxx.openai.azure.com/)"
    $key = Read-Host -Prompt "Enter Azure OpenAI Key" -AsSecureString
    $keyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($key))
    
    dotnet user-secrets set "AZURE_OPENAI_ENDPOINT" $endpoint
    dotnet user-secrets set "AZURE_OPENAI_KEY" $keyPlain
    dotnet user-secrets set "AZURE_OPENAI_DEPLOYMENT" "gpt-4o-mini"
    
    Write-Host "Azure OpenAI configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "Local development setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To view your secrets:" -ForegroundColor Cyan
Write-Host "  dotnet user-secrets list" -ForegroundColor Gray
Write-Host ""
Write-Host "To run the API:" -ForegroundColor Cyan
Write-Host "  dotnet run" -ForegroundColor Gray
Write-Host ""
Write-Host "Test endpoints:" -ForegroundColor Cyan
Write-Host "  https://localhost:5001/health" -ForegroundColor Gray
Write-Host "  https://localhost:5001/db/verify" -ForegroundColor Gray

Set-Location "..\.."