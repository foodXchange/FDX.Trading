#!/usr/bin/env python3
"""
Simple Development Setup for FoodXchange
Sets up your local + Azure development environment
"""

import os
from pathlib import Path

def create_env_files():
    """Create environment files for local and Azure development"""
    print("Creating environment files...")
    
    # Create .env.local for local development
    env_local = Path(".env.local")
    if not env_local.exists():
        env_local.write_text("""# Local Development Environment
ENVIRONMENT=development
DEBUG=True
DATABASE_URL=sqlite:///./foodxchange_dev.db
SECRET_KEY=dev-secret-key-local-only
USE_HTTPS=False

# Azure OpenAI (optional for local dev)
# AZURE_OPENAI_API_KEY=your-key-here
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo
""", encoding='utf-8')
        print("Created .env.local")
    
    # Create .env.azure for Azure production
    env_azure = Path(".env.azure")
    if not env_azure.exists():
        env_azure.write_text("""# Azure Production Environment
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://username:password@server.postgres.database.azure.com:5432/database_name?sslmode=require
SECRET_KEY=your-production-secret-key-change-this
USE_HTTPS=True

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-openai-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4-turbo

# Azure App Service Specific
SCM_DO_BUILD_DURING_DEPLOYMENT=true
PYTHON_VERSION=3.12
WEBSITES_PORT=8000
""", encoding='utf-8')
        print("Created .env.azure")

def create_dev_scripts():
    """Create development convenience scripts"""
    print("Creating development scripts...")
    
    # Create start-local.bat
    start_local_bat = Path("start-local.bat")
    start_local_bat.write_text("""@echo off
echo Starting FoodXchange Local Development Server
echo ================================================
echo.
echo Loading local environment...
set ENV_FILE=.env.local
echo.
echo Starting server with auto-reload...
python -m uvicorn foodxchange.main:app --reload --host 0.0.0.0 --port 8000
pause
""", encoding='utf-8')
    print("Created start-local.bat")
    
    # Create quick-deploy.bat
    quick_deploy_bat = Path("quick-deploy.bat")
    quick_deploy_bat.write_text("""@echo off
echo Quick Deploy to Azure
echo =======================
echo.
echo This will deploy your current code to Azure for testing
echo.
set /p confirm="Continue? (y/N): "
if /i "%confirm%"=="y" (
    python azure_deploy.py
) else (
    echo Deployment cancelled.
)
pause
""", encoding='utf-8')
    print("Created quick-deploy.bat")

def show_workflow():
    """Show the recommended development workflow"""
    print("\nYour Development Workflow")
    print("=" * 40)
    print()
    print("1. LOCAL DEVELOPMENT (95% of time)")
    print("   - Edit code in Cursor")
    print("   - Run: start-local.bat")
    print("   - Auto-reload on changes")
    print("   - Fast iteration")
    print()
    print("2. AZURE TESTING (5% of time)")
    print("   - When ready to test Azure features")
    print("   - Run: quick-deploy.bat")
    print("   - Test in production-like environment")
    print()
    print("3. ITERATE")
    print("   - Back to local development")
    print("   - Repeat as needed")
    print()
    print("Files Created:")
    print("  .env.local          - Local development settings")
    print("  .env.azure          - Azure production settings")
    print("  start-local.bat     - Start local server")
    print("  quick-deploy.bat    - Deploy to Azure")

def main():
    print("FoodXchange Development Setup")
    print("=" * 40)
    print()
    print("Setting up your hybrid development environment...")
    print()
    
    create_env_files()
    create_dev_scripts()
    show_workflow()
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Start local development: start-local.bat")
    print("2. Deploy to Azure: quick-deploy.bat")
    print("3. Edit .env.local and .env.azure with your settings")
    print()
    print("Tip: Your Cursor development experience stays exactly the same!")

if __name__ == "__main__":
    main() 