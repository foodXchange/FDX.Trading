#!/usr/bin/env python3
"""
Comprehensive Azure Deployment Script for FoodXchange
Handles FastAPI deployment to Azure App Service with all necessary configurations
"""

import subprocess
import sys
import os
import json
import zipfile
import shutil
from pathlib import Path

def run_command(command, check=True, capture_output=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=capture_output, text=True, check=check)
        return result.stdout.strip() if capture_output else result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        if capture_output:
            print(f"Error: {e.stderr}")
        return None

def create_deployment_package():
    """Create a deployment package with all necessary files"""
    print("📦 Creating deployment package...")
    
    # Files to include in deployment
    include_files = [
        'foodxchange/',
        'requirements.txt',
        'web.config',
        'index.py',
        'static/',
        'templates/',
        'migrations/',
        'docs/',
        'Fonts/',
        'Logo/',
        'Photos/'
    ]
    
    # Create deployment directory
    deploy_dir = Path("azure_deployment")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Copy files
    for item in include_files:
        src = Path(item)
        dst = deploy_dir / item
        
        if src.exists():
            if src.is_file():
                shutil.copy2(src, dst)
            else:
                shutil.copytree(src, dst, dirs_exist_ok=True)
    
    # Create startup script for Azure
    startup_script = deploy_dir / "startup.sh"
    startup_script.write_text("""#!/bin/bash
cd /home/site/wwwroot
python -m uvicorn foodxchange.main:app --host 0.0.0.0 --port $PORT
""")
    os.chmod(startup_script, 0o755)
    
    # Create runtime.txt
    runtime_file = deploy_dir / "runtime.txt"
    runtime_file.write_text("python-3.12")
    
    # Create .deployment file
    deployment_file = deploy_dir / ".deployment"
    deployment_file.write_text("""[config]
SCM_DO_BUILD_DURING_DEPLOYMENT=true
""")
    
    print("✅ Deployment package created")
    return deploy_dir

def setup_azure_resources(resource_group, app_name, location="East US"):
    """Set up Azure resources if they don't exist"""
    print(f"🔧 Setting up Azure resources...")
    
    # Check if resource group exists
    rg_exists = run_command(f"az group show --name {resource_group}", check=False)
    if not rg_exists:
        print(f"📁 Creating resource group: {resource_group}")
        if not run_command(f"az group create --name {resource_group} --location {location}"):
            return False
    
    # Check if app service plan exists
    plan_name = f"{app_name}-plan"
    plan_exists = run_command(f"az appservice plan show --name {plan_name} --resource-group {resource_group}", check=False)
    if not plan_exists:
        print(f"📋 Creating app service plan: {plan_name}")
        if not run_command(f"az appservice plan create --name {plan_name} --resource-group {resource_group} --sku B1 --is-linux"):
            return False
    
    # Check if web app exists
    app_exists = run_command(f"az webapp show --name {app_name} --resource-group {resource_group}", check=False)
    if not app_exists:
        print(f"🌐 Creating web app: {app_name}")
        if not run_command(f"az webapp create --name {app_name} --resource-group {resource_group} --plan {plan_name} --runtime \"PYTHON|3.12\""):
            return False
    
    return True

def configure_app_settings(resource_group, app_name, database_url=None):
    """Configure app settings and environment variables"""
    print("⚙️ Configuring app settings...")
    
    # Base settings
    settings = {
        "SCM_DO_BUILD_DURING_DEPLOYMENT": "true",
        "PYTHON_VERSION": "3.12",
        "WEBSITES_PORT": "8000",
        "ENVIRONMENT": "production",
        "DEBUG": "False"
    }
    
    # Add database URL if provided
    if database_url:
        settings["DATABASE_URL"] = database_url
    
    # Build settings string
    settings_str = " ".join([f"{k}=\"{v}\"" for k, v in settings.items()])
    
    # Apply settings
    if run_command(f"az webapp config appsettings set --name {app_name} --resource-group {resource_group} --settings {settings_str}"):
        print("✅ App settings configured")
        return True
    else:
        print("❌ Failed to configure app settings")
        return False

def deploy_to_azure(resource_group, app_name, deploy_dir):
    """Deploy the application to Azure"""
    print(f"🚀 Deploying to Azure...")
    
    # Create zip file
    zip_path = f"{app_name}-deployment.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"📦 Created deployment package: {zip_path}")
    
    # Deploy using Azure CLI
    if run_command(f"az webapp deployment source config-zip --resource-group {resource_group} --name {app_name} --src {zip_path}"):
        print("✅ Deployment successful!")
        return True
    else:
        print("❌ Deployment failed!")
        return False

def verify_deployment(app_name):
    """Verify the deployment by checking the health endpoint"""
    print("🔍 Verifying deployment...")
    
    import time
    import requests
    
    # Wait for app to start
    print("⏳ Waiting for app to start...")
    time.sleep(30)
    
    # Check health endpoint
    try:
        response = requests.get(f"https://{app_name}.azurewebsites.net/health", timeout=30)
        if response.status_code == 200:
            print("✅ Deployment verified! App is responding.")
            print(f"🌐 Your app is available at: https://{app_name}.azurewebsites.net")
            return True
        else:
            print(f"⚠️ App responded with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not verify deployment: {e}")
        return False

def main():
    print("🚀 FoodXchange Azure Deployment")
    print("=" * 50)
    
    # Check Azure CLI
    print("📋 Checking Azure CLI...")
    az_version = run_command("az version --output json")
    if not az_version:
        print("❌ Azure CLI not found. Please install it first.")
        print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return
    
    # Check login
    print("🔐 Checking Azure login...")
    account = run_command("az account show --output json")
    if not account:
        print("❌ Not logged in to Azure. Please run 'az login' first.")
        return
    
    account_data = json.loads(account)
    print(f"✅ Logged in as: {account_data.get('user', {}).get('name', 'Unknown')}")
    
    # Get deployment configuration
    print("\n📝 Deployment Configuration:")
    resource_group = input("Resource group name (e.g., foodxchange-rg): ").strip()
    app_name = input("Web app name (e.g., foodxchange-app): ").strip()
    database_url = input("Database URL (optional, press Enter to skip): ").strip()
    
    if not resource_group or not app_name:
        print("❌ Resource group and app name are required.")
        return
    
    # Create deployment package
    deploy_dir = create_deployment_package()
    
    # Setup Azure resources
    if not setup_azure_resources(resource_group, app_name):
        print("❌ Failed to setup Azure resources")
        return
    
    # Configure app settings
    if not configure_app_settings(resource_group, app_name, database_url if database_url else None):
        print("❌ Failed to configure app settings")
        return
    
    # Deploy
    if not deploy_to_azure(resource_group, app_name, deploy_dir):
        print("❌ Deployment failed")
        return
    
    # Verify deployment
    verify_deployment(app_name)
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    zip_path = f"{app_name}-deployment.zip"
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    print("\n🎉 Deployment completed!")
    print(f"🌐 Your FoodXchange app is now running at: https://{app_name}.azurewebsites.net")
    print("\n📋 Next steps:")
    print("1. Set up your database connection string in Azure App Settings")
    print("2. Configure your domain and SSL certificate")
    print("3. Set up monitoring and logging")
    print("4. Configure your environment variables")

if __name__ == "__main__":
    main() 