# PowerShell script to set up GitHub secret for deployment

Write-Host "Setting up GitHub Actions secret for Azure deployment" -ForegroundColor Cyan

# Read the publish profile
$publishProfile = Get-Content -Path "publish_profile.xml" -Raw

# Check if GitHub CLI is installed
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghInstalled) {
    Write-Host "GitHub CLI not found. Please install it from: https://cli.github.com/" -ForegroundColor Red
    Write-Host "After installation, run 'gh auth login' to authenticate" -ForegroundColor Yellow
    exit 1
}

# Check if authenticated
$authStatus = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Not authenticated with GitHub. Running 'gh auth login'..." -ForegroundColor Yellow
    gh auth login
}

# Get repository info
$repoInfo = gh repo view --json nameWithOwner 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Make sure you're in a Git repository directory" -ForegroundColor Red
    exit 1
}

# Set the secret
Write-Host "Adding AZUREAPPSERVICE_PUBLISHPROFILE secret to GitHub..." -ForegroundColor Yellow
gh secret set AZUREAPPSERVICE_PUBLISHPROFILE --body $publishProfile

if ($LASTEXITCODE -eq 0) {
    Write-Host "Secret added successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Commit and push your changes to trigger deployment"
    Write-Host "2. Check the Actions tab in your GitHub repository"
    Write-Host "3. The workflow 'deploy_with_publish_profile.yml' will run automatically"
} else {
    Write-Host "Failed to add secret. Please add it manually through GitHub web interface" -ForegroundColor Red
}