#!/usr/bin/env python
"""
Radically simple Azure deployment
Uses the most basic approach possible
"""
import os
import zipfile
import shutil
import tempfile
import subprocess

def create_minimal_package():
    """Create a minimal deployment package"""
    print("=== Creating Minimal Deployment Package ===")
    
    # Only include essential files
    include_files = [
        'app.py',  # Main application file
        'requirements_minimal.txt',  # Minimal requirements
        'runtime.txt',  # Python version
        'foodxchange.db'  # Database
    ]
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Copy essential files
        for item in include_files:
            if os.path.exists(item):
                print(f"Copying: {item}")
                shutil.copy2(item, temp_dir)
            else:
                print(f"Warning: {item} not found")
        
        # Copy app directory (essential)
        if os.path.exists('app'):
            print("Copying: app/")
            shutil.copytree('app', os.path.join(temp_dir, 'app'))
        
        # Create zip file
        zip_path = 'foodxchange_minimal.zip'
        print(f"\nCreating: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        file_size = os.path.getsize(zip_path) / (1024 * 1024)
        print(f"Package created: {file_size:.2f} MB")
        return zip_path

def deploy_minimal():
    """Deploy using the simplest possible approach"""
    print("\n🚀 Deploying minimal package...")
    
    # Configuration
    resource_group = "foodxchange-rg"
    app_name = "foodxchange-app"
    zip_path = "foodxchange_minimal.zip"
    
    # Use Azure CLI directly
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    
    # Step 1: Upload package
    print("📦 Uploading package...")
    deploy_cmd = [
        az_path, 'webapp', 'deploy',
        '--resource-group', resource_group,
        '--name', app_name,
        '--src-path', zip_path,
        '--type', 'zip'
    ]
    
    try:
        result = subprocess.run(deploy_cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ Package uploaded successfully")
        else:
            print(f"❌ Upload failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️ Upload timed out, but may have succeeded")
    
    # Step 2: Set startup command to the simplest possible
    print("⚙️ Setting startup command...")
    startup_cmd = [
        az_path, 'webapp', 'config', 'set',
        '--resource-group', resource_group,
        '--name', app_name,
        '--startup-file', 'python app.py'
    ]
    
    try:
        result = subprocess.run(startup_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Startup command set")
        else:
            print(f"⚠️ Startup command failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Startup command error: {e}")
    
    # Step 3: Set basic environment variables
    print("🔧 Setting environment variables...")
    env_vars = [
        'DATABASE_URL=sqlite:///./foodxchange.db',
        'SECRET_KEY=dev-secret-key',
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
            result = subprocess.run(env_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Set {key}")
            else:
                print(f"⚠️ Failed to set {key}")
        except Exception as e:
            print(f"⚠️ Error setting {key}: {e}")
    
    # Step 4: Restart
    print("🔄 Restarting application...")
    restart_cmd = [
        az_path, 'webapp', 'restart',
        '--resource-group', resource_group,
        '--name', app_name
    ]
    
    try:
        result = subprocess.run(restart_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Application restarted")
        else:
            print(f"⚠️ Restart failed: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Restart error: {e}")
    
    # Step 5: Get URL
    print("🌐 Getting application URL...")
    url_cmd = [
        az_path, 'webapp', 'show',
        '--resource-group', resource_group,
        '--name', app_name,
        '--query', 'defaultHostName',
        '-o', 'tsv'
    ]
    
    try:
        result = subprocess.run(url_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            hostname = result.stdout.strip()
            app_url = f"https://{hostname}"
            print(f"\n🎉 Deployment completed!")
            print(f"🌐 Your app: {app_url}")
            print(f"🔍 Health: {app_url}/health")
            print(f"📚 Docs: {app_url}/docs")
            return True
        else:
            print(f"❌ Failed to get URL: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error getting URL: {e}")
        return False

def main():
    """Main function"""
    print("=== Radical Azure Deployment ===")
    print("Using the simplest possible approach")
    
    # Create minimal package
    zip_path = create_minimal_package()
    
    # Deploy
    success = deploy_minimal()
    
    if success:
        print("\n✅ Radical deployment completed!")
        print("The application should now be running with minimal configuration.")
    else:
        print("\n❌ Radical deployment failed.")
        print("Check the Azure portal for more details.")

if __name__ == "__main__":
    main() 