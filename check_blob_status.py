#!/usr/bin/env python3
"""
Check Azure Blob Storage Status and Setup Containers
"""

import subprocess
import json
import sys

def run_azure_command(command):
    """Run Azure CLI command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error running command: {command}")
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception running command: {e}")
        return None

def main():
    print("=== Azure Blob Storage Status Check ===")
    
    # Storage account details
    storage_account = "foodxchangeblob2025"
    resource_group = "foodxchange-rg"
    
    # Check if storage account exists
    print(f"Checking storage account: {storage_account}")
    account_info = run_azure_command(f'az storage account show --name {storage_account} --resource-group {resource_group}')
    
    if not account_info:
        print("❌ Storage account not found or error occurred")
        return
    
    print("✅ Storage account found!")
    
    # Get connection string
    print("Getting connection string...")
    connection_string = run_azure_command(f'az storage account show-connection-string --name {storage_account} --resource-group {resource_group}')
    
    if connection_string:
        conn_data = json.loads(connection_string)
        print(f"✅ Connection string: {conn_data['connectionString'][:50]}...")
    else:
        print("❌ Failed to get connection string")
        return
    
    # Get storage account key
    print("Getting storage account key...")
    keys = run_azure_command(f'az storage account keys list --account-name {storage_account} --resource-group {resource_group}')
    
    if keys:
        keys_data = json.loads(keys)
        key1 = keys_data[0]['value']
        print(f"✅ Storage key: {key1[:10]}...")
    else:
        print("❌ Failed to get storage keys")
        return
    
    # Check existing containers
    print("Checking existing containers...")
    containers = run_azure_command(f'az storage container list --account-name {storage_account} --account-key {key1}')
    
    if containers:
        containers_data = json.loads(containers)
        print(f"✅ Found {len(containers_data)} containers:")
        for container in containers_data:
            print(f"  - {container['name']}")
    else:
        print("No containers found or error occurred")
    
    # Create containers if they don't exist
    required_containers = ["uploads", "documents", "images", "exports"]
    print(f"Creating required containers: {required_containers}")
    
    for container in required_containers:
        print(f"Creating container: {container}")
        result = run_azure_command(f'az storage container create --name {container} --account-name {storage_account} --account-key {key1}')
        if result:
            print(f"✅ Container '{container}' created successfully")
        else:
            print(f"⚠️ Container '{container}' may already exist or failed to create")
    
    # Save configuration
    config = {
        "storage_account_name": storage_account,
        "resource_group": resource_group,
        "connection_string": conn_data['connectionString'],
        "storage_key": key1,
        "containers": required_containers,
        "blob_endpoint": f"https://{storage_account}.blob.core.windows.net/"
    }
    
    with open("azure_blob_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("\n=== Configuration Summary ===")
    print(f"Storage Account: {storage_account}")
    print(f"Resource Group: {resource_group}")
    print(f"Blob Endpoint: https://{storage_account}.blob.core.windows.net/")
    print(f"Containers: {', '.join(required_containers)}")
    print(f"Config saved to: azure_blob_config.json")
    print("\n✅ Azure Blob Storage is ready to use!")

if __name__ == "__main__":
    main() 