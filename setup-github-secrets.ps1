# Setup GitHub Secrets for FoodXchange CI/CD
# This script helps configure all required GitHub secrets

param(
    [Parameter(Mandatory=$false)]
    [string]$GitHubRepo = "foodxchange/foodxchange-app",
    
    [Parameter(Mandatory=$false)]
    [switch]$UseOIDC = $false
)

Write-Host "GitHub Secrets Setup for FoodXchange" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

# Check if GitHub CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "GitHub CLI not found. Installing..." -ForegroundColor Yellow
    winget install --id GitHub.cli
    Write-Host "Please restart PowerShell after installation and run this script again." -ForegroundColor Yellow
    exit 1
}

# Check GitHub authentication
Write-Host "`nChecking GitHub authentication..." -ForegroundColor Cyan
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not authenticated with GitHub. Starting login..." -ForegroundColor Yellow
    gh auth login
}

# Function to set secret
function Set-GitHubSecret {
    param(
        [string]$Name,
        [string]$Value,
        [string]$Repo
    )
    
    Write-Host "Setting secret: $Name" -ForegroundColor Gray
    $Value | gh secret set $Name --repo $Repo
}

Write-Host "`nConfiguring secrets for repository: $GitHubRepo" -ForegroundColor Cyan

# Method 1: Using Azure Publish Profile (Recommended for quick setup)
Write-Host "`n=== Method 1: Publish Profile Setup ===" -ForegroundColor Yellow
Write-Host "This is the simplest method and recommended for most users." -ForegroundColor Gray

$usePublishProfile = Read-Host "Do you want to use Publish Profile authentication? (Y/N)"
if ($usePublishProfile -eq 'Y' -or $usePublishProfile -eq 'y') {
    Write-Host "`nTo get your publish profile:" -ForegroundColor Cyan
    Write-Host "1. Go to Azure Portal (https://portal.azure.com)"
    Write-Host "2. Navigate to your App Service (foodxchange-app)"
    Write-Host "3. Click 'Download publish profile' in the Overview section"
    Write-Host "4. Open the downloaded file and copy its entire contents"
    
    Write-Host "`nPaste the publish profile content (press Enter twice when done):" -ForegroundColor Yellow
    $publishProfile = ""
    while ($true) {
        $line = Read-Host
        if ([string]::IsNullOrWhiteSpace($line)) {
            if ($publishProfile.EndsWith("`n`n")) { break }
        }
        $publishProfile += $line + "`n"
    }
    
    if ($publishProfile.Trim()) {
        Set-GitHubSecret -Name "AZUREAPPSERVICE_PUBLISHPROFILE" -Value $publishProfile.Trim() -Repo $GitHubRepo
        Write-Host "✅ Publish profile secret set successfully!" -ForegroundColor Green
    }
}

# Method 2: Using OIDC (Federated credentials)
if ($UseOIDC) {
    Write-Host "`n=== Method 2: OIDC Setup (Advanced) ===" -ForegroundColor Yellow
    Write-Host "This method uses federated credentials for enhanced security." -ForegroundColor Gray
    
    Write-Host "`nYou'll need the following from your Azure AD app registration:" -ForegroundColor Cyan
    Write-Host "- Client ID (Application ID)"
    Write-Host "- Tenant ID"
    Write-Host "- Subscription ID"
    
    $clientId = Read-Host "Enter Azure Client ID"
    $tenantId = Read-Host "Enter Azure Tenant ID"
    $subscriptionId = Read-Host "Enter Azure Subscription ID"
    
    if ($clientId -and $tenantId -and $subscriptionId) {
        Set-GitHubSecret -Name "AZURE_CLIENT_ID" -Value $clientId -Repo $GitHubRepo
        Set-GitHubSecret -Name "AZURE_TENANT_ID" -Value $tenantId -Repo $GitHubRepo
        Set-GitHubSecret -Name "AZURE_SUBSCRIPTION_ID" -Value $subscriptionId -Repo $GitHubRepo
        Write-Host "✅ OIDC secrets set successfully!" -ForegroundColor Green
        
        Write-Host "`nIMPORTANT: Configure federated credentials in Azure:" -ForegroundColor Yellow
        Write-Host "1. Go to your App Registration in Azure AD"
        Write-Host "2. Navigate to 'Certificates & secrets' > 'Federated credentials'"
        Write-Host "3. Add a credential for: repo:$GitHubRepo:ref:refs/heads/main"
    }
}

# Method 3: Service Principal with password
Write-Host "`n=== Method 3: Service Principal (Alternative) ===" -ForegroundColor Yellow
$useServicePrincipal = Read-Host "Do you want to configure Service Principal authentication? (Y/N)"
if ($useServicePrincipal -eq 'Y' -or $useServicePrincipal -eq 'y') {
    Write-Host "`nCreate service principal credentials JSON in this format:" -ForegroundColor Cyan
    Write-Host '{
  "clientId": "<YOUR_CLIENT_ID>",
  "clientSecret": "<YOUR_CLIENT_SECRET>",
  "subscriptionId": "<YOUR_SUBSCRIPTION_ID>",
  "tenantId": "<YOUR_TENANT_ID>"
}' -ForegroundColor Gray
    
    Write-Host "`nPaste the credentials JSON (press Enter twice when done):" -ForegroundColor Yellow
    $credentials = ""
    while ($true) {
        $line = Read-Host
        if ([string]::IsNullOrWhiteSpace($line)) {
            if ($credentials.EndsWith("`n`n")) { break }
        }
        $credentials += $line + "`n"
    }
    
    if ($credentials.Trim()) {
        Set-GitHubSecret -Name "AZURE_CREDENTIALS" -Value $credentials.Trim() -Repo $GitHubRepo
        Write-Host "✅ Service principal credentials set successfully!" -ForegroundColor Green
    }
}

# Verify secrets
Write-Host "`n=== Verifying Secrets ===" -ForegroundColor Cyan
Write-Host "Current secrets in repository:" -ForegroundColor Gray
gh secret list --repo $GitHubRepo

Write-Host "`n✅ GitHub secrets configuration complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Commit and push your changes to trigger the workflow"
Write-Host "2. Monitor the Actions tab in your GitHub repository"
Write-Host "3. Check deployment status at: https://github.com/$GitHubRepo/actions"

# Create quick reference
Write-Host "`nCreating quick reference file..." -ForegroundColor Gray
@"
# GitHub Secrets Quick Reference

Repository: $GitHubRepo
Date configured: $(Get-Date)

## Configured Authentication Methods:

$(if ($usePublishProfile -eq 'Y') { "✅ Publish Profile (AZUREAPPSERVICE_PUBLISHPROFILE)" } else { "❌ Publish Profile" })
$(if ($UseOIDC) { "✅ OIDC/Federated (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_SUBSCRIPTION_ID)" } else { "❌ OIDC/Federated" })
$(if ($useServicePrincipal -eq 'Y') { "✅ Service Principal (AZURE_CREDENTIALS)" } else { "❌ Service Principal" })

## Workflow Status:
- Main workflow: .github/workflows/main_foodxchange-app.yml
- Triggers on: push to main, pull requests, manual dispatch

## Troubleshooting:
- View secrets: gh secret list --repo $GitHubRepo
- View workflow runs: gh run list --repo $GitHubRepo
- View specific run: gh run view <run-id> --repo $GitHubRepo

## Update a secret:
echo "new-value" | gh secret set SECRET_NAME --repo $GitHubRepo
"@ | Out-File -FilePath "github-secrets-configured.txt" -Encoding UTF8

Write-Host "✅ Reference saved to: github-secrets-configured.txt" -ForegroundColor Green