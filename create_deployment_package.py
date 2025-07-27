#!/usr/bin/env python
"""
Create a deployment package for manual upload to Azure
"""
import os
import zipfile
import shutil
import tempfile

def create_deployment_package():
    """Create a deployment package for Azure"""
    print("=== Creating Azure Deployment Package ===")
    
    # Files to include in deployment
    include_files = [
        'app/',
        'requirements.txt',
        'runtime.txt',
        'startup.sh',
        'startup_wsgi.txt',
        'startup.txt',
        'web.config',
        'sentry_config.py',
        'sentry_optimized_config.py',
        'sentry_middleware.py',
        'wsgi.py',
        'start.py',
        'startup.py',
        'foodxchange.db'
    ]
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Copy files to temp directory
        for item in include_files:
            if os.path.exists(item):
                if os.path.isdir(item):
                    print(f"Copying directory: {item}")
                    shutil.copytree(item, os.path.join(temp_dir, item))
                else:
                    print(f"Copying file: {item}")
                    shutil.copy2(item, temp_dir)
            else:
                print(f"Warning: {item} not found")
        
        # Create zip file
        zip_path = 'foodxchange_deployment.zip'
        print(f"\nCreating deployment package: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
                    print(f"  Added: {arcname}")
        
        # Get file size
        file_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
        print(f"\nDeployment package created successfully!")
        print(f"File size: {file_size:.2f} MB")
        print(f"Location: {os.path.abspath(zip_path)}")
        
        return zip_path

def print_deployment_instructions():
    """Print instructions for manual deployment"""
    print("\n" + "="*60)
    print("MANUAL DEPLOYMENT INSTRUCTIONS")
    print("="*60)
    
    print("\n**Step 1: Upload Package**")
    print("1. Go to Azure Portal: https://portal.azure.com")
    print("2. Navigate to your App Service: foodxchange-app")
    print("3. Go to 'Deployment Center'")
    print("4. Choose 'Manual deployment' or 'Zip Deploy'")
    print("5. Upload the file: foodxchange_deployment.zip")
    
    print("\n**Step 2: Configure App Settings**")
    print("1. Go to 'Configuration' -> 'Application settings'")
    print("2. Add these settings:")
    print("   - DATABASE_URL = sqlite:///./foodxchange.db")
    print("   - SECRET_KEY = dev-secret-key-change-in-production")
    print("   - ENVIRONMENT = production")
    print("   - DEBUG = False")
    
    print("\n**Step 3: Set Startup Command**")
    print("1. Go to 'Configuration' -> 'General settings'")
    print("2. Set Startup Command to:")
    print("   gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app")
    
    print("\n**Step 4: Set Python Version**")
    print("1. In 'Configuration' -> 'General settings'")
    print("2. Set Stack to: Python")
    print("3. Set Major version to: 3.12")
    
    print("\n**Step 5: Restart and Test**")
    print("1. Go to 'Overview' and click 'Restart'")
    print("2. Wait 2-3 minutes")
    print("3. Test your app: http://www.fdx.trading/")
    print("4. Check health: http://www.fdx.trading/health")
    
    print("\n" + "="*60)
    print("Your deployment package is ready!")
    print("="*60)

if __name__ == "__main__":
    try:
        zip_path = create_deployment_package()
        print_deployment_instructions()
    except Exception as e:
        print(f"Error creating deployment package: {e}")
        import traceback
        traceback.print_exc() 