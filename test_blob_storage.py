#!/usr/bin/env python3
"""
Test Azure Blob Storage Functionality
"""

import json
from azure.storage.blob import BlobServiceClient
import tempfile
import os

def test_blob_storage():
    """Test Azure Blob Storage functionality"""
    print("=== Testing Azure Blob Storage ===")
    
    # Load configuration
    try:
        with open("azure_blob_config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Configuration file not found. Run check_blob_status.py first.")
        return False
    
    # Create blob service client
    try:
        blob_service_client = BlobServiceClient.from_connection_string(config["connection_string"])
        print("✅ Connected to Azure Blob Storage")
    except Exception as e:
        print(f"❌ Failed to connect to Azure Blob Storage: {e}")
        return False
    
    # Test container access
    containers = ["uploads", "documents", "images", "exports"]
    for container_name in containers:
        try:
            container_client = blob_service_client.get_container_client(container_name)
            properties = container_client.get_container_properties()
            print(f"✅ Container '{container_name}' is accessible")
        except Exception as e:
            print(f"❌ Failed to access container '{container_name}': {e}")
            return False
    
    # Test upload and download
    test_container = "uploads"
    test_blob_name = "test_file.txt"
    test_content = "Hello from FoodXchange Azure Blob Storage!"
    
    try:
        # Upload test file
        container_client = blob_service_client.get_container_client(test_container)
        blob_client = container_client.get_blob_client(test_blob_name)
        
        blob_client.upload_blob(test_content, overwrite=True)
        print(f"✅ Uploaded test file to {test_container}/{test_blob_name}")
        
        # Download and verify
        downloaded_content = blob_client.download_blob().readall().decode('utf-8')
        if downloaded_content == test_content:
            print("✅ Download and verification successful")
        else:
            print("❌ Content verification failed")
            return False
        
        # Clean up test file
        blob_client.delete_blob()
        print("✅ Test file cleaned up")
        
    except Exception as e:
        print(f"❌ Test upload/download failed: {e}")
        return False
    
    print("\n=== Test Summary ===")
    print("✅ Azure Blob Storage is working correctly!")
    print(f"Storage Account: {config['storage_account_name']}")
    print(f"Blob Endpoint: {config['blob_endpoint']}")
    print(f"Containers: {', '.join(config['containers'])}")
    
    return True

if __name__ == "__main__":
    test_blob_storage() 