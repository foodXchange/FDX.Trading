#!/usr/bin/env python
"""
Simplified Azure deployment script
Uses basic uvicorn startup for better compatibility
"""
import os
import zipfile
import shutil
import tempfile
import subprocess
import sys

def create_simple_deployment_package():
    """Create a simplified deployment package for Azure"""
    print("=== Creating Simplified Azure Deployment Package ===")
    
    # Files to include in deployment (minimal set)
    include_files = [
        'app/',
        'requirements.txt',
        'runtime.txt',
        'startup_simple.py',
        'startup_simple.txt',
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
        zip_path = 'foodxchange_deployment_simple.zip'
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

def deploy_simple_to_azure():
    """Deploy the simplified package to Azure"""
    print("\n🚀 Deploying simplified package to Azure...")
    
    # Configuration
    resource_group = "foodxchange-rg"
    app_name = "foodxchange-app"
    zip_path = "foodxchange_deployment_simple.zip"
    
    # Use full path to Azure CLI
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    
    # Deploy using ZIP deploy
    print("🔄 Uploading simplified package to Azure...")
    deploy_cmd = [
        az_path, 'webapp', 'deploy',
        '--resource-group', resource_group,
        '--name', app_name,
        '--src-path', zip_path,
        '--type', 'zip'
    ]
    
    try:
        result = subprocess.run(deploy_cmd, capture_output=True, text=True, check=True)
        print("✅ Package uploaded successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload failed: {e.stderr}")
        return False
    
    # Configure startup command
    print("⚙️ Configuring startup command...")
    startup_cmd = [
        az_path, 'webapp', 'config', 'set',
        '--resource-group', resource_group,
        '--name', app_name,
        '--startup-file', 'python startup_simple.py'
    ]
    
    try:
        result = subprocess.run(startup_cmd, capture_output=True, text=True, check=True)
        print("✅ Startup command configured")
    except subprocess.CalledProcessError as e:
        print(f"❌ Startup configuration failed: {e.stderr}")
        return False
    
    # Set environment variables
    print("🔧 Configuring environment variables...")
    env_vars = [
        'DATABASE_URL=sqlite:///./foodxchange.db',
        'SECRET_KEY=dev-secret-key-change-in-production',
        'ENVIRONMENT=production',
        'DEBUG=False'
    ]
    
    for env_var in env_vars:
        key, value = env_var.split('=', 1)
        env_cmd = [
            az_path, 'webapp', 'config', 'appsettings', 'set',
            '--resource-group', resource_group,
            '--name', app_name,
            '--settings', f'{key}={value}'
        ]
        
        try:
            result = subprocess.run(env_cmd, capture_output=True, text=True, check=True)
            print(f"✅ Set {key}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to set {key}: {e.stderr}")
            return False
    
    # Restart the app
    print("🔄 Restarting the application...")
    restart_cmd = [
        az_path, 'webapp', 'restart',
        '--resource-group', resource_group,
        '--name', app_name
    ]
    
    try:
        result = subprocess.run(restart_cmd, capture_output=True, text=True, check=True)
        print("✅ Application restarted")
    except subprocess.CalledProcessError as e:
        print(f"❌ Restart failed: {e.stderr}")
        return False
    
    # Get the app URL
    print("🌐 Getting application URL...")
    url_cmd = [
        az_path, 'webapp', 'show',
        '--resource-group', resource_group,
        '--name', app_name,
        '--query', 'defaultHostName',
        '-o', 'tsv'
    ]
    
    try:
        result = subprocess.run(url_cmd, capture_output=True, text=True, check=True)
        hostname = result.stdout.strip()
        app_url = f"https://{hostname}"
        
        print(f"\n🎉 Simplified deployment completed!")
        print(f"🌐 Your app is available at: {app_url}")
        print(f"🔍 Health check: {app_url}/health")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get app URL: {e.stderr}")
        return False

def main():
    """Main deployment function"""
    print("=== Simplified Azure Deployment ===")
    print("This uses basic uvicorn startup for better compatibility")
    
    # Create deployment package
    zip_path = create_simple_deployment_package()
    
    # Deploy to Azure
    success = deploy_simple_to_azure()
    
    if success:
        print("\n✅ Simplified deployment completed successfully!")
        print("The application should now be running with basic uvicorn startup.")
    else:
        print("\n❌ Simplified deployment failed.")
        return False

if __name__ == "__main__":
    main() 