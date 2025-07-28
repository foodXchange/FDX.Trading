#!/usr/bin/env python3
"""
Development Setup Script for FoodXchange
Manages hybrid local/Azure development workflow
"""

import os
import subprocess
import json
from pathlib import Path

def run_command(command, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return None

def setup_local_dev():
    """Set up local development environment"""
    print("🔧 Setting up local development environment...")
    
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
""")
        print("✅ Created .env.local for local development")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    if run_command("pip install -r requirements.txt"):
        print("✅ Dependencies installed")
    
    # Initialize database
    print("🗄️ Setting up local database...")
    if run_command("python -c \"from foodxchange.database import init_db; init_db()\""):
        print("✅ Local database initialized")
    
    print("\n🎉 Local development environment ready!")
    print("Run: python -m uvicorn foodxchange.main:app --reload")

def setup_azure_dev():
    """Set up Azure development environment"""
    print("☁️ Setting up Azure development environment...")
    
    # Check Azure CLI
    if not run_command("az version --output json"):
        print("❌ Azure CLI not found. Please install it first.")
        return
    
    # Check login
    if not run_command("az account show --output json"):
        print("❌ Not logged in to Azure. Please run 'az login' first.")
        return
    
    print("✅ Azure development environment ready!")
    print("Run: python azure_deploy.py to deploy")

def create_dev_scripts():
    """Create development convenience scripts"""
    print("📝 Creating development scripts...")
    
    # Create start-local.bat
    start_local_bat = Path("start-local.bat")
    start_local_bat.write_text("""@echo off
echo 🚀 Starting FoodXchange Local Development Server
echo ================================================
echo.
echo Loading local environment...
set ENV_FILE=.env.local
echo.
echo Starting server with auto-reload...
python -m uvicorn foodxchange.main:app --reload --host 0.0.0.0 --port 8000
pause
""")
    
    # Create start-local.sh
    start_local_sh = Path("start-local.sh")
    start_local_sh.write_text("""#!/bin/bash
echo "🚀 Starting FoodXchange Local Development Server"
echo "================================================"
echo ""
echo "Loading local environment..."
export ENV_FILE=.env.local
echo ""
echo "Starting server with auto-reload..."
python -m uvicorn foodxchange.main:app --reload --host 0.0.0.0 --port 8000
""")
    os.chmod(start_local_sh, 0o755)
    
    # Create quick-deploy.bat
    quick_deploy_bat = Path("quick-deploy.bat")
    quick_deploy_bat.write_text("""@echo off
echo 🚀 Quick Deploy to Azure
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
""")
    
    print("✅ Development scripts created:")
    print("  - start-local.bat (Windows)")
    print("  - start-local.sh (Linux/Mac)")
    print("  - quick-deploy.bat (Quick Azure deployment)")

def show_dev_workflow():
    """Show the recommended development workflow"""
    print("\n🔄 Recommended Development Workflow")
    print("=" * 40)
    print()
    print("1. 🏠 LOCAL DEVELOPMENT (Cursor)")
    print("   - Edit code in Cursor")
    print("   - Run: start-local.bat")
    print("   - Auto-reload on changes")
    print("   - Fast iteration")
    print()
    print("2. ☁️ AZURE TESTING")
    print("   - When ready to test Azure features")
    print("   - Run: quick-deploy.bat")
    print("   - Test in production-like environment")
    print()
    print("3. 🔄 ITERATE")
    print("   - Back to local development")
    print("   - Repeat as needed")
    print()
    print("📁 File Structure:")
    print("  .env.local          - Local development settings")
    print("  .env.azure          - Azure production settings")
    print("  start-local.bat     - Start local server")
    print("  quick-deploy.bat    - Deploy to Azure")

def main():
    print("🚀 FoodXchange Development Setup")
    print("=" * 40)
    print()
    print("This will set up your development environment for:")
    print("✅ Local development in Cursor")
    print("✅ Azure deployment and testing")
    print("✅ Hybrid workflow management")
    print()
    
    choice = input("Choose setup option:\n1. Full setup (local + Azure)\n2. Local only\n3. Azure only\n4. Show workflow\nChoice (1-4): ").strip()
    
    if choice == "1":
        setup_local_dev()
        setup_azure_dev()
        create_dev_scripts()
        show_dev_workflow()
    elif choice == "2":
        setup_local_dev()
        create_dev_scripts()
    elif choice == "3":
        setup_azure_dev()
    elif choice == "4":
        show_dev_workflow()
    else:
        print("❌ Invalid choice")
        return
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Start local development: start-local.bat")
    print("2. Deploy to Azure: quick-deploy.bat")
    print("3. Check the workflow guide above")

if __name__ == "__main__":
    main() 