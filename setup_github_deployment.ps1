# GitHub Actions Deployment Setup Script
Write-Host "=== FoodXchange GitHub Actions Setup ===" -ForegroundColor Green

# Check if git is initialized
if (!(Test-Path .git)) {
    Write-Host "Initializing Git repository..." -ForegroundColor Yellow
    git init
}

# Create comprehensive .gitignore
Write-Host "Creating .gitignore..." -ForegroundColor Yellow
@"
# Python
*.pyc
__pycache__/
venv/
env/
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment files
.env
.env.*
!.env.example

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Azure
.deployment
.azure/
*.zip
deployment_contents/
emergency_deployment/
minimal_deploy/

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db

# Backup files
*.backup
*.bak
"@ | Set-Content .gitignore

# Create requirements.txt with all dependencies
Write-Host "Updating requirements.txt..." -ForegroundColor Yellow
@"
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0

# Database
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0

# Email
python-email-validator==2.1.0

# Templates
Jinja2==3.1.2

# Azure
azure-storage-blob==12.19.0
openai==1.3.0

# Monitoring
sentry-sdk[fastapi]==1.38.0
psutil==5.9.6

# Utilities
requests==2.31.0
pydantic==2.5.0
pydantic-settings==2.1.0
"@ | Set-Content requirements.txt

# Create a simple startup.py that works
Write-Host "Creating startup.py..." -ForegroundColor Yellow
@"
import os
import sys
from pathlib import Path

# Add app directory to path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

try:
    from app.main import app
    print("FastAPI app imported successfully")
except Exception as e:
    print(f"Failed to import app: {e}")
    # Create fallback app
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def root():
        return {"status": "fallback", "error": str(e)}
    
    @app.get("/health")
    def health():
        return {"status": "fallback"}

# For Azure App Service
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
"@ | Set-Content startup.py

# Download publish profile
Write-Host "`nSTEP 1: Download Azure Publish Profile" -ForegroundColor Cyan
Write-Host "1. Go to: https://portal.azure.com" -ForegroundColor Yellow
Write-Host "2. Navigate to: App Services > foodxchange-app" -ForegroundColor Yellow
Write-Host "3. Click 'Get publish profile' and save the file" -ForegroundColor Yellow
Write-Host "4. Press Enter when done..." -ForegroundColor Green
Read-Host

# Get publish profile path
$profilePath = Read-Host "Enter the path to your publish profile file"
if (Test-Path $profilePath) {
    $publishProfile = Get-Content $profilePath -Raw
    Write-Host "Publish profile loaded successfully!" -ForegroundColor Green
} else {
    Write-Host "File not found. You'll need to add it manually to GitHub." -ForegroundColor Red
    $publishProfile = $null
}

# Initialize git and create first commit
Write-Host "`nCreating initial commit..." -ForegroundColor Yellow
git add .
git commit -m "Initial commit with GitHub Actions workflow" 2>$null

# GitHub repository setup
Write-Host "`nSTEP 2: Create GitHub Repository" -ForegroundColor Cyan
Write-Host "1. Go to: https://github.com/new" -ForegroundColor Yellow
Write-Host "2. Repository name: FoodXchange" -ForegroundColor Yellow
Write-Host "3. Make it Private or Public as needed" -ForegroundColor Yellow
Write-Host "4. DON'T initialize with README, .gitignore, or license" -ForegroundColor Yellow
Write-Host "5. Click 'Create repository'" -ForegroundColor Yellow
Write-Host "6. Press Enter when done..." -ForegroundColor Green
Read-Host

# Get GitHub username
$githubUsername = Read-Host "Enter your GitHub username"
$repoUrl = "https://github.com/$githubUsername/FoodXchange.git"

# Add remote
Write-Host "`nAdding GitHub remote..." -ForegroundColor Yellow
git remote add origin $repoUrl 2>$null
git branch -M main

# Create a helper script for adding secrets
Write-Host "`nCreating helper script for GitHub secrets..." -ForegroundColor Yellow
@"
# GitHub Secrets Configuration

Go to: https://github.com/$githubUsername/FoodXchange/settings/secrets/actions/new

Add the following secret:
- Name: AZURE_WEBAPP_PUBLISH_PROFILE
- Value: (paste the entire content of the publish profile XML file)

Optional: Add these for enhanced monitoring:
- AZURE_OPENAI_API_KEY: f9061473a6754ec1b572f674d8b28b07
- AZURE_OPENAI_ENDPOINT: https://swedencentral.api.cognitive.microsoft.com/
- SENTRY_DSN: (your Sentry DSN if you have one)
"@ | Set-Content GITHUB_SECRETS_SETUP.txt

Write-Host "`nSTEP 3: Add GitHub Secrets" -ForegroundColor Cyan
Write-Host "Follow the instructions in GITHUB_SECRETS_SETUP.txt" -ForegroundColor Yellow
Write-Host "Press Enter when done..." -ForegroundColor Green
Read-Host

# Push to GitHub
Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSuccess! Your code is now on GitHub." -ForegroundColor Green
    Write-Host "`nThe deployment will start automatically." -ForegroundColor Cyan
    Write-Host "Monitor it at: https://github.com/$githubUsername/FoodXchange/actions" -ForegroundColor Yellow
    
    Write-Host "`nYour app will be available at:" -ForegroundColor Cyan
    Write-Host "- https://foodxchange-app.azurewebsites.net" -ForegroundColor Green
    Write-Host "- https://www.fdx.trading" -ForegroundColor Green
} else {
    Write-Host "`nPush failed. You may need to:" -ForegroundColor Red
    Write-Host "1. Check your GitHub credentials" -ForegroundColor Yellow
    Write-Host "2. Make sure the repository was created" -ForegroundColor Yellow
    Write-Host "3. Try: git push -u origin main --force" -ForegroundColor Yellow
}

Write-Host "`nSetup complete!" -ForegroundColor Green