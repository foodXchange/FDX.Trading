# FoodXchange GitHub Secrets Setup Script
# Poland Central Infrastructure

Write-Host "🔧 Setting up GitHub Secrets for FoodXchange" -ForegroundColor Green
Write-Host "📍 Poland Central VM: 74.248.141.31" -ForegroundColor Cyan
Write-Host ""

# Get repository name
$repo = (git remote get-url origin) -replace '.*github\.com[:/]([^/]*/[^/]*).*', '$1'
Write-Host "📦 Repository: $repo" -ForegroundColor Yellow
Write-Host ""

# Check if gh CLI is installed
try {
    gh --version | Out-Null
    Write-Host "✅ GitHub CLI ready" -ForegroundColor Green
} catch {
    Write-Host "❌ GitHub CLI (gh) not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://cli.github.com/" -ForegroundColor Yellow
    exit 1
}

# Check if user is authenticated
try {
    gh auth status | Out-Null
} catch {
    Write-Host "❌ Not authenticated with GitHub. Please run:" -ForegroundColor Red
    Write-Host "   gh auth login" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Database Configuration
Write-Host "🗄️ Database Configuration:" -ForegroundColor Magenta
Write-Host "Setting DATABASE_URL..." -ForegroundColor Green
$databaseUrl = "postgresql://fdxadmin:FoodXchange2024!@fdx-poland-db.postgres.database.azure.com/foodxchange?sslmode=require"
gh secret set DATABASE_URL --body $databaseUrl --repo $repo
Write-Host ""

# VM Configuration
Write-Host "🖥️ VM Configuration:" -ForegroundColor Magenta

# Check for SSH key
if (Test-Path "~/.ssh/fdx_poland_key") {
    Write-Host "Setting VM_SSH_KEY from ~/.ssh/fdx_poland_key..." -ForegroundColor Green
    $sshKey = Get-Content "~/.ssh/fdx_poland_key" -Raw
    gh secret set VM_SSH_KEY --body $sshKey --repo $repo
} else {
    Write-Host "⚠️ SSH key not found at ~/.ssh/fdx_poland_key" -ForegroundColor Yellow
    Write-Host "   gh secret set VM_SSH_KEY --body 'YOUR_SSH_KEY' --repo $repo"
}

Write-Host "Setting VM_HOST..." -ForegroundColor Green
gh secret set VM_HOST --body "74.248.141.31" --repo $repo

Write-Host "Setting VM_USER..." -ForegroundColor Green
gh secret set VM_USER --body "azureuser" --repo $repo

Write-Host ""

# Azure OpenAI Configuration
Write-Host "🤖 Azure OpenAI Configuration:" -ForegroundColor Magenta

# Check for Azure OpenAI environment variables
Write-Host "`nChecking for Azure OpenAI credentials..." -ForegroundColor Yellow

if ($env:AZURE_OPENAI_KEY) {
    Write-Host "Setting AZURE_OPENAI_KEY from environment..." -ForegroundColor Green
    gh secret set AZURE_OPENAI_KEY --body $env:AZURE_OPENAI_KEY --repo $repo
} else {
    Write-Host "AZURE_OPENAI_KEY not found in environment" -ForegroundColor Red
    Write-Host "  gh secret set AZURE_OPENAI_KEY --body 'YOUR_KEY' --repo $repo"
}

if ($env:AZURE_OPENAI_ENDPOINT) {
    Write-Host "Setting AZURE_OPENAI_ENDPOINT from environment..." -ForegroundColor Green
    gh secret set AZURE_OPENAI_ENDPOINT --body $env:AZURE_OPENAI_ENDPOINT --repo $repo
} else {
    Write-Host "AZURE_OPENAI_ENDPOINT not found in environment" -ForegroundColor Red
    Write-Host "  gh secret set AZURE_OPENAI_ENDPOINT --body 'https://YOUR.openai.azure.com/' --repo $repo"
}

# Set deployment name
$deployment = if ($env:AZURE_OPENAI_DEPLOYMENT) { $env:AZURE_OPENAI_DEPLOYMENT } else { "gpt-4o-mini" }
Write-Host "Setting AZURE_OPENAI_DEPLOYMENT to: $deployment" -ForegroundColor Green
gh secret set AZURE_OPENAI_DEPLOYMENT --body $deployment --repo $repo

Write-Host ""

# Optional: Email Configuration
Write-Host "📧 Optional Email Configuration:" -ForegroundColor Magenta
Write-Host "To set up email notifications, run these commands:" -ForegroundColor Yellow
Write-Host "  gh secret set SMTP_SERVER --body 'smtp-mail.outlook.com' --repo $repo"
Write-Host "  gh secret set SMTP_PORT --body '587' --repo $repo"
Write-Host "  gh secret set SMTP_USERNAME --body 'your-email@domain.com' --repo $repo"
Write-Host "  gh secret set SMTP_PASSWORD --body 'your-password' --repo $repo"

Write-Host ""
Write-Host "🚀 GitHub Secrets setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "- Replace 'YOUR_KEY' with actual values if not set from environment"
Write-Host "- Test deployment with: gh workflow run deploy.yml"
Write-Host "- Monitor deployment in GitHub Actions"
Write-Host ""
Write-Host "🔗 VM Details:" -ForegroundColor Cyan
Write-Host "- IP: 74.248.141.31"
Write-Host "- Location: Poland Central"
Write-Host "- Performance: 30ms latency from Israel"
Write-Host "- Cost: `$57/month"
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Verify secrets are set: gh secret list --repo $repo"
Write-Host "2. Test deployment: gh workflow run deploy.yml --repo $repo"
Write-Host "3. Check application: http://74.248.141.31"
Write-Host "4. Monitor logs: ssh azureuser@74.248.141.31"
Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green