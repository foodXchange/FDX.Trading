#!/usr/bin/env python3
"""
Azure App Auto-Fixer: Comprehensive diagnostic and remediation tool
Automatically detects, researches, and fixes Azure deployment issues
"""

import os
import sys
import json
import time
import subprocess
import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import asyncio
import aiohttp
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('azure_auto_fixer.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AzureAutoFixer:
    def __init__(self):
        self.app_name = os.getenv('AZURE_APP_NAME', 'foodxchange-app')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'foodxchange-rg')
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.app_url = f"https://{self.app_name}.azurewebsites.net"
        self.kudu_url = f"https://{self.app_name}.scm.azurewebsites.net"
        self.fixes_applied = []
        self.errors_found = []
        
    async def run_full_diagnostic(self):
        """Run comprehensive diagnostics and auto-fix issues"""
        logger.info("🔍 Starting Azure App Auto-Fixer...")
        
        # Step 1: Check app health
        health_status = await self.check_app_health()
        
        # Step 2: Fetch and analyze logs
        logs = await self.fetch_app_logs()
        errors = self.analyze_logs(logs)
        
        # Step 3: Check deployment configuration
        config_issues = await self.check_deployment_config()
        
        # Step 4: Verify dependencies
        dep_issues = await self.verify_dependencies()
        
        # Step 5: Check Azure settings
        azure_issues = await self.check_azure_settings()
        
        # Step 6: Apply fixes
        await self.apply_fixes(errors + config_issues + dep_issues + azure_issues)
        
        # Step 7: Validate fixes
        await self.validate_fixes()
        
        # Step 8: Generate report
        self.generate_report()
        
    async def check_app_health(self) -> Dict:
        """Check if the app is responding"""
        logger.info("Checking app health...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.app_url, timeout=30) as response:
                    status = response.status
                    if status == 200:
                        logger.info("✅ App is responding normally")
                        return {"status": "healthy", "code": status}
                    else:
                        logger.warning(f"⚠️ App returned status code: {status}")
                        content = await response.text()
                        self.errors_found.append({
                            "type": "http_error",
                            "code": status,
                            "content": content[:500]
                        })
                        return {"status": "unhealthy", "code": status, "content": content}
        except Exception as e:
            logger.error(f"❌ App health check failed: {str(e)}")
            self.errors_found.append({
                "type": "connection_error",
                "error": str(e)
            })
            return {"status": "unreachable", "error": str(e)}
    
    async def fetch_app_logs(self) -> str:
        """Fetch application logs from Azure"""
        logger.info("Fetching application logs...")
        try:
            # Try multiple log sources
            logs = ""
            
            # 1. Azure CLI logs
            result = subprocess.run(
                f"az webapp log download --name {self.app_name} --resource-group {self.resource_group} --log-file app-logs.zip",
                shell=True, capture_output=True, text=True
            )
            
            # 2. Kudu logs API
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.kudu_url}/api/logs/docker", 
                                     auth=aiohttp.BasicAuth(self.get_deployment_credentials())) as response:
                    if response.status == 200:
                        logs += await response.text()
            
            # 3. Application insights
            logs += self.fetch_application_insights_logs()
            
            return logs
        except Exception as e:
            logger.error(f"Failed to fetch logs: {str(e)}")
            return ""
    
    def analyze_logs(self, logs: str) -> List[Dict]:
        """Analyze logs for common errors and issues"""
        logger.info("Analyzing logs for errors...")
        errors = []
        
        # Common error patterns
        error_patterns = {
            "module_not_found": r"ModuleNotFoundError: No module named '([^']+)'",
            "import_error": r"ImportError: cannot import name '([^']+)'",
            "startup_timeout": r"Container didn't respond to HTTP pings",
            "memory_error": r"MemoryError|Out of memory",
            "permission_denied": r"Permission denied|Access denied",
            "port_binding": r"Address already in use|bind failed",
            "flask_error": r"Flask application failed to start",
            "gunicorn_error": r"gunicorn.*failed|worker.*failed",
            "dependency_conflict": r"dependency.*conflict|version.*conflict",
            "database_connection": r"database.*connection.*failed|psycopg2.*error",
            "azure_storage": r"azure\.storage.*error|blob.*failed",
            "authentication": r"authentication.*failed|unauthorized|401"
        }
        
        import re
        for error_type, pattern in error_patterns.items():
            matches = re.findall(pattern, logs, re.IGNORECASE)
            if matches:
                errors.append({
                    "type": error_type,
                    "matches": matches,
                    "count": len(matches)
                })
                logger.warning(f"Found {len(matches)} {error_type} errors")
        
        return errors
    
    async def check_deployment_config(self) -> List[Dict]:
        """Check deployment configuration files"""
        logger.info("Checking deployment configuration...")
        issues = []
        
        # Check web.config
        if os.path.exists("web.config"):
            with open("web.config", "r") as f:
                content = f.read()
                if "python" not in content.lower():
                    issues.append({
                        "type": "config_error",
                        "file": "web.config",
                        "issue": "Python handler not configured"
                    })
        
        # Check startup files
        startup_files = ["startup.sh", "startup.py", "azure_startup.py"]
        found_startup = False
        for file in startup_files:
            if os.path.exists(file):
                found_startup = True
                # Check file permissions
                if not os.access(file, os.X_OK):
                    issues.append({
                        "type": "permission_error",
                        "file": file,
                        "issue": "Startup file not executable"
                    })
        
        if not found_startup:
            issues.append({
                "type": "missing_file",
                "issue": "No startup file found"
            })
        
        # Check requirements.txt
        if os.path.exists("requirements.txt"):
            with open("requirements.txt", "r") as f:
                reqs = f.read()
                # Check for problematic packages
                if "azure-ai-translation" in reqs and "azure-ai-translation==1.0.0b1" not in reqs:
                    issues.append({
                        "type": "dependency_error",
                        "file": "requirements.txt",
                        "issue": "azure-ai-translation version not specified"
                    })
        
        return issues
    
    async def verify_dependencies(self) -> List[Dict]:
        """Verify all dependencies are correctly installed"""
        logger.info("Verifying dependencies...")
        issues = []
        
        try:
            # Check if all required packages can be imported
            required_packages = [
                "flask", "fastapi", "uvicorn", "gunicorn",
                "azure.storage.blob", "azure.ai.translation",
                "sqlalchemy", "pydantic", "python-multipart"
            ]
            
            for package in required_packages:
                try:
                    __import__(package.split('.')[0])
                except ImportError:
                    issues.append({
                        "type": "missing_dependency",
                        "package": package
                    })
        except Exception as e:
            logger.error(f"Dependency verification failed: {str(e)}")
        
        return issues
    
    async def check_azure_settings(self) -> List[Dict]:
        """Check Azure App Service settings"""
        logger.info("Checking Azure settings...")
        issues = []
        
        try:
            # Check app settings
            result = subprocess.run(
                f"az webapp config appsettings list --name {self.app_name} --resource-group {self.resource_group}",
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                settings = json.loads(result.stdout)
                required_settings = [
                    "WEBSITE_RUN_FROM_PACKAGE",
                    "SCM_DO_BUILD_DURING_DEPLOYMENT",
                    "PYTHON_VERSION"
                ]
                
                setting_dict = {s["name"]: s["value"] for s in settings}
                
                for setting in required_settings:
                    if setting not in setting_dict:
                        issues.append({
                            "type": "missing_setting",
                            "setting": setting
                        })
            
            # Check runtime stack
            result = subprocess.run(
                f"az webapp config show --name {self.app_name} --resource-group {self.resource_group}",
                shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                config = json.loads(result.stdout)
                if config.get("linuxFxVersion", "").startswith("PYTHON"):
                    python_version = config["linuxFxVersion"].split("|")[1]
                    if python_version < "3.9":
                        issues.append({
                            "type": "runtime_version",
                            "issue": f"Python version {python_version} is too old"
                        })
        
        except Exception as e:
            logger.error(f"Azure settings check failed: {str(e)}")
        
        return issues
    
    async def apply_fixes(self, issues: List[Dict]):
        """Apply automatic fixes for detected issues"""
        logger.info(f"Applying fixes for {len(issues)} issues...")
        
        for issue in issues:
            try:
                if issue["type"] == "module_not_found":
                    await self.fix_missing_module(issue)
                elif issue["type"] == "permission_error":
                    await self.fix_permissions(issue)
                elif issue["type"] == "missing_setting":
                    await self.fix_azure_setting(issue)
                elif issue["type"] == "dependency_error":
                    await self.fix_dependency(issue)
                elif issue["type"] == "config_error":
                    await self.fix_config(issue)
                elif issue["type"] == "http_error":
                    await self.fix_http_error(issue)
            except Exception as e:
                logger.error(f"Failed to apply fix for {issue['type']}: {str(e)}")
    
    async def fix_missing_module(self, issue: Dict):
        """Fix missing module errors"""
        logger.info(f"Fixing missing modules: {issue['matches']}")
        
        # Update requirements.txt
        with open("requirements.txt", "a") as f:
            for module in issue["matches"]:
                if module not in open("requirements.txt").read():
                    f.write(f"\n{module}")
                    self.fixes_applied.append(f"Added {module} to requirements.txt")
    
    async def fix_permissions(self, issue: Dict):
        """Fix file permission issues"""
        logger.info(f"Fixing permissions for {issue['file']}")
        
        if sys.platform != "win32":
            os.chmod(issue["file"], 0o755)
            self.fixes_applied.append(f"Fixed permissions for {issue['file']}")
    
    async def fix_azure_setting(self, issue: Dict):
        """Fix missing Azure settings"""
        logger.info(f"Adding Azure setting: {issue['setting']}")
        
        settings_map = {
            "WEBSITE_RUN_FROM_PACKAGE": "0",
            "SCM_DO_BUILD_DURING_DEPLOYMENT": "true",
            "PYTHON_VERSION": "3.12"
        }
        
        if issue["setting"] in settings_map:
            cmd = f"az webapp config appsettings set --name {self.app_name} --resource-group {self.resource_group} --settings {issue['setting']}={settings_map[issue['setting']]}"
            subprocess.run(cmd, shell=True)
            self.fixes_applied.append(f"Set {issue['setting']} = {settings_map[issue['setting']]}")
    
    async def fix_dependency(self, issue: Dict):
        """Fix dependency issues"""
        logger.info(f"Fixing dependency issue in {issue['file']}")
        
        if issue["issue"] == "azure-ai-translation version not specified":
            # Update requirements.txt
            with open("requirements.txt", "r") as f:
                content = f.read()
            
            content = content.replace("azure-ai-translation", "azure-ai-translation==1.0.0b1")
            
            with open("requirements.txt", "w") as f:
                f.write(content)
            
            self.fixes_applied.append("Fixed azure-ai-translation version")
    
    async def fix_config(self, issue: Dict):
        """Fix configuration issues"""
        logger.info(f"Fixing config issue in {issue['file']}")
        
        if issue["file"] == "web.config" and issue["issue"] == "Python handler not configured":
            # Create proper web.config
            web_config = '''<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="python" 
                  arguments="startup.py"
                  stdoutLogEnabled="true" 
                  stdoutLogFile="\\\\?\\%home%\\LogFiles\\python.log"
                  startupTimeLimit="60"
                  processesPerApplication="1">
      <environmentVariables>
        <environmentVariable name="PORT" value="%HTTP_PLATFORM_PORT%" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>'''
            
            with open("web.config", "w") as f:
                f.write(web_config)
            
            self.fixes_applied.append("Updated web.config with Python handler")
    
    async def fix_http_error(self, issue: Dict):
        """Fix HTTP errors"""
        logger.info(f"Fixing HTTP error: {issue['code']}")
        
        if issue["code"] == 503:
            # Service unavailable - restart the app
            cmd = f"az webapp restart --name {self.app_name} --resource-group {self.resource_group}"
            subprocess.run(cmd, shell=True)
            self.fixes_applied.append("Restarted application")
            
            # Wait for restart
            await asyncio.sleep(30)
    
    async def validate_fixes(self):
        """Validate that fixes were successful"""
        logger.info("Validating fixes...")
        
        # Re-check app health
        health = await self.check_app_health()
        
        if health["status"] == "healthy":
            logger.info("✅ All fixes validated successfully!")
        else:
            logger.warning("⚠️ Some issues may still persist")
    
    def generate_report(self):
        """Generate a comprehensive report"""
        logger.info("Generating report...")
        
        report = f"""
# Azure Auto-Fixer Report
Generated: {datetime.now().isoformat()}

## App Information
- App Name: {self.app_name}
- URL: {self.app_url}
- Resource Group: {self.resource_group}

## Errors Found: {len(self.errors_found)}
{json.dumps(self.errors_found, indent=2)}

## Fixes Applied: {len(self.fixes_applied)}
{chr(10).join(f"- {fix}" for fix in self.fixes_applied)}

## Recommendations:
1. Monitor the application for the next 24 hours
2. Check Azure Monitor for detailed metrics
3. Review application logs regularly
4. Set up alerts for critical errors

## Next Steps:
- Redeploy the application if fixes were applied
- Test all functionality thoroughly
- Set up continuous monitoring
"""
        
        with open("azure_auto_fixer_report.md", "w") as f:
            f.write(report)
        
        logger.info("Report saved to azure_auto_fixer_report.md")
    
    def get_deployment_credentials(self) -> Tuple[str, str]:
        """Get deployment credentials for Kudu"""
        # This would need to be configured with actual credentials
        return ("$fdx-trading", "deployment_password")
    
    def fetch_application_insights_logs(self) -> str:
        """Fetch logs from Application Insights"""
        # This would integrate with Application Insights API
        return ""

async def main():
    """Main entry point"""
    fixer = AzureAutoFixer()
    await fixer.run_full_diagnostic()

if __name__ == "__main__":
    asyncio.run(main())