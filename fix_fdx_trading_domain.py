#!/usr/bin/env python
"""
Complete fix for fdx.trading domain and Azure deployment
"""
import subprocess
import time
import os
import zipfile
import tempfile
import shutil

def run_az_command(cmd, description, timeout=60):
    """Run Azure CLI command with proper error handling"""
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    full_cmd = [az_path] + cmd
    
    print(f"\n🔄 {description}...")
    print(f"Command: {' '.join(full_cmd)}")
    
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return result.stdout.strip()
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out")
        return None
    except Exception as e:
        print(f"❌ {description} exception: {e}")
        return None

def create_deployment_package():
    """Create a fresh deployment package"""
    print("\n📦 Creating deployment package...")
    
    # Files to include in deployment
    include_files = [
        'app/',
        'requirements.txt',
        'runtime.txt',
        'startup.sh',
        'startup_wsgi.txt',
        'sentry_config.py',
        'sentry_optimized_config.py',
        'sentry_middleware.py',
        'wsgi.py',
        'start.py',
        'foodxchange.db'
    ]
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy files to temp directory
        for item in include_files:
            if os.path.exists(item):
                if os.path.isdir(item):
                    shutil.copytree(item, os.path.join(temp_dir, item))
                else:
                    shutil.copy2(item, temp_dir)
        
        # Create zip file
        zip_path = 'foodxchange_deployment_fresh.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Deployment package created: {zip_path}")
        return zip_path

def fix_azure_deployment():
    """Fix the Azure deployment and configure custom domain"""
    print("=== Complete fdx.trading Domain Fix ===")
    
    # Configuration
    resource_group = "foodxchange-rg"
    app_name = "foodxchange-app"
    plan_name = "foodxchange-plan"
    location = "East US"
    domain = "fdx.trading"
    www_domain = "www.fdx.trading"
    
    # Step 1: Check if logged in to Azure
    if not run_az_command(['account', 'show'], "Checking Azure login"):
        print("❌ Please run 'az login' first to authenticate with Azure")
        return False
    
    # Step 2: Check if resource group exists, create if not
    group_info = run_az_command(['group', 'show', '--name', resource_group], 
                               "Checking resource group")
    if not group_info:
        print(f"Creating resource group {resource_group}...")
        run_az_command(['group', 'create', '--name', resource_group, '--location', location], 
                      "Creating resource group")
    
    # Step 3: Check if app service plan exists, create if not
    plan_info = run_az_command(['appservice', 'plan', 'show', '--name', plan_name, 
                               '--resource-group', resource_group], 
                              "Checking app service plan")
    if not plan_info:
        run_az_command(['appservice', 'plan', 'create', '--name', plan_name, 
                       '--resource-group', resource_group, '--sku', 'B1', '--is-linux'], 
                      "Creating app service plan")
    
    # Step 4: Check if web app exists, create if not
    app_info = run_az_command(['webapp', 'show', '--name', app_name, 
                              '--resource-group', resource_group], 
                             "Checking web app")
    if not app_info:
        run_az_command(['webapp', 'create', '--resource-group', resource_group, 
                       '--plan', plan_name, '--name', app_name, '--runtime', 'PYTHON:3.12'], 
                      "Creating web app")
    
    # Step 5: Create fresh deployment package
    zip_path = create_deployment_package()
    
    # Step 6: Deploy the application
    run_az_command(['webapp', 'deployment', 'source', 'config-zip', 
                   '--resource-group', resource_group, '--name', app_name, '--src', zip_path], 
                  "Deploying application")
    
    # Step 7: Configure startup command
    startup_command = "gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app"
    run_az_command(['webapp', 'config', 'set', '--resource-group', resource_group, 
                   '--name', app_name, '--startup-file', startup_command], 
                  "Setting startup command")
    
    # Step 8: Set environment variables
    env_vars = [
        "DATABASE_URL=sqlite:///./foodxchange.db",
        "SECRET_KEY=dev-secret-key-change-in-production",
        "ENVIRONMENT=production",
        "DEBUG=False",
        "BACKEND_CORS_ORIGINS=https://fdx.trading,https://www.fdx.trading,http://localhost:3000,http://localhost:8000"
    ]
    
    for env_var in env_vars:
        key, value = env_var.split('=', 1)
        run_az_command(['webapp', 'config', 'appsettings', 'set', '--resource-group', resource_group, 
                       '--name', app_name, '--settings', f"{key}={value}"], 
                      f"Setting {key}")
    
    # Step 9: Enable HTTPS only
    run_az_command(['webapp', 'update', '--resource-group', resource_group, 
                   '--name', app_name, '--https-only', 'true'], 
                  "Enabling HTTPS only")
    
    # Step 10: Add custom domains
    print(f"\n🌐 Adding custom domain: {domain}")
    run_az_command(['webapp', 'config', 'hostname', 'add', '--webapp-name', app_name, 
                   '--resource-group', resource_group, '--hostname', domain], 
                  f"Adding domain {domain}")
    
    print(f"🌐 Adding custom domain: {www_domain}")
    run_az_command(['webapp', 'config', 'hostname', 'add', '--webapp-name', app_name, 
                   '--resource-group', resource_group, '--hostname', www_domain], 
                  f"Adding domain {www_domain}")
    
    # Step 11: Get outbound IP addresses for DNS configuration
    print("\n📋 Getting outbound IP addresses for DNS configuration...")
    outbound_ips = run_az_command(['webapp', 'show', '--name', app_name, 
                                  '--resource-group', resource_group, 
                                  '--query', 'outboundIpAddresses', '--output', 'tsv'], 
                                 "Getting outbound IP addresses")
    
    # Step 12: Restart the app
    run_az_command(['webapp', 'restart', '--resource-group', resource_group, 
                   '--name', app_name], 
                  "Restarting app")
    
    # Step 13: Get the app URL
    hostname = run_az_command(['webapp', 'show', '--resource-group', resource_group, 
                              '--name', app_name, '--query', 'defaultHostName', '--output', 'tsv'], 
                             "Getting app URL")
    
    if hostname:
        print(f"\n🎉 Deployment and domain configuration completed successfully!")
        print(f"🌐 Azure URL: https://{hostname}")
        print(f"🌐 Custom domain: https://{domain}")
        print(f"🌐 WWW domain: https://{www_domain}")
        print(f"🔍 Health check: https://{hostname}/health")
        print(f"📊 System status: https://{hostname}/system-status")
        
        if outbound_ips:
            print(f"\n📋 DNS Configuration Required:")
            print(f"Add these A records in your Namecheap DNS settings:")
            for ip in outbound_ips.split(','):
                print(f"  Type: A, Name: @, Value: {ip.strip()}")
            print(f"  Type: CNAME, Name: www, Value: {domain}")
        
        print(f"\n⏳ Please wait 5-10 minutes for changes to take effect.")
        print(f"🔒 SSL certificates will be automatically provisioned.")
        
        return True
    else:
        print("❌ Failed to get app URL")
        return False

def test_domain():
    """Test the domain after configuration"""
    print("\n🧪 Testing domain configuration...")
    
    import urllib.request
    import urllib.error
    
    domains_to_test = [
        "https://foodxchange-app.azurewebsites.net",
        "https://fdx.trading",
        "https://www.fdx.trading"
    ]
    
    for domain in domains_to_test:
        try:
            print(f"Testing {domain}...")
            response = urllib.request.urlopen(domain, timeout=10)
            if response.getcode() == 200:
                print(f"✅ {domain} is working!")
            else:
                print(f"⚠️ {domain} returned status code: {response.getcode()}")
        except urllib.error.URLError as e:
            print(f"❌ {domain} failed: {e}")
        except Exception as e:
            print(f"❌ {domain} error: {e}")

if __name__ == "__main__":
    print("🚀 Starting complete fdx.trading domain fix...")
    
    if fix_azure_deployment():
        print("\n⏳ Waiting 2 minutes before testing...")
        time.sleep(120)
        test_domain()
    else:
        print("❌ Fix failed. Please check the error messages above.") 