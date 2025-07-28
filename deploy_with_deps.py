#!/usr/bin/env python3
"""
Create a deployment package with all dependencies for Azure
"""
import os
import zipfile
import shutil

def create_deployment_package():
    # Files to include
    files_to_deploy = [
        'minimal_app.py',
        'requirements.txt',
        'startup.sh',
        'web.config',
        'runtime.txt'
    ]
    
    # Create deployment directory
    deploy_dir = 'azure_deployment_package'
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    
    # Copy files
    for file in files_to_deploy:
        if os.path.exists(file):
            shutil.copy2(file, deploy_dir)
            print(f"Copied {file}")
    
    # Create a simple startup script that installs dependencies
    startup_content = '''#!/bin/bash
echo "Installing dependencies..."
pip install -r requirements.txt
echo "Starting application..."
python -m uvicorn minimal_app:app --host 0.0.0.0 --port $PORT
'''
    
    with open(os.path.join(deploy_dir, 'startup.sh'), 'w') as f:
        f.write(startup_content)
    
    # Create deployment zip
    zip_name = 'foodxchange_with_deps.zip'
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(deploy_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, deploy_dir)
                zipf.write(file_path, arcname)
    
    print(f"\nDeployment package created: {zip_name}")
    print("\nTo deploy:")
    print("1. Go to Azure Portal")
    print("2. Navigate to your App Service")
    print("3. Go to Deployment Center")
    print("4. Upload this zip file")
    
    # Clean up
    shutil.rmtree(deploy_dir)

if __name__ == "__main__":
    create_deployment_package()