# Create Azure Service Principal for GitHub Actions
$subscriptionId = "88931ed0-52df-42fb-a09c-e024c9586f8a"
$resourceGroup = "foodxchange-rg"
$spName = "github-actions-foodxchange"

Write-Host "Creating service principal for GitHub Actions..." -ForegroundColor Yellow

$sp = az ad sp create-for-rbac `
  --name $spName `
  --role contributor `
  --scopes "/subscriptions/$subscriptionId/resourceGroups/$resourceGroup" `
  --output json | ConvertFrom-Json

if ($sp) {
    Write-Host "`nService Principal created successfully!" -ForegroundColor Green
    Write-Host "`nAdd these secrets to your GitHub repository:" -ForegroundColor Cyan
    Write-Host "=================================" -ForegroundColor Cyan
    Write-Host "AZURE_CLIENT_ID: $($sp.appId)" -ForegroundColor White
    Write-Host "AZURE_TENANT_ID: $($sp.tenant)" -ForegroundColor White
    Write-Host "AZURE_SUBSCRIPTION_ID: $subscriptionId" -ForegroundColor White
    Write-Host "=================================" -ForegroundColor Cyan
    
    # Also save to a file for reference
    $output = @{
        AZURE_CLIENT_ID = $sp.appId
        AZURE_TENANT_ID = $sp.tenant
        AZURE_SUBSCRIPTION_ID = $subscriptionId
        AZURE_CLIENT_SECRET = $sp.password
    }
    
    $output | ConvertTo-Json | Out-File -FilePath "github_secrets.json"
    Write-Host "`nSecrets also saved to github_secrets.json (keep this file secure!)" -ForegroundColor Yellow
} else {
    Write-Host "Failed to create service principal" -ForegroundColor Red
}