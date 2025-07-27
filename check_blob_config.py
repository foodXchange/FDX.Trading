#!/usr/bin/env python
"""
Check Azure Blob Storage Configuration
"""
import os

def check_configuration():
    """Check if blob storage is configured"""
    print("=== Azure Blob Storage Configuration Check ===")
    
    # Check environment variables
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    
    print(f"\n📋 Environment Variables:")
    print(f"  AZURE_STORAGE_CONNECTION_STRING: {'✅ Set' if connection_string else '❌ Not set'}")
    print(f"  AZURE_STORAGE_CONTAINER_NAME: {'✅ Set' if container_name else '❌ Not set'}")
    print(f"  AZURE_STORAGE_ACCOUNT_NAME: {'✅ Set' if account_name else '❌ Not set'}")
    
    if connection_string:
        print(f"\n🔗 Connection String (first 50 chars): {connection_string[:50]}...")
    
    # Check if Azure storage package is installed
    try:
        import azure.storage.blob
        print(f"\n📦 Azure Storage Package: ✅ Installed")
    except ImportError:
        print(f"\n📦 Azure Storage Package: ❌ Not installed")
        print("   Run: pip install azure-storage-blob")
    
    # Test blob storage service
    try:
        from app.services.blob_storage_service import BlobStorageService
        
        blob_service = BlobStorageService()
        
        if blob_service.blob_service_client:
            print(f"\n🔧 Blob Storage Service: ✅ Initialized")
            print(f"   Account: {blob_service.account_name}")
        else:
            print(f"\n🔧 Blob Storage Service: ❌ Not initialized")
            print("   Check connection string and container name")
        
    except Exception as e:
        print(f"\n🔧 Blob Storage Service: ❌ Error: {e}")
    
    # Check .env.blob file
    if os.path.exists('.env.blob'):
        print(f"\n📄 .env.blob file: ✅ Exists")
        with open('.env.blob', 'r') as f:
            content = f.read()
            print(f"   Content length: {len(content)} characters")
    else:
        print(f"\n📄 .env.blob file: ❌ Not found")
    
    print(f"\n" + "="*50)
    print("📊 Summary:")
    
    if connection_string and container_name and account_name:
        print("✅ Configuration looks good!")
        print("🔧 Next: Test the connection")
    else:
        print("❌ Configuration incomplete")
        print("🔧 Run: python setup_azure_blob_storage.py")

if __name__ == "__main__":
    check_configuration() 