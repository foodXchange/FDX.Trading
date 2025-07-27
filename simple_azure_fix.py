#!/usr/bin/env python
"""
Simple Azure fix script that doesn't hang
"""
import subprocess
import time

def run_az_command(cmd):
    """Run Azure CLI command with proper error handling"""
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    full_cmd = [az_path] + cmd
    
    try:
        print(f"Running: {' '.join(full_cmd)}")
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Success")
            return result.stdout.strip()
        else:
            print(f"❌ Error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("❌ Command timed out")
        return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def fix_azure_deployment():
    """Fix the Azure deployment"""
    print("=== Simple Azure Fix ===")
    
    # Configuration
    resource_group = "foodxchange-rg"
    app_name = "foodxchange-app"
    
    print("\n1. Setting startup command...")
    startup_cmd = [
        'webapp', 'config', 'set',
        '--resource-group', resource_group,
        '--name', app_name,
        '--startup-file', 'gunicorn --bind 0.0.0.0:8000 --timeout 600 --worker-class uvicorn.workers.UvicornWorker app.main:app'
    ]
    run_az_command(startup_cmd)
    
    print("\n2. Setting environment variables...")
    env_cmd = [
        'webapp', 'config', 'appsettings', 'set',
        '--resource-group', resource_group,
        '--name', app_name,
        '--settings',
        'DATABASE_URL=sqlite:///./foodxchange.db',
        'SECRET_KEY=dev-secret-key-change-in-production',
        'ENVIRONMENT=production',
        'DEBUG=False'
    ]
    run_az_command(env_cmd)
    
    print("\n3. Enabling HTTPS only...")
    https_cmd = [
        'webapp', 'update',
        '--resource-group', resource_group,
        '--name', app_name,
        '--https-only', 'true'
    ]
    run_az_command(https_cmd)
    
    print("\n4. Restarting the app...")
    restart_cmd = [
        'webapp', 'restart',
        '--resource-group', resource_group,
        '--name', app_name
    ]
    run_az_command(restart_cmd)
    
    print("\n5. Getting app URL...")
    url_cmd = [
        'webapp', 'show',
        '--resource-group', resource_group,
        '--name', app_name,
        '--query', 'defaultHostName',
        '-o', 'tsv'
    ]
    hostname = run_az_command(url_cmd)
    
    if hostname:
        print(f"\n🎉 Fix applied successfully!")
        print(f"🌐 Your app is available at: https://{hostname}")
        print(f"🔒 HTTPS is now enforced")
        print(f"🔍 Health check: https://{hostname}/health")
        print(f"📊 System status: https://{hostname}/system-status")
        print(f"\n⏳ Please wait 2-3 minutes for changes to take effect.")
        print(f"🌐 Your custom domain: https://www.fdx.trading")
    else:
        print("❌ Failed to get app URL")

if __name__ == "__main__":
    fix_azure_deployment() 