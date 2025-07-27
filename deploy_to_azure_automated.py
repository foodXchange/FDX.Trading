#!/usr/bin/env python
"""
Automated Azure deployment script
Uploads the fixed package and configures Azure App Service
"""
import os
import subprocess
import sys
import time
import requests
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return None

def check_azure_cli():
    """Check if Azure CLI is installed and logged in"""
    print("🔍 Checking Azure CLI...")
    
    # Check if Azure CLI is installed
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    if not os.path.exists(az_path):
        print("❌ Azure CLI not found. Please install it first:")
        print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Check if logged in
    result = run_command([az_path, 'account', 'show'], "Checking Azure login", check=False)
    if result is None or result.returncode != 0:
        print("❌ Not logged in to Azure. Please run 'az login' first")
        return False
    
    return True

def deploy_to_azure():
    """Deploy the fixed package to Azure"""
    print("🚀 Starting automated Azure deployment...")
    
    # Configuration
    resource_group = "foodxchange-rg"
    app_name = "foodxchange-app"
    plan_name = "foodxchange-plan"
    location = "East US"
    zip_path = "foodxchange_deployment_fixed.zip"
    
    # Check if deployment package exists
    if not os.path.exists(zip_path):
        print(f"❌ Deployment package not found: {zip_path}")
        print("Please run 'python deploy_azure_fixed.py' first to create the package")
        return False
    
    # Use full path to Azure CLI
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    
    # Check Azure CLI
    if not check_azure_cli():
        return False
    
    print(f"\n📦 Deploying package: {zip_path}")
    print(f"📊 Package size: {os.path.getsize(zip_path) / (1024*1024):.2f} MB")
    
    # Deploy using ZIP deploy
    print("\n🔄 Uploading package to Azure...")
    deploy_cmd = [
        az_path, 'webapp', 'deployment', 'source', 'config-zip',
        '--resource-group', resource_group,
        '--name', app_name,
        '--src', zip_path
    ]
    
    result = run_command(deploy_cmd, "Uploading deployment package")
    if result is None:
        return False
    
    # Configure startup command
    print("\n⚙️ Configuring startup command...")
    startup_cmd = [
        az_path, 'webapp', 'config', 'set',
        '--resource-group', resource_group,
        '--name', app_name,
        '--startup-file', 'gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app'
    ]
    
    result = run_command(startup_cmd, "Setting startup command")
    if result is None:
        return False
    
    # Configure Python version
    print("\n🐍 Configuring Python version...")
    python_cmd = [
        az_path, 'webapp', 'config', 'set',
        '--resource-group', resource_group,
        '--name', app_name,
        '--linux-fx-version', 'PYTHON:3.12'
    ]
    
    result = run_command(python_cmd, "Setting Python version")
    if result is None:
        return False
    
    # Set environment variables
    print("\n🔧 Configuring environment variables...")
    env_vars = [
        'DATABASE_URL=sqlite:///./foodxchange.db',
        'SECRET_KEY=dev-secret-key-change-in-production',
        'ENVIRONMENT=production',
        'DEBUG=False'
    ]
    
    for env_var in env_vars:
        key, value = env_var.split('=', 1)
        env_cmd = [
            az_path, 'webapp', 'config', 'appsettings', 'set',
            '--resource-group', resource_group,
            '--name', app_name,
            '--settings', f'{key}={value}'
        ]
        
        result = run_command(env_cmd, f"Setting {key}")
        if result is None:
            return False
    
    # Restart the app
    print("\n🔄 Restarting the application...")
    restart_cmd = [
        az_path, 'webapp', 'restart',
        '--resource-group', resource_group,
        '--name', app_name
    ]
    
    result = run_command(restart_cmd, "Restarting application")
    if result is None:
        return False
    
    # Get the app URL
    print("\n🌐 Getting application URL...")
    url_cmd = [
        az_path, 'webapp', 'show',
        '--resource-group', resource_group,
        '--name', app_name,
        '--query', 'defaultHostName',
        '-o', 'tsv'
    ]
    
    result = run_command(url_cmd, "Getting app URL")
    if result is None:
        return False
    
    hostname = result.stdout.strip()
    app_url = f"https://{hostname}"
    
    print(f"\n🎉 Deployment completed successfully!")
    print(f"🌐 Your app is available at: {app_url}")
    print(f"🔍 Health check: {app_url}/health")
    print(f"📊 System status: {app_url}/system-status")
    
    # Wait a moment and test the deployment
    print("\n⏳ Waiting for application to start...")
    time.sleep(30)
    
    # Test the health endpoint
    print("\n🧪 Testing deployment...")
    try:
        health_url = f"{app_url}/health"
        response = requests.get(health_url, timeout=30)
        if response.status_code == 200:
            print(f"✅ Health check passed: {health_url}")
            print(f"Response: {response.text}")
        else:
            print(f"⚠️ Health check returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Health check failed: {e}")
        print("The app may still be starting up. Please wait a few minutes and try again.")
    
    return True

def main():
    """Main deployment function"""
    print("=== Automated Azure Deployment ===")
    print("This script will:")
    print("1. Upload the fixed deployment package")
    print("2. Configure startup command")
    print("3. Set Python version to 3.12")
    print("4. Configure environment variables")
    print("5. Restart the application")
    print("6. Test the deployment")
    
    # Check if deployment package exists
    if not os.path.exists("foodxchange_deployment_fixed.zip"):
        print("\n❌ Deployment package not found!")
        print("Creating deployment package first...")
        
        create_cmd = [sys.executable, "deploy_azure_fixed.py"]
        result = subprocess.run(create_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Failed to create deployment package")
            print(f"Error: {result.stderr}")
            return False
    
    # Deploy to Azure
    success = deploy_to_azure()
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print("Your FoodXchange application should now be running on Azure.")
    else:
        print("\n❌ Deployment failed. Please check the error messages above.")
        return False

if __name__ == "__main__":
    main() 