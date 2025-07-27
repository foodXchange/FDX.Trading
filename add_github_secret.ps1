# Alternative script to add GitHub secret using file input

Write-Host "Setting up GitHub Actions secret for Azure deployment" -ForegroundColor Cyan
Write-Host ""

# Check if GitHub CLI is installed
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if (-not $ghInstalled) {
    Write-Host "GitHub CLI not found. Please install it from: https://cli.github.com/" -ForegroundColor Red
    exit 1
}

# Check current directory is a git repo
if (-not (Test-Path .git)) {
    Write-Host "Error: Not in a Git repository. Please run this from your FoodXchange directory." -ForegroundColor Red
    exit 1
}

# Check if publish profile exists
if (-not (Test-Path publish_profile.xml)) {
    Write-Host "Error: publish_profile.xml not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Using GitHub CLI to add secret from file..." -ForegroundColor Yellow

# Use file input method
try {
    Get-Content publish_profile.xml | gh secret set AZUREAPPSERVICE_PUBLISHPROFILE
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Secret added successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Cyan
        Write-Host "1. Commit and push your changes to trigger deployment" -ForegroundColor White
        Write-Host "   git add ." -ForegroundColor Gray
        Write-Host "   git commit -m 'Fix: Add email-validator dependency'" -ForegroundColor Gray
        Write-Host "   git push" -ForegroundColor Gray
        Write-Host ""
        Write-Host "2. Check the Actions tab in your GitHub repository" -ForegroundColor White
        Write-Host "3. The workflow will run automatically on push to main branch" -ForegroundColor White
    } else {
        throw "GitHub CLI command failed"
    }
} catch {
    Write-Host "Failed to add secret automatically." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please add it manually:" -ForegroundColor Yellow
    Write-Host "1. Copy the contents of publish_profile.xml" -ForegroundColor White
    Write-Host "2. Go to: https://github.com/[your-username]/FoodXchange/settings/secrets/actions" -ForegroundColor White
    Write-Host "3. Click 'New repository secret'" -ForegroundColor White
    Write-Host "4. Name: AZUREAPPSERVICE_PUBLISHPROFILE" -ForegroundColor White
    Write-Host "5. Value: Paste the XML content" -ForegroundColor White
    Write-Host "6. Click 'Add secret'" -ForegroundColor White
}