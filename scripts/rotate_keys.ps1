# Key Rotation Script - Run monthly for security
# Rotates Azure service keys and updates .env file

Write-Host "🔐 Rotating Azure Keys..." -ForegroundColor Cyan

# Backup current .env
Copy-Item .env ".env.backup.$(Get-Date -Format 'yyyyMMdd')"

# Rotate OpenAI key
Write-Host "Rotating OpenAI key..." -ForegroundColor Yellow
$newKey = az cognitiveservices account keys regenerate `
    --name foodxchangeopenai `
    --resource-group foodxchange-rg `
    --key-name key1 `
    --query "key1" -o tsv

# Update .env file
(Get-Content .env) -replace 'AZURE_OPENAI_API_KEY=.*', "AZURE_OPENAI_API_KEY=$newKey" | Set-Content .env

Write-Host "✅ Keys rotated successfully!" -ForegroundColor Green
Write-Host "⚠️  Remember to restart your application!" -ForegroundColor Yellow