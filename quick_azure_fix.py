#!/usr/bin/env python
"""
Quick fix for Azure deployment - updates configuration without full redeployment
"""
import subprocess
import sys

def run_azure_command(cmd, description):
    """Run an Azure CLI command"""
    print(f"\n🔄 {description}...")
    # Use full path to Azure CLI
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    try:
        result = subprocess.run([az_path] + cmd, capture_output=True, text=True, check=True, timeout=30)
        print(f"✅ {description} completed")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out")
        return None

def quick_fix():
    """Apply quick fixes to Azure deployment"""
    print("=== Quick Azure Fix ===")
    
    # Configuration
    resource_group = "foodxchange-rg"
    app_name = "foodxchange-app"
    
    # Check if app exists
    app_info = run_azure_command(['webapp', 'show', '--resource-group', resource_group, '--name', app_name], 
                                "Checking if app exists")
    
    if not app_info:
        print(f"❌ App {app_name} not found in resource group {resource_group}")
        print("Please check your Azure configuration or run the full deployment script.")
        return False
    
    # Fix 1: Update startup command
    startup_command = "gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app"
    run_azure_command(['webapp', 'config', 'set', '--resource-group', resource_group, 
                      '--name', app_name, '--startup-file', startup_command], 
                     "Updating startup command")
    
    # Fix 2: Set Python version
    run_azure_command(['webapp', 'config', 'set', '--resource-group', resource_group, 
                      '--name', app_name, '--linux-fx-version', 'PYTHON:3.12'], 
                     "Setting Python version")
    
    # Fix 3: Set environment variables
    env_vars = [
        "DATABASE_URL=sqlite:///./foodxchange.db",
        "SECRET_KEY=dev-secret-key-change-in-production",
        "ENVIRONMENT=production",
        "DEBUG=False"
    ]
    
    for env_var in env_vars:
        key, value = env_var.split('=', 1)
        run_azure_command(['webapp', 'config', 'appsettings', 'set', '--resource-group', resource_group, 
                          '--name', app_name, '--settings', f"{key}={value}"], 
                         f"Setting {key}")
    
    # Fix 4: Restart the app
    run_azure_command(['webapp', 'restart', '--resource-group', resource_group, '--name', app_name], 
                     "Restarting app")
    
    # Get the app URL
    hostname = run_azure_command(['webapp', 'show', '--resource-group', resource_group, 
                                '--name', app_name, '--query', 'defaultHostName', '-o', 'tsv'], 
                               "Getting app URL")
    
    if hostname:
        app_url = f"https://{hostname}"
        print(f"\n🎉 Quick fix applied successfully!")
        print(f"🌐 Your app should now be available at: {app_url}")
        print(f"🔍 Health check: {app_url}/health")
        print(f"📊 System status: {app_url}/system-status")
        print(f"\n⏳ Please wait 2-3 minutes for the changes to take effect.")
        return True
    else:
        print("❌ Failed to get app URL")
        return False

if __name__ == "__main__":
    quick_fix() 