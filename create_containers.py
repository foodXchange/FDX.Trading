#!/usr/bin/env python
"""
Create Azure Blob Storage containers
"""
import subprocess
import os

def run_az_command(cmd, description):
    """Run Azure CLI command with timeout"""
    az_path = r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
    full_cmd = [az_path] + cmd
    
    try:
        print(f"🔄 {description}...")
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def create_containers():
    """Create all required blob storage containers"""
    print("=== Creating Azure Blob Storage Containers ===")
    
    containers = [
        "quotes",
        "orders", 
        "products",
        "suppliers",
        "email-attachments"
    ]
    
    success_count = 0
    
    for container in containers:
        cmd = [
            'storage', 'container', 'create',
            '--name', container,
            '--account-name', 'foodxchangestorage',
            '--public-access', 'off'
        ]
        
        if run_az_command(cmd, f"Creating container {container}"):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(containers)} containers created")
    
    if success_count == len(containers):
        print("✅ All containers created successfully!")
    else:
        print("⚠️  Some containers failed to create")
        print("   You may need to create them manually in Azure Portal")

def restart_app_service():
    """Restart the App Service"""
    print("\n=== Restarting App Service ===")
    
    cmd = [
        'webapp', 'restart',
        '--resource-group', 'foodxchange-rg',
        '--name', 'foodxchange-app'
    ]
    
    if run_az_command(cmd, "Restarting App Service"):
        print("✅ App Service restart initiated")
        print("   Wait 2-3 minutes for changes to take effect")
    else:
        print("❌ App Service restart failed")
        print("   Restart manually in Azure Portal")

if __name__ == "__main__":
    print("🚀 Azure Blob Storage Container Setup")
    print("="*50)
    
    create_containers()
    restart_app_service()
    
    print("\n🎉 Setup completed!")
    print("🔧 Next: Test the blob storage connection") 