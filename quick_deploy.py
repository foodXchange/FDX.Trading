#!/usr/bin/env python3
"""
Ultra-Simple Azure Deployment Script
Run this script to deploy your app to Azure in one command
"""

import subprocess
import sys
import os
import json

def run_command(command, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e.stderr}")
        return None

def main():
    print("🚀 Ultra-Simple Azure Deployment")
    print("=" * 40)
    
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
    
    # Get deployment info
    print("\n📝 Deployment Configuration:")
    resource_group = input("Resource group name (e.g., foodxchange-rg): ").strip()
    app_name = input("Web app name (e.g., foodxchange-app): ").strip()
    
    if not resource_group or not app_name:
        print("❌ Resource group and app name are required.")
        return
    
    # Install dependencies
    print(f"\n📦 Installing dependencies...")
    if run_command("pip install -r requirements.txt"):
        print("✅ Dependencies installed")
    else:
        print("❌ Failed to install dependencies")
        return
    
    # Deploy
    print(f"\n🚀 Deploying to {app_name}...")
    deploy_cmd = f"az webapp deployment source config-zip --resource-group {resource_group} --name {app_name} --src ."
    
    if run_command(deploy_cmd):
        print("✅ Deployment successful!")
        print(f"🌐 Your app is available at: https://{app_name}.azurewebsites.net")
        
        # Optional restart
        restart = input("\n🔄 Do you want to restart the app? (y/n): ").strip().lower()
        if restart == 'y':
            print("🔄 Restarting app...")
            if run_command(f"az webapp restart --name {app_name} --resource-group {resource_group}"):
                print("✅ App restarted!")
    else:
        print("❌ Deployment failed!")

if __name__ == "__main__":
    main() 