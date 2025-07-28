#!/usr/bin/env python3
"""
Azure App Service Diagnostic and Fix Script
This script diagnoses and fixes common deployment issues
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

class AzureDiagnosticFix:
    def __init__(self, app_name="fdx-trading", resource_group="foodxchange-rg"):
        self.app_name = app_name
        self.resource_group = resource_group
        self.issues = []
        self.fixes_applied = []
        
    def run_command(self, command, capture_output=True):
        """Run a shell command and return output"""
        try:
            if isinstance(command, str):
                command = command.split()
            
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                shell=True if sys.platform == "win32" else False
            )
            
            if result.returncode != 0 and capture_output:
                print(f"Command failed: {' '.join(command)}")
                print(f"Error: {result.stderr}")
            
            return result.stdout if capture_output else result.returncode
        except Exception as e:
            print(f"Error running command: {e}")
            return None
    
    def check_azure_cli(self):
        """Check if Azure CLI is installed and logged in"""
        print("[CHECK] Checking Azure CLI...")
        
        # Check if az is installed
        version = self.run_command("az --version")
        if not version:
            self.issues.append("Azure CLI not installed")
            return False
        
        # Check if logged in
        account = self.run_command("az account show")
        if not account:
            self.issues.append("Not logged in to Azure")
            return False
        
        print("[OK] Azure CLI is ready")
        return True
    
    def check_app_exists(self):
        """Check if the app exists"""
        print(f"\n[CHECK] Checking if app '{self.app_name}' exists...")
        
        result = self.run_command(f"az webapp show --name {self.app_name} --resource-group {self.resource_group}")
        if not result:
            self.issues.append(f"App '{self.app_name}' not found")
            return False
        
        app_info = json.loads(result)
        print(f"[OK] App found: {app_info['defaultHostName']}")
        print(f"   State: {app_info['state']}")
        print(f"   Runtime: {app_info.get('siteConfig', {}).get('linuxFxVersion', 'Unknown')}")
        
        return True
    
    def check_app_settings(self):
        """Check and fix app settings"""
        print(f"\n[CHECK] Checking app settings...")
        
        result = self.run_command(
            f"az webapp config appsettings list --name {self.app_name} --resource-group {self.resource_group}"
        )
        
        if not result:
            self.issues.append("Could not retrieve app settings")
            return False
        
        settings = json.loads(result)
        settings_dict = {s['name']: s['value'] for s in settings}
        
        required_settings = {
            'SCM_DO_BUILD_DURING_DEPLOYMENT': 'true',
            'ENABLE_ORYX_BUILD': 'true',
            'PYTHON_ENABLE_GUNICORN_MULTIWORKERS': 'false',
            'WEBSITES_PORT': '8000',
            'WEBSITE_HEALTHCHECK_MAXPINGFAILURES': '10'
        }
        
        missing_settings = []
        for key, value in required_settings.items():
            if key not in settings_dict or settings_dict[key] != value:
                missing_settings.append(f"{key}={value}")
        
        if missing_settings:
            print(f"[WARN] Missing or incorrect settings found")
            print(f"[FIX] Applying settings fix...")
            
            settings_str = ' '.join(missing_settings)
            self.run_command(
                f"az webapp config appsettings set --name {self.app_name} --resource-group {self.resource_group} --settings {settings_str}"
            )
            self.fixes_applied.append("Updated app settings")
        else:
            print("[OK] App settings are correct")
        
        return True
    
    def check_startup_command(self):
        """Check and fix startup command"""
        print(f"\n[CHECK] Checking startup command...")
        
        result = self.run_command(
            f"az webapp config show --name {self.app_name} --resource-group {self.resource_group}"
        )
        
        if not result:
            self.issues.append("Could not retrieve startup configuration")
            return False
        
        config = json.loads(result)
        startup_command = config.get('appCommandLine', '')
        
        if not startup_command or 'uvicorn' not in startup_command:
            print("[WARN] Startup command not configured properly")
            print("[FIX] Setting startup command...")
            
            self.run_command(
                f'az webapp config set --name {self.app_name} --resource-group {self.resource_group} --startup-file "python -m uvicorn app:app --host 0.0.0.0 --port 8000"'
            )
            self.fixes_applied.append("Updated startup command")
        else:
            print(f"[OK] Startup command: {startup_command}")
        
        return True
    
    def create_minimal_deployment(self):
        """Create a minimal working deployment"""
        print(f"\n[BUILD] Creating minimal deployment package...")
        
        # Create deployment directory
        deploy_dir = "minimal_azure_deploy"
        if os.path.exists(deploy_dir):
            import shutil
            shutil.rmtree(deploy_dir)
        os.makedirs(deploy_dir)
        
        # Create minimal app.py
        app_content = '''from fastapi import FastAPI, Response
from datetime import datetime
import os
import sys

app = FastAPI(title="FoodXchange API - Minimal")

@app.get("/")
async def root():
    return {
        "message": "FoodXchange API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.head("/health")
async def health_head():
    return Response(status_code=200)

@app.get("/health/simple")
async def health_simple():
    return Response(content="OK", media_type="text/plain")

@app.head("/")
async def root_head():
    return Response(status_code=200)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
'''
        
        with open(os.path.join(deploy_dir, "app.py"), "w") as f:
            f.write(app_content)
        
        # Create minimal requirements.txt
        requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
python-dotenv==1.0.0
"""
        
        with open(os.path.join(deploy_dir, "requirements.txt"), "w") as f:
            f.write(requirements)
        
        # Create startup.txt
        with open(os.path.join(deploy_dir, "startup.txt"), "w") as f:
            f.write("python -m uvicorn app:app --host 0.0.0.0 --port 8000")
        
        # Create runtime.txt
        with open(os.path.join(deploy_dir, "runtime.txt"), "w") as f:
            f.write("python-3.12")
        
        # Create deployment package
        import zipfile
        with zipfile.ZipFile("minimal_deployment.zip", "w") as zipf:
            for root, dirs, files in os.walk(deploy_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, deploy_dir)
                    zipf.write(file_path, arcname)
        
        # Clean up
        import shutil
        shutil.rmtree(deploy_dir)
        
        print("[OK] Minimal deployment package created: minimal_deployment.zip")
        return True
    
    def deploy_package(self):
        """Deploy the minimal package"""
        print(f"\n[DEPLOY] Deploying minimal package...")
        
        if not os.path.exists("minimal_deployment.zip"):
            print("[ERROR] Deployment package not found")
            return False
        
        result = self.run_command(
            f"az webapp deploy --name {self.app_name} --resource-group {self.resource_group} --src-path minimal_deployment.zip --type zip"
        )
        
        if result:
            print("[OK] Deployment initiated")
            self.fixes_applied.append("Deployed minimal working app")
            return True
        
        return False
    
    def restart_app(self):
        """Restart the app"""
        print(f"\n[RESTART] Restarting app...")
        
        self.run_command(
            f"az webapp restart --name {self.app_name} --resource-group {self.resource_group}"
        )
        
        print("[OK] App restart initiated")
        time.sleep(30)  # Wait for restart
        return True
    
    def test_endpoints(self):
        """Test the app endpoints"""
        print(f"\n[TEST] Testing endpoints...")
        
        base_url = f"https://{self.app_name}.azurewebsites.net"
        endpoints = ["/", "/health", "/health/simple"]
        
        import urllib.request
        import urllib.error
        
        all_passed = True
        for endpoint in endpoints:
            url = base_url + endpoint
            try:
                response = urllib.request.urlopen(url, timeout=30)
                status = response.getcode()
                if status == 200:
                    print(f"[OK] {endpoint} - Status: {status}")
                else:
                    print(f"[WARN] {endpoint} - Status: {status}")
                    all_passed = False
            except Exception as e:
                print(f"[ERROR] {endpoint} - Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def run_diagnostics(self):
        """Run full diagnostics and fixes"""
        print("Azure App Service Diagnostic Tool")
        print("=" * 50)
        print(f"App Name: {self.app_name}")
        print(f"Resource Group: {self.resource_group}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # Run checks
        if not self.check_azure_cli():
            print("\n[ERROR] Cannot proceed without Azure CLI")
            return
        
        if not self.check_app_exists():
            print("\n[ERROR] App does not exist. Please create it first.")
            return
        
        # Apply fixes
        self.check_app_settings()
        self.check_startup_command()
        
        # Create and deploy minimal app
        self.create_minimal_deployment()
        self.deploy_package()
        
        # Restart and test
        self.restart_app()
        success = self.test_endpoints()
        
        # Summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        if self.issues:
            print("\n[ISSUES] Issues found:")
            for issue in self.issues:
                print(f"   - {issue}")
        
        if self.fixes_applied:
            print("\n[FIXES] Fixes applied:")
            for fix in self.fixes_applied:
                print(f"   - {fix}")
        
        if success:
            print(f"\n[SUCCESS] App is now accessible at: https://{self.app_name}.azurewebsites.net")
        else:
            print(f"\n[WARN] App may still have issues. Check logs at:")
            print(f"   https://{self.app_name}.scm.azurewebsites.net/api/logs/docker")
        
        print("\n[NEXT STEPS]:")
        print("   1. Monitor the app for a few minutes")
        print("   2. Check application logs if issues persist")
        print("   3. Deploy your full application once minimal version works")

if __name__ == "__main__":
    # Parse command line arguments
    app_name = "fdx-trading"
    resource_group = "foodxchange-rg"
    
    if len(sys.argv) > 1:
        app_name = sys.argv[1]
    if len(sys.argv) > 2:
        resource_group = sys.argv[2]
    
    # Run diagnostics
    fixer = AzureDiagnosticFix(app_name, resource_group)
    fixer.run_diagnostics()