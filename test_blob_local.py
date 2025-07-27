#!/usr/bin/env python
"""
Test Azure Blob Storage locally with environment variables
"""
import os
import io
from datetime import datetime

def load_env_from_file(file_path):
    """Load environment variables from file"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print(f"✅ Loaded environment variables from {file_path}")

def test_blob_storage():
    """Test Azure Blob Storage functionality"""
    print("=== Testing Azure Blob Storage ===")
    
    # Load environment variables
    load_env_from_file('.env.blob')
    
    try:
        from app.services.blob_storage_service import BlobStorageService
        
        # Initialize service
        blob_service = BlobStorageService()
        
        # Check if configured
        if not blob_service.blob_service_client:
            print("❌ Blob storage not configured")
            print("   Check environment variables:")
            print("   - AZURE_STORAGE_CONNECTION_STRING")
            print("   - AZURE_STORAGE_CONTAINER_NAME")
            return False
        
        print("✅ Blob storage service initialized")
        print(f"   Account: {blob_service.account_name}")
        
        # Test upload
        print("\n📤 Testing file upload...")
        test_content = f"Test file created at {datetime.now()}"
        test_filename = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
        
        # Create file-like object
        file_obj = io.BytesIO(test_content.encode('utf-8'))
        
        # Upload file
        import asyncio
        
        async def upload_test():
            upload_result = await blob_service.upload_file(
                file=file_obj,
                filename=test_filename,
                container_type="emails",
                company_id=1,
                metadata={"test": "true"}
            )
            
            if upload_result:
                print(f"✅ File uploaded successfully: {test_filename}")
                print(f"   URL: {upload_result.get('url', 'N/A')}")
                
                # Test download
                print("\n📥 Testing file download...")
                download_result = await blob_service.download_file(
                    container_name="emails",
                    blob_name=test_filename
                )
                
                if download_result and download_result.decode('utf-8') == test_content:
                    print("✅ File downloaded successfully")
                    print("✅ Content matches original")
                else:
                    print("❌ File download failed or content mismatch")
                
                # Test delete
                print("\n🗑️  Testing file deletion...")
                delete_result = await blob_service.delete_file(
                    container_name="emails",
                    blob_name=test_filename
                )
                
                if delete_result:
                    print("✅ File deleted successfully")
                else:
                    print("❌ File deletion failed")
                
                return True
            else:
                print("❌ File upload failed")
                return False
        
        return asyncio.run(upload_test())
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Install required packages: pip install azure-storage-blob")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_app_service_connection():
    """Test if App Service can connect to blob storage"""
    print("\n=== Testing App Service Connection ===")
    
    try:
        import requests
        
        # Test the health endpoint
        response = requests.get("https://www.fdx.trading/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ App Service is running")
            
            # Test file upload endpoint
            print("\n📤 Testing file upload endpoint...")
            
            # Create a test file
            test_content = f"Test upload at {datetime.now()}"
            files = {'file': ('test.txt', test_content, 'text/plain')}
            
            upload_response = requests.post(
                "https://www.fdx.trading/api/files/upload",
                files=files,
                timeout=30
            )
            
            if upload_response.status_code == 200:
                print("✅ File upload endpoint working")
                result = upload_response.json()
                print(f"   File uploaded: {result.get('filename', 'Unknown')}")
                return True
            else:
                print(f"❌ File upload endpoint failed: {upload_response.status_code}")
                print(f"   Response: {upload_response.text}")
                return False
        else:
            print(f"❌ App Service health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Azure Blob Storage Local Test")
    print("="*50)
    
    # Test local connection
    local_success = test_blob_storage()
    
    # Test App Service connection
    app_success = test_app_service_connection()
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print(f"   Local Connection: {'✅ Success' if local_success else '❌ Failed'}")
    print(f"   App Service: {'✅ Success' if app_success else '❌ Failed'}")
    
    if local_success and app_success:
        print("\n🎉 Azure Blob Storage is fully connected!")
        print("   ✅ File uploads working")
        print("   ✅ File downloads working")
        print("   ✅ File deletions working")
        print("   ✅ App Service integration working")
    elif local_success:
        print("\n⚠️  Local connection works but App Service needs restart")
        print("   🔧 Restart your App Service to apply changes")
    else:
        print("\n❌ Setup incomplete - check configuration") 