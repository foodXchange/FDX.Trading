#!/usr/bin/env python3
"""
Azure Continuous Monitor: Real-time monitoring and auto-remediation
Continuously monitors your Azure app and automatically fixes issues
"""

import asyncio
import os
import sys
import json
import logging
import subprocess
from datetime import datetime, timedelta
import aiohttp
import time
from typing import Dict, List, Optional
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('azure_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AzureContinuousMonitor:
    def __init__(self):
        self.app_name = os.getenv('AZURE_APP_NAME', 'foodxchange-app')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'foodxchange-rg')
        self.app_url = f"https://{self.app_name}.azurewebsites.net"
        self.kudu_url = f"https://{self.app_name}.scm.azurewebsites.net"
        self.check_interval = 60  # seconds
        self.error_threshold = 3  # consecutive errors before action
        self.error_count = 0
        self.last_error_hash = None
        self.auto_fix_enabled = True
        self.notification_email = os.getenv('NOTIFICATION_EMAIL')
        
    async def start_monitoring(self):
        """Start continuous monitoring loop"""
        logger.info("🚀 Starting Azure Continuous Monitor...")
        logger.info(f"Monitoring {self.app_url} every {self.check_interval} seconds")
        
        while True:
            try:
                await self.monitor_cycle()
                await asyncio.sleep(self.check_interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitor cycle error: {str(e)}")
                await asyncio.sleep(self.check_interval)
    
    async def monitor_cycle(self):
        """Single monitoring cycle"""
        timestamp = datetime.now().isoformat()
        
        # 1. Health check
        health = await self.check_health()
        
        # 2. Performance metrics
        metrics = await self.collect_metrics()
        
        # 3. Log analysis
        recent_errors = await self.analyze_recent_logs()
        
        # 4. Resource usage
        resources = await self.check_resource_usage()
        
        # 5. SSL certificate
        ssl_status = await self.check_ssl_certificate()
        
        # 6. Database connectivity (if applicable)
        db_status = await self.check_database()
        
        # Compile status
        status = {
            "timestamp": timestamp,
            "health": health,
            "metrics": metrics,
            "errors": recent_errors,
            "resources": resources,
            "ssl": ssl_status,
            "database": db_status
        }
        
        # Determine if action needed
        if await self.action_required(status):
            await self.take_action(status)
        
        # Log status
        self.log_status(status)
    
    async def check_health(self) -> Dict:
        """Check application health"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(self.app_url, timeout=30) as response:
                    response_time = time.time() - start_time
                    status_code = response.status
                    
                    if status_code == 200:
                        self.error_count = 0
                        return {
                            "status": "healthy",
                            "code": status_code,
                            "response_time": round(response_time, 2)
                        }
                    else:
                        self.error_count += 1
                        content = await response.text()
                        return {
                            "status": "unhealthy",
                            "code": status_code,
                            "response_time": round(response_time, 2),
                            "error": content[:200]
                        }
        except asyncio.TimeoutError:
            self.error_count += 1
            return {"status": "timeout", "error": "Request timed out"}
        except Exception as e:
            self.error_count += 1
            return {"status": "error", "error": str(e)}
    
    async def collect_metrics(self) -> Dict:
        """Collect performance metrics"""
        metrics = {}
        
        try:
            # Get Azure metrics
            cmd = f"az monitor metrics list --resource /subscriptions/{os.getenv('AZURE_SUBSCRIPTION_ID')}/resourceGroups/{self.resource_group}/providers/Microsoft.Web/sites/{self.app_name} --metric 'Http5xx,Requests,ResponseTime,Http4xx' --interval PT1M"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for metric in data.get("value", []):
                    metric_name = metric["name"]["value"]
                    if metric["timeseries"]:
                        latest_value = metric["timeseries"][0]["data"][-1]["average"]
                        metrics[metric_name] = latest_value
        except Exception as e:
            logger.error(f"Failed to collect metrics: {str(e)}")
        
        return metrics
    
    async def analyze_recent_logs(self) -> List[Dict]:
        """Analyze recent logs for errors"""
        errors = []
        
        try:
            # Get recent logs
            cmd = f"az webapp log tail --name {self.app_name} --resource-group {self.resource_group} --max-log-size 1000"
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Read logs for 5 seconds
            await asyncio.sleep(5)
            process.terminate()
            
            stdout, stderr = process.communicate()
            logs = stdout + stderr
            
            # Common error patterns
            import re
            error_patterns = {
                "application_error": r"ERROR|Exception|Traceback",
                "memory_issue": r"MemoryError|Out of memory",
                "timeout": r"Timeout|timed out",
                "database_error": r"database.*error|connection.*failed",
                "import_error": r"ImportError|ModuleNotFoundError"
            }
            
            for error_type, pattern in error_patterns.items():
                if re.search(pattern, logs, re.IGNORECASE):
                    errors.append({
                        "type": error_type,
                        "timestamp": datetime.now().isoformat()
                    })
        
        except Exception as e:
            logger.error(f"Log analysis failed: {str(e)}")
        
        return errors
    
    async def check_resource_usage(self) -> Dict:
        """Check resource usage"""
        try:
            # Get app service plan metrics
            cmd = f"az appservice plan show --name {self.app_name}-plan --resource-group {self.resource_group}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                plan_data = json.loads(result.stdout)
                return {
                    "sku": plan_data.get("sku", {}).get("name"),
                    "capacity": plan_data.get("sku", {}).get("capacity"),
                    "status": plan_data.get("status")
                }
        except Exception as e:
            logger.error(f"Resource check failed: {str(e)}")
        
        return {}
    
    async def check_ssl_certificate(self) -> Dict:
        """Check SSL certificate status"""
        try:
            import ssl
            import socket
            
            hostname = f"{self.app_name}.azurewebsites.net"
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (expiry_date - datetime.now()).days
                    
                    return {
                        "valid": True,
                        "days_until_expiry": days_until_expiry,
                        "issuer": cert['issuer'][0][0][1]
                    }
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def check_database(self) -> Dict:
        """Check database connectivity if applicable"""
        # This would need to be customized based on your database
        return {"status": "not_configured"}
    
    async def action_required(self, status: Dict) -> bool:
        """Determine if action is required"""
        # Check if app is unhealthy
        if status["health"]["status"] != "healthy":
            if self.error_count >= self.error_threshold:
                return True
        
        # Check for high error rates
        if status["metrics"].get("Http5xx", 0) > 10:
            return True
        
        # Check for critical errors in logs
        critical_errors = ["application_error", "memory_issue", "database_error"]
        if any(error["type"] in critical_errors for error in status["errors"]):
            return True
        
        # Check SSL certificate expiry
        if status["ssl"].get("valid") and status["ssl"].get("days_until_expiry", 90) < 30:
            return True
        
        return False
    
    async def take_action(self, status: Dict):
        """Take remediation action"""
        logger.warning("🚨 Action required! Initiating auto-remediation...")
        
        actions_taken = []
        
        # 1. If app is down, try to restart
        if status["health"]["status"] != "healthy":
            logger.info("Restarting application...")
            cmd = f"az webapp restart --name {self.app_name} --resource-group {self.resource_group}"
            subprocess.run(cmd, shell=True)
            actions_taken.append("Restarted application")
            await asyncio.sleep(60)  # Wait for restart
        
        # 2. If memory issues, scale up temporarily
        if any(error["type"] == "memory_issue" for error in status["errors"]):
            logger.info("Scaling up due to memory issues...")
            cmd = f"az appservice plan update --name {self.app_name}-plan --resource-group {self.resource_group} --sku P1V2"
            subprocess.run(cmd, shell=True)
            actions_taken.append("Scaled up to P1V2")
        
        # 3. If import errors, trigger deployment
        if any(error["type"] == "import_error" for error in status["errors"]):
            logger.info("Triggering redeployment...")
            # Run the auto-fixer
            subprocess.run([sys.executable, "azure_auto_fixer.py"])
            actions_taken.append("Ran auto-fixer")
        
        # 4. Send notification
        if self.notification_email:
            await self.send_notification(status, actions_taken)
        
        # Log actions
        logger.info(f"Actions taken: {', '.join(actions_taken)}")
        
        # Reset error count after action
        self.error_count = 0
    
    async def send_notification(self, status: Dict, actions: List[str]):
        """Send email notification"""
        try:
            subject = f"Azure Monitor Alert: {self.app_name}"
            body = f"""
Azure Monitor has detected issues with {self.app_name} and taken automatic action.

Status: {json.dumps(status, indent=2)}

Actions Taken:
{chr(10).join(f"- {action}" for action in actions)}

Please review the application status.
"""
            
            # This would need SMTP configuration
            logger.info(f"Notification would be sent to {self.notification_email}")
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
    
    def log_status(self, status: Dict):
        """Log current status"""
        if status["health"]["status"] == "healthy":
            logger.info(f"✅ App healthy - Response time: {status['health'].get('response_time', 'N/A')}s")
        else:
            logger.warning(f"⚠️ App status: {status['health']['status']}")
        
        # Log metrics if available
        if status["metrics"]:
            metrics_str = ", ".join(f"{k}: {v}" for k, v in status["metrics"].items())
            logger.info(f"Metrics: {metrics_str}")

async def main():
    """Main entry point"""
    monitor = AzureContinuousMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main()