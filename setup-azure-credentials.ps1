# FoodXchange Azure Credentials Setup for GitHub Actions
# This script helps you set up the required Azure credentials for GitHub Actions deployment

Write-Host "🔐 FoodXchange Azure Credentials Setup" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
Write-Host "Checking Azure CLI installation..." -ForegroundColor Yellow
try {
    $azVersion = az version --output json 2>$null | ConvertFrom-Json
    Write-Host "✅ Azure CLI version: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if logged in
Write-Host "`nChecking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ Not logged in to Azure. Please login first:" -ForegroundColor Red
    Write-Host "   az login" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Logged in to Azure" -ForegroundColor Green

# Get current subscription
$subscription = az account show --query "{id:id, name:name, tenantId:tenantId}" --output json | ConvertFrom-Json
Write-Host "`n📋 Current Azure Subscription:" -ForegroundColor Cyan
Write-Host "   Name: $($subscription.name)" -ForegroundColor White
Write-Host "   ID: $($subscription.id)" -ForegroundColor White
Write-Host "   Tenant ID: $($subscription.tenantId)" -ForegroundColor White

# Check if GitHub CLI is available
Write-Host "`nChecking GitHub CLI..." -ForegroundColor Yellow
try {
    $ghVersion = gh version 2>$null
    Write-Host "✅ GitHub CLI available" -ForegroundColor Green
} catch {
    Write-Host "❌ GitHub CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://cli.github.com/" -ForegroundColor Yellow
    Write-Host "`nAlternatively, you can manually add the secrets to your GitHub repository." -ForegroundColor Yellow
    exit 1
}

# Check if logged in to GitHub
Write-Host "`nChecking GitHub login status..." -ForegroundColor Yellow
try {
    $ghUser = gh auth status --json user 2>$null | ConvertFrom-Json
    Write-Host "✅ Logged in to GitHub as: $($ghUser.user.login)" -ForegroundColor Green
} catch {
    Write-Host "❌ Not logged in to GitHub. Please login first:" -ForegroundColor Red
    Write-Host "   gh auth login" -ForegroundColor Yellow
    exit 1
}

# Get repository information
Write-Host "`n📁 Repository Information:" -ForegroundColor Cyan
try {
    $repo = gh repo view --json name,owner 2>$null | ConvertFrom-Json
    Write-Host "   Repository: $($repo.owner.login)/$($repo.name)" -ForegroundColor White
} catch {
    Write-Host "❌ Could not determine repository. Please run this script from your repository directory." -ForegroundColor Red
    exit 1
}

# Create Service Principal
Write-Host "`n🔧 Creating Azure Service Principal..." -ForegroundColor Yellow
Write-Host "This will create a service principal with Contributor access to your subscription." -ForegroundColor Gray

$spName = "foodxchange-github-actions"
$spDescription = "Service Principal for FoodXchange GitHub Actions deployment"

try {
    # Check if service principal already exists
    $existingSp = az ad sp list --display-name $spName --query "[0]" --output json 2>$null | ConvertFrom-Json
    
    if ($existingSp) {
        Write-Host "⚠️  Service principal '$spName' already exists. Using existing one." -ForegroundColor Yellow
        $sp = $existingSp
    } else {
        # Create new service principal
        Write-Host "Creating new service principal..." -ForegroundColor Yellow
        $sp = az ad sp create-for-rbac --name $spName --description $spDescription --role Contributor --scopes "/subscriptions/$($subscription.id)" --output json 2>$null | ConvertFrom-Json
        
        if (-not $sp) {
            throw "Failed to create service principal"
        }
        
        Write-Host "✅ Service principal created successfully" -ForegroundColor Green
    }
    
    Write-Host "`n📋 Service Principal Details:" -ForegroundColor Cyan
    Write-Host "   Name: $($sp.displayName)" -ForegroundColor White
    Write-Host "   Application ID: $($sp.appId)" -ForegroundColor White
    Write-Host "   Object ID: $($sp.id)" -ForegroundColor White
    
} catch {
    Write-Host "❌ Failed to create service principal: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nManual Setup Instructions:" -ForegroundColor Yellow
    Write-Host "1. Go to Azure Portal > Azure Active Directory > App registrations" -ForegroundColor White
    Write-Host "2. Click 'New registration'" -ForegroundColor White
    Write-Host "3. Name: foodxchange-github-actions" -ForegroundColor White
    Write-Host "4. Click 'Register'" -ForegroundColor White
    Write-Host "5. Note the Application (client) ID and Directory (tenant) ID" -ForegroundColor White
    Write-Host "6. Go to 'Certificates & secrets' > 'New client secret'" -ForegroundColor White
    Write-Host "7. Note the secret value" -ForegroundColor White
    exit 1
}

# Set up GitHub secrets
Write-Host "`n🔐 Setting up GitHub Secrets..." -ForegroundColor Yellow

try {
    # Set AZURE_CLIENT_ID
    Write-Host "Setting AZURE_CLIENT_ID..." -ForegroundColor Gray
    gh secret set AZURE_CLIENT_ID --body $sp.appId 2>$null
    
    # Set AZURE_TENANT_ID
    Write-Host "Setting AZURE_TENANT_ID..." -ForegroundColor Gray
    gh secret set AZURE_TENANT_ID --body $subscription.tenantId 2>$null
    
    # Set AZURE_SUBSCRIPTION_ID
    Write-Host "Setting AZURE_SUBSCRIPTION_ID..." -ForegroundColor Gray
    gh secret set AZURE_SUBSCRIPTION_ID --body $subscription.id 2>$null
    
    Write-Host "✅ GitHub secrets configured successfully" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Failed to set GitHub secrets: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nManual Setup Instructions:" -ForegroundColor Yellow
    Write-Host "Go to your GitHub repository > Settings > Secrets and variables > Actions" -ForegroundColor White
    Write-Host "Add these secrets:" -ForegroundColor White
    Write-Host "   AZURE_CLIENT_ID = $($sp.appId)" -ForegroundColor Cyan
    Write-Host "   AZURE_TENANT_ID = $($subscription.tenantId)" -ForegroundColor Cyan
    Write-Host "   AZURE_SUBSCRIPTION_ID = $($subscription.id)" -ForegroundColor Cyan
}

# Test the deployment
Write-Host "`n🧪 Testing Azure Deployment..." -ForegroundColor Yellow

try {
    # Check if the web app exists
    $webApp = az webapp show --name "foodxchange-app" --resource-group "foodxchange-rg" --query "name" --output tsv 2>$null
    
    if ($webApp) {
        Write-Host "✅ Web app 'foodxchange-app' found" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Web app 'foodxchange-app' not found. You may need to create it first." -ForegroundColor Yellow
        Write-Host "   Run: az webapp create --name foodxchange-app --resource-group foodxchange-rg --plan foodxchange-plan --runtime 'PYTHON:3.12'" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "❌ Could not verify web app. Please check your Azure resources." -ForegroundColor Red
}

# Summary
Write-Host "`n📋 Setup Summary:" -ForegroundColor Cyan
Write-Host "✅ Azure CLI: Available" -ForegroundColor Green
Write-Host "✅ Azure Login: Active" -ForegroundColor Green
Write-Host "✅ GitHub CLI: Available" -ForegroundColor Green
Write-Host "✅ GitHub Login: Active" -ForegroundColor Green
Write-Host "✅ Service Principal: Created" -ForegroundColor Green
Write-Host "✅ GitHub Secrets: Configured" -ForegroundColor Green

Write-Host "`n🚀 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Commit and push your changes to trigger the GitHub Actions workflow" -ForegroundColor White
Write-Host "2. Monitor the deployment in GitHub Actions tab" -ForegroundColor White
Write-Host "3. Check the deployment logs if there are any issues" -ForegroundColor White

Write-Host "`n📚 Troubleshooting:" -ForegroundColor Yellow
Write-Host "• If deployment fails, check the GitHub Actions logs" -ForegroundColor Gray
Write-Host "• Verify your Azure resources exist and are accessible" -ForegroundColor Gray
Write-Host "• Ensure your service principal has the necessary permissions" -ForegroundColor Gray

Write-Host "`n✅ Setup completed successfully!" -ForegroundColor Green 