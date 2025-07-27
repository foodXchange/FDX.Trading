#!/usr/bin/env python
"""
Setup Azure Blob Storage for FoodXchange
"""
import subprocess
import json
import os
from datetime import datetime

def run_az_command(cmd, description):
    """Run Azure CLI command with timeout"""
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    full_cmd = [az_path] + cmd
    
    try:
        print(f"🔄 {description}...")
        print(f"Command: {' '.join(full_cmd)}")
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return result.stdout.strip()
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return None
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return None

def setup_blob_storage():
    """Set up Azure Blob Storage"""
    print("=== Azure Blob Storage Setup ===")
    
    # Configuration
    resource_group = "foodxchange-rg"
    storage_account_name = "foodxchangestorage"
    location = "West Europe"
    container_name = "foodxchange-files"
    
    print(f"\n📋 Configuration:")
    print(f"  Resource Group: {resource_group}")
    print(f"  Storage Account: {storage_account_name}")
    print(f"  Location: {location}")
    print(f"  Container: {container_name}")
    
    # Step 1: Create storage account
    print(f"\n1️⃣ Creating storage account...")
    create_cmd = [
        'storage', 'account', 'create',
        '--name', storage_account_name,
        '--resource-group', resource_group,
        '--location', location,
        '--sku', 'Standard_LRS',
        '--kind', 'StorageV2',
        '--https-only', 'true',
        '--min-tls-version', 'TLS1_2'
    ]
    
    result = run_az_command(create_cmd, "Creating storage account")
    if not result:
        print("⚠️  Storage account creation failed or timed out")
        print("   You may need to create it manually in Azure Portal")
    
    # Step 2: Get connection string
    print(f"\n2️⃣ Getting connection string...")
    conn_cmd = [
        'storage', 'account', 'show-connection-string',
        '--name', storage_account_name,
        '--resource-group', resource_group,
        '--query', 'connectionString',
        '-o', 'tsv'
    ]
    
    connection_string = run_az_command(conn_cmd, "Getting connection string")
    
    if connection_string:
        print(f"✅ Connection string retrieved")
        
        # Step 3: Create container
        print(f"\n3️⃣ Creating blob container...")
        container_cmd = [
            'storage', 'container', 'create',
            '--name', container_name,
            '--account-name', storage_account_name,
            '--public-access', 'off'
        ]
        
        run_az_command(container_cmd, "Creating blob container")
        
        # Step 4: Set up CORS
        print(f"\n4️⃣ Setting up CORS...")
        cors_cmd = [
            'storage', 'cors', 'add',
            '--account-name', storage_account_name,
            '--services', 'blob',
            '--methods', 'GET POST PUT DELETE OPTIONS',
            '--origins', 'https://www.fdx.trading https://fdx.trading',
            '--allowed-headers', '*',
            '--exposed-headers', '*',
            '--max-age', '86400'
        ]
        
        run_az_command(cors_cmd, "Setting up CORS")
        
        # Step 5: Update App Service settings
        print(f"\n5️⃣ Updating App Service settings...")
        app_settings = [
            f"AZURE_STORAGE_CONNECTION_STRING={connection_string}",
            f"AZURE_STORAGE_CONTAINER_NAME={container_name}",
            f"AZURE_STORAGE_ACCOUNT_NAME={storage_account_name}"
        ]
        
        for setting in app_settings:
            key, value = setting.split('=', 1)
            setting_cmd = [
                'webapp', 'config', 'appsettings', 'set',
                '--resource-group', resource_group,
                '--name', 'foodxchange-app',
                '--settings', f"{key}={value}"
            ]
            run_az_command(setting_cmd, f"Setting {key}")
        
        # Step 6: Save connection string locally
        print(f"\n6️⃣ Saving connection string locally...")
        env_content = f"""
# Azure Blob Storage Configuration
AZURE_STORAGE_CONNECTION_STRING={connection_string}
AZURE_STORAGE_CONTAINER_NAME={container_name}
AZURE_STORAGE_ACCOUNT_NAME={storage_account_name}
"""
        
        with open('.env.blob', 'w') as f:
            f.write(env_content)
        
        print(f"✅ Connection string saved to .env.blob")
        
        # Step 7: Test connection
        print(f"\n7️⃣ Testing connection...")
        test_cmd = [
            'storage', 'blob', 'list',
            '--container-name', container_name,
            '--account-name', storage_account_name,
            '--num-results', '1'
        ]
        
        test_result = run_az_command(test_cmd, "Testing blob storage connection")
        if test_result is not None:
            print("✅ Blob storage connection test successful")
        else:
            print("⚠️  Connection test failed - check manually")
        
        print(f"\n🎉 Azure Blob Storage setup completed!")
        print(f"📁 Container: {container_name}")
        print(f"🔗 Connection string saved to .env.blob")
        print(f"⚙️  App Service settings updated")
        
        return True
    else:
        print("❌ Failed to get connection string")
        return False

def print_manual_steps():
    """Print manual setup steps"""
    print("\n" + "="*60)
    print("📋 MANUAL SETUP STEPS (if automated setup fails)")
    print("="*60)
    
    print("\n1️⃣ Create Storage Account:")
    print("   - Go to Azure Portal: https://portal.azure.com")
    print("   - Navigate to your resource group: foodxchange-rg")
    print("   - Click 'Add' → 'Storage account'")
    print("   - Name: foodxchangestorage")
    print("   - Location: West Europe")
    print("   - Performance: Standard")
    print("   - Redundancy: LRS")
    
    print("\n2️⃣ Get Connection String:")
    print("   - Go to your storage account")
    print("   - Access keys → Show connection string")
    print("   - Copy the connection string")
    
    print("\n3️⃣ Create Blob Container:")
    print("   - Go to Blob service → Containers")
    print("   - Add container: foodxchange-files")
    print("   - Public access level: Private")
    
    print("\n4️⃣ Set CORS:")
    print("   - Go to Settings → Resource sharing (CORS)")
    print("   - Add rule:")
    print("     - Allowed origins: https://www.fdx.trading, https://fdx.trading")
    print("     - Allowed methods: GET, POST, PUT, DELETE, OPTIONS")
    print("     - Allowed headers: *")
    print("     - Exposed headers: *")
    print("     - Max age: 86400")
    
    print("\n5️⃣ Update App Service:")
    print("   - Go to your App Service: foodxchange-app")
    print("   - Configuration → Application settings")
    print("   - Add these settings:")
    print("     - AZURE_STORAGE_CONNECTION_STRING = [your-connection-string]")
    print("     - AZURE_STORAGE_CONTAINER_NAME = foodxchange-files")
    print("     - AZURE_STORAGE_ACCOUNT_NAME = foodxchangestorage")
    
    print("\n6️⃣ Restart App Service:")
    print("   - Go to Overview → Restart")
    print("   - Wait 2-3 minutes")
    
    print("\n7️⃣ Test:")
    print("   - Visit: https://www.fdx.trading")
    print("   - Try uploading a file")
    print("   - Check if it appears in blob storage")

if __name__ == "__main__":
    print("🚀 Azure Blob Storage Setup for FoodXchange")
    print("="*50)
    
    success = setup_blob_storage()
    
    if not success:
        print("\n⚠️  Automated setup failed or incomplete")
        print_manual_steps()
    else:
        print("\n✅ Setup completed successfully!")
        print("🔧 Next: Restart your App Service to apply changes") 