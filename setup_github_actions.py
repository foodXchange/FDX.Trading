#!/usr/bin/env python3
"""
GitHub Actions Setup for FoodXchange
Helps you set up automatic deployment to Azure via GitHub Actions
"""

import subprocess
import json
import os

def run_command(command, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return None

def check_azure_cli():
    """Check if Azure CLI is installed and logged in"""
    print("🔍 Checking Azure CLI...")
    
    # Check if Azure CLI is installed
    az_version = run_command("az version --output json")
    if not az_version:
        print("❌ Azure CLI not found. Please install it first.")
        print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False
    
    # Check if logged in
    account = run_command("az account show --output json")
    if not account:
        print("❌ Not logged in to Azure. Please run 'az login' first.")
        return False
    
    account_data = json.loads(account)
    print(f"✅ Logged in as: {account_data.get('user', {}).get('name', 'Unknown')}")
    return True

def create_azure_resources():
    """Create Azure resources for deployment"""
    print("\n🔧 Creating Azure resources...")
    
    # Get resource names
    resource_group = input("Resource group name (e.g., foodxchange-rg): ").strip() or "foodxchange-rg"
    app_name = input("Web app name (e.g., foodxchange-app): ").strip() or "foodxchange-app"
    location = input("Location (e.g., East US): ").strip() or "East US"
    
    # Fix location format - ensure proper Azure location format
    location_lower = location.lower().replace(" ", "")
    if "westeurope" in location_lower:
        location = "West Europe"
    elif "eastus" in location_lower:
        location = "East US"
    elif "westus" in location_lower:
        location = "West US"
    elif "northeurope" in location_lower:
        location = "North Europe"
    elif "southeastasia" in location_lower:
        location = "Southeast Asia"
    
    print(f"\nCreating resources:")
    print(f"  Resource Group: {resource_group}")
    print(f"  App Name: {app_name}")
    print(f"  Location: {location}")
    
    # Create resource group
    print("\n📁 Creating resource group...")
    if not run_command(f"az group create --name {resource_group} --location \"{location}\""):
        print("❌ Failed to create resource group")
        return None
    
    # Create app service plan
    plan_name = f"{app_name}-plan"
    print(f"📋 Creating app service plan: {plan_name}")
    if not run_command(f"az appservice plan create --name {plan_name} --resource-group {resource_group} --sku B1 --is-linux"):
        print("❌ Failed to create app service plan")
        return None
    
    # Create web app
    print(f"🌐 Creating web app: {app_name}")
    if not run_command(f"az webapp create --name {app_name} --resource-group {resource_group} --plan {plan_name} --runtime \"PYTHON|3.12\""):
        print("❌ Failed to create web app")
        return None
    
    return {
        "resource_group": resource_group,
        "app_name": app_name,
        "location": location
    }

def configure_app_settings(resource_group, app_name):
    """Configure Azure app settings"""
    print("\n⚙️ Configuring app settings...")
    
    # Basic settings
    settings = {
        "SCM_DO_BUILD_DURING_DEPLOYMENT": "true",
        "PYTHON_VERSION": "3.12",
        "WEBSITES_PORT": "8000",
        "ENVIRONMENT": "production",
        "DEBUG": "False"
    }
    
    # Build settings string
    settings_str = " ".join([f"{k}=\"{v}\"" for k, v in settings.items()])
    
    if run_command(f"az webapp config appsettings set --name {app_name} --resource-group {resource_group} --settings {settings_str}"):
        print("✅ App settings configured")
        return True
    else:
        print("❌ Failed to configure app settings")
        return False

def get_publish_profile(resource_group, app_name):
    """Get the publish profile for GitHub Actions"""
    print("\n📋 Getting publish profile...")
    
    profile = run_command(f"az webapp deployment list-publishing-profiles --name {app_name} --resource-group {resource_group} --xml")
    if profile:
        print("✅ Publish profile retrieved")
        return profile
    else:
        print("❌ Failed to get publish profile")
        return None

def show_next_steps(resource_group, app_name, publish_profile):
    """Show the next steps for GitHub setup"""
    print("\n🎉 Azure resources created successfully!")
    print("\n📋 Next steps for GitHub Actions setup:")
    print("=" * 50)
    
    print("\n1. 📝 Copy the publish profile below:")
    print("-" * 30)
    print(publish_profile)
    print("-" * 30)
    
    print("\n2. 🔐 Add GitHub Secret:")
    print("   - Go to your GitHub repository")
    print("   - Click Settings → Secrets and variables → Actions")
    print("   - Click 'New repository secret'")
    print("   - Name: AZURE_WEBAPP_PUBLISH_PROFILE")
    print("   - Value: Paste the XML above")
    
    print("\n3. 🚀 Your workflow is ready!")
    print("   - Push to GitHub: git push origin main")
    print("   - GitHub Actions will automatically deploy to Azure")
    print(f"   - Your app will be at: https://{app_name}.azurewebsites.net")
    
    print("\n4. 🔧 Optional: Configure environment variables")
    print(f"   az webapp config appsettings set --name {app_name} --resource-group {resource_group} --settings DATABASE_URL=\"your-db-connection\"")
    print(f"   az webapp config appsettings set --name {app_name} --resource-group {resource_group} --settings SECRET_KEY=\"your-secret-key\"")

def main():
    print("🚀 GitHub Actions + Azure Setup")
    print("=" * 40)
    print()
    print("This will set up automatic deployment from GitHub to Azure")
    print()
    
    # Check prerequisites
    if not check_azure_cli():
        return
    
    # Create Azure resources
    resources = create_azure_resources()
    if not resources:
        return
    
    # Configure app settings
    if not configure_app_settings(resources["resource_group"], resources["app_name"]):
        return
    
    # Get publish profile
    publish_profile = get_publish_profile(resources["resource_group"], resources["app_name"])
    if not publish_profile:
        return
    
    # Show next steps
    show_next_steps(resources["resource_group"], resources["app_name"], publish_profile)
    
    print("\n🎯 Your development workflow:")
    print("1. Develop locally: start-local.bat")
    print("2. Deploy to Azure: git push origin main")
    print("3. Your app is live automatically!")

if __name__ == "__main__":
    main() 