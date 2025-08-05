#!/usr/bin/env python3
"""
FDX VM Control Panel - FastAPI Edition with Azure Integration
Robust GUI for Linux/Ubuntu VM Operations
Version: 3.0
"""

import os
import subprocess
import json
import psutil
import platform
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import aiofiles
import httpx
from pathlib import Path

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import uvicorn

# Azure integration
from azure.monitor.query import LogsQueryClient, MetricsQueryClient
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.communication.email import EmailClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
class Settings:
    """Application settings"""
    APP_NAME = "FDX VM Control Panel"
    VERSION = "3.0"
    HOST = "0.0.0.0"
    PORT = 5555
    
    # Azure settings
    AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
    AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "foodxchange-rg")
    AZURE_VM_NAME = os.getenv("AZURE_VM_NAME", "fdx-vm")
    AZURE_STORAGE_CONNECTION = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_COMMUNICATION_CONNECTION = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    AZURE_LOG_WORKSPACE_ID = os.getenv("AZURE_LOG_WORKSPACE_ID")
    
    # VM settings
    VM_IP = "4.206.1.15"
    VM_USER = "fdxfounder"
    
    # Service configurations
    SERVICES = {
        "foodxchange": {
            "name": "FoodXchange App",
            "port": 80,
            "process": "uvicorn",
            "path": "/home/fdxfounder/fdx/app",
            "url": f"http://{VM_IP}",
            "health_check": "/health",
            "systemd": "foodxchange"
        },
        "fdx_crawler": {
            "name": "FDX Crawler (23,206 Suppliers)",
            "port": 8003,
            "process": "uvicorn",
            "path": "/home/fdxfounder/fdx/crawler",
            "url": f"http://{VM_IP}:8003",
            "health_check": "/health",
            "systemd": "fdx-crawler"
        },
        "postgresql": {
            "name": "PostgreSQL Database",
            "port": 5432,
            "process": "postgres",
            "systemd": "postgresql"
        },
        "redis": {
            "name": "Redis Cache",
            "port": 6379,
            "process": "redis-server",
            "systemd": "redis"
        },
        "nginx": {
            "name": "Nginx Web Server",
            "port": 80,
            "process": "nginx",
            "systemd": "nginx"
        },
        "grafana": {
            "name": "Grafana Monitoring",
            "port": 3000,
            "process": "grafana-server",
            "url": f"http://{VM_IP}:3000",
            "systemd": "grafana-server"
        },
        "netdata": {
            "name": "Netdata Real-time",
            "port": 19999,
            "process": "netdata",
            "url": f"http://{VM_IP}:19999",
            "systemd": "netdata"
        }
    }

settings = Settings()

# Pydantic models
class CommandRequest(BaseModel):
    command: str = Field(..., description="Command to execute")
    timeout: int = Field(30, description="Command timeout in seconds")

class CommandResponse(BaseModel):
    success: bool
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    command: str
    execution_time: float

class ServiceAction(BaseModel):
    service: str
    action: str = Field(..., regex="^(start|stop|restart|status)$")

class SystemMetrics(BaseModel):
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: Dict[str, Any]
    network: Dict[str, Any]
    timestamp: datetime
    
class BackupRequest(BaseModel):
    backup_type: str = Field("full", regex="^(full|incremental|differential)$")
    compress: bool = True
    upload_to_azure: bool = True

class Alert(BaseModel):
    level: str = Field(..., regex="^(info|warning|error|critical)$")
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    service: Optional[str] = None

# Initialize FastAPI with lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    app.state.alerts = []
    app.state.metrics_history = []
    
    # Start background tasks
    asyncio.create_task(monitor_system(app))
    asyncio.create_task(sync_with_azure(app))
    
    yield
    
    # Shutdown
    print("Shutting down VM Control Panel")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Azure clients
try:
    credential = DefaultAzureCredential()
    logs_client = LogsQueryClient(credential)
    metrics_client = MetricsQueryClient(credential)
    blob_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION) if settings.AZURE_STORAGE_CONNECTION else None
    email_client = EmailClient.from_connection_string(settings.AZURE_COMMUNICATION_CONNECTION) if settings.AZURE_COMMUNICATION_CONNECTION else None
except Exception as e:
    print(f"Azure clients initialization warning: {e}")
    logs_client = None
    metrics_client = None
    blob_client = None
    email_client = None

# VM Controller class
class VMController:
    """Main VM control logic"""
    
    @staticmethod
    async def execute_command(command: str, timeout: int = 30) -> CommandResponse:
        """Execute command asynchronously"""
        start_time = datetime.now()
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return CommandResponse(
                success=process.returncode == 0,
                stdout=stdout.decode() if stdout else None,
                stderr=stderr.decode() if stderr else None,
                command=command,
                execution_time=execution_time
            )
        except asyncio.TimeoutError:
            return CommandResponse(
                success=False,
                stderr="Command timeout",
                command=command,
                execution_time=timeout
            )
        except Exception as e:
            return CommandResponse(
                success=False,
                stderr=str(e),
                command=command,
                execution_time=(datetime.now() - start_time).total_seconds()
            )
    
    @staticmethod
    async def get_system_metrics() -> SystemMetrics:
        """Get comprehensive system metrics"""
        try:
            # CPU metrics with per-core info
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics for all partitions
            disk_partitions = psutil.disk_partitions()
            disk_usage = {}
            for partition in disk_partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    }
                except:
                    pass
            
            # Network metrics
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            return SystemMetrics(
                cpu={
                    'percent': cpu_percent,
                    'per_core': cpu_per_core,
                    'count': psutil.cpu_count(),
                    'freq_current': cpu_freq.current if cpu_freq else 0,
                    'freq_max': cpu_freq.max if cpu_freq else 0,
                    'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                },
                memory={
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percent': swap.percent
                },
                disk=disk_usage,
                network={
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv,
                    'connections': net_connections
                },
                timestamp=datetime.now()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get metrics: {e}")
    
    @staticmethod
    async def check_service_health(service_config: dict) -> dict:
        """Check service health including port and process"""
        health = {
            'name': service_config['name'],
            'port_open': False,
            'process_running': False,
            'systemd_active': False,
            'url_accessible': False
        }
        
        # Check port
        if 'port' in service_config:
            for conn in psutil.net_connections():
                if conn.laddr.port == service_config['port'] and conn.status == 'LISTEN':
                    health['port_open'] = True
                    break
        
        # Check process
        if 'process' in service_config:
            for proc in psutil.process_iter(['name']):
                if service_config['process'] in proc.info['name']:
                    health['process_running'] = True
                    break
        
        # Check systemd service
        if 'systemd' in service_config:
            result = await VMController.execute_command(f"systemctl is-active {service_config['systemd']}")
            health['systemd_active'] = result.stdout.strip() == 'active' if result.stdout else False
        
        # Check URL if available
        if 'url' in service_config and 'health_check' in service_config:
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(service_config['url'] + service_config['health_check'])
                    health['url_accessible'] = response.status_code == 200
            except:
                health['url_accessible'] = False
        
        health['overall'] = any([health['port_open'], health['process_running'], health['systemd_active']])
        return health
    
    @staticmethod
    async def create_backup(backup_request: BackupRequest) -> dict:
        """Create comprehensive system backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"/home/{settings.VM_USER}/backups"
        
        # Create backup directory
        await VMController.execute_command(f"mkdir -p {backup_dir}")
        
        backup_files = []
        
        # Database backup
        if backup_request.backup_type in ["full", "differential"]:
            db_backup = f"{backup_dir}/database_{timestamp}.sql"
            db_result = await VMController.execute_command(
                f"pg_dump -U {settings.VM_USER} -d foodxchange > {db_backup}"
            )
            if db_result.success:
                backup_files.append(db_backup)
        
        # Application files backup
        if backup_request.backup_type == "full":
            app_backup = f"{backup_dir}/apps_{timestamp}.tar"
            app_result = await VMController.execute_command(
                f"tar -cf {app_backup} /home/{settings.VM_USER}/fdx"
            )
            if app_result.success:
                backup_files.append(app_backup)
        
        # Compress backups
        if backup_request.compress and backup_files:
            archive = f"{backup_dir}/backup_{timestamp}.tar.gz"
            compress_result = await VMController.execute_command(
                f"tar -czf {archive} {' '.join(backup_files)}"
            )
            if compress_result.success:
                # Clean up individual files
                for file in backup_files:
                    await VMController.execute_command(f"rm {file}")
                backup_files = [archive]
        
        # Upload to Azure Blob Storage
        uploaded_files = []
        if backup_request.upload_to_azure and blob_client and backup_files:
            container_name = "vm-backups"
            try:
                container_client = blob_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client.create_container()
                
                for file in backup_files:
                    blob_name = os.path.basename(file)
                    blob_client_file = container_client.get_blob_client(blob_name)
                    
                    with open(file, 'rb') as data:
                        blob_client_file.upload_blob(data, overwrite=True)
                    
                    uploaded_files.append(f"https://{blob_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}")
            except Exception as e:
                print(f"Azure upload error: {e}")
        
        return {
            'success': len(backup_files) > 0,
            'local_files': backup_files,
            'azure_files': uploaded_files,
            'timestamp': timestamp
        }

# Background tasks
async def monitor_system(app: FastAPI):
    """Continuous system monitoring"""
    while True:
        try:
            metrics = await VMController.get_system_metrics()
            
            # Store metrics history (keep last hour)
            app.state.metrics_history.append(metrics.dict())
            cutoff_time = datetime.now() - timedelta(hours=1)
            app.state.metrics_history = [
                m for m in app.state.metrics_history 
                if datetime.fromisoformat(m['timestamp']) > cutoff_time
            ]
            
            # Check for alerts
            if metrics.cpu['percent'] > 90:
                app.state.alerts.append(Alert(
                    level="warning",
                    message=f"High CPU usage: {metrics.cpu['percent']}%"
                ).dict())
            
            if metrics.memory['percent'] > 90:
                app.state.alerts.append(Alert(
                    level="warning",
                    message=f"High memory usage: {metrics.memory['percent']}%"
                ).dict())
            
            # Check disk space
            for mount, usage in metrics.disk.items():
                if usage['percent'] > 90:
                    app.state.alerts.append(Alert(
                        level="critical",
                        message=f"Low disk space on {mount}: {usage['percent']}%"
                    ).dict())
            
            # Keep only recent alerts
            app.state.alerts = app.state.alerts[-50:]
            
        except Exception as e:
            print(f"Monitoring error: {e}")
        
        await asyncio.sleep(30)

async def sync_with_azure(app: FastAPI):
    """Sync metrics with Azure Monitor"""
    while True:
        try:
            if metrics_client and settings.AZURE_LOG_WORKSPACE_ID:
                # Query Azure metrics
                end_time = datetime.now()
                start_time = end_time - timedelta(minutes=5)
                
                # This would query actual Azure metrics
                # Example: CPU percentage from Azure Monitor
                # metrics = await metrics_client.query_resource(...)
                pass
        except Exception as e:
            print(f"Azure sync error: {e}")
        
        await asyncio.sleep(300)  # Every 5 minutes

# Routes
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard"""
    return templates.TemplateResponse(
        "dashboard_fastapi.html",
        {
            "request": request,
            "settings": settings,
            "title": settings.APP_NAME,
            "version": settings.VERSION
        }
    )

@app.get("/api/metrics")
async def get_metrics():
    """Get current system metrics"""
    metrics = await VMController.get_system_metrics()
    return metrics

@app.get("/api/metrics/history")
async def get_metrics_history():
    """Get metrics history"""
    return app.state.metrics_history

@app.get("/api/services")
async def get_services():
    """Get all services status"""
    services_status = {}
    for service_id, service_config in settings.SERVICES.items():
        services_status[service_id] = await VMController.check_service_health(service_config)
    return services_status

@app.get("/api/service/{service_id}")
async def get_service(service_id: str):
    """Get specific service status"""
    if service_id not in settings.SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return await VMController.check_service_health(settings.SERVICES[service_id])

@app.post("/api/service/{service_id}/{action}")
async def manage_service(service_id: str, action: str):
    """Manage service (start/stop/restart)"""
    if service_id not in settings.SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if action not in ["start", "stop", "restart", "status"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    service = settings.SERVICES[service_id]
    if 'systemd' not in service:
        raise HTTPException(status_code=400, detail="Service not manageable")
    
    result = await VMController.execute_command(f"sudo systemctl {action} {service['systemd']}")
    return result

@app.post("/api/execute")
async def execute_command(request: CommandRequest):
    """Execute command with restrictions"""
    # Whitelist safe commands
    safe_commands = [
        'ls', 'pwd', 'whoami', 'date', 'uptime', 'df', 'free',
        'ps', 'top', 'htop', 'netstat', 'ss', 'ip', 'ifconfig',
        'systemctl', 'journalctl', 'tail', 'head', 'cat', 'grep'
    ]
    
    cmd_parts = request.command.split()
    if not cmd_parts:
        raise HTTPException(status_code=400, detail="Empty command")
    
    # Check if command is safe
    base_command = cmd_parts[0].replace('sudo', '').strip()
    if base_command not in safe_commands:
        # Check for piped commands
        for safe_cmd in safe_commands:
            if safe_cmd in request.command:
                break
        else:
            raise HTTPException(status_code=403, detail="Command not allowed")
    
    result = await VMController.execute_command(request.command, request.timeout)
    return result

@app.get("/api/processes")
async def get_processes():
    """Get top processes by CPU and memory"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'username']):
        try:
            pinfo = proc.info
            if pinfo['cpu_percent'] > 0.1 or pinfo['memory_percent'] > 0.1:
                processes.append(pinfo)
        except:
            pass
    
    # Sort by CPU usage
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
    return processes[:30]

@app.get("/api/logs/{service_id}")
async def get_logs(service_id: str, lines: int = 100):
    """Get service logs"""
    if service_id not in settings.SERVICES and service_id != "system":
        raise HTTPException(status_code=404, detail="Service not found")
    
    if service_id == "system":
        command = f"sudo journalctl -n {lines} --no-pager"
    else:
        service = settings.SERVICES[service_id]
        if 'systemd' in service:
            command = f"sudo journalctl -u {service['systemd']} -n {lines} --no-pager"
        else:
            command = f"sudo tail -n {lines} /var/log/syslog"
    
    result = await VMController.execute_command(command)
    return {"logs": result.stdout if result.success else result.stderr}

@app.post("/api/backup")
async def create_backup(backup_request: BackupRequest, background_tasks: BackgroundTasks):
    """Create system backup"""
    # Run backup in background
    background_tasks.add_task(VMController.create_backup, backup_request)
    return {"message": "Backup initiated", "status": "processing"}

@app.get("/api/alerts")
async def get_alerts():
    """Get system alerts"""
    return app.state.alerts

@app.delete("/api/alerts")
async def clear_alerts():
    """Clear all alerts"""
    app.state.alerts = []
    return {"message": "Alerts cleared"}

@app.post("/api/alert")
async def send_alert(alert: Alert):
    """Send alert via Azure Communication Services"""
    if email_client:
        try:
            # Send email alert
            message = {
                "senderAddress": "DoNotReply@fdx.trading",
                "recipients": {
                    "to": [{"address": "admin@fdx.trading"}]
                },
                "content": {
                    "subject": f"VM Alert: {alert.level.upper()} - {alert.service or 'System'}",
                    "plainText": alert.message,
                    "html": f"""
                    <html>
                        <body>
                            <h2>VM Alert</h2>
                            <p><strong>Level:</strong> {alert.level}</p>
                            <p><strong>Service:</strong> {alert.service or 'System'}</p>
                            <p><strong>Message:</strong> {alert.message}</p>
                            <p><strong>Time:</strong> {alert.timestamp}</p>
                        </body>
                    </html>
                    """
                }
            }
            
            poller = email_client.begin_send(message)
            result = poller.result()
            return {"message": "Alert sent", "id": result.id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send alert: {e}")
    else:
        # Just store locally
        app.state.alerts.append(alert.dict())
        return {"message": "Alert stored locally"}

@app.get("/api/azure/status")
async def get_azure_status():
    """Get Azure integration status"""
    return {
        "storage_connected": blob_client is not None,
        "email_connected": email_client is not None,
        "monitor_connected": logs_client is not None,
        "subscription_id": settings.AZURE_SUBSCRIPTION_ID,
        "resource_group": settings.AZURE_RESOURCE_GROUP,
        "vm_name": settings.AZURE_VM_NAME
    }

# Health check
@app.get("/health")
async def health_check():
    """Application health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "version": settings.VERSION,
        "uptime": (datetime.now() - app.state.get('start_time', datetime.now())).total_seconds()
    }

if __name__ == "__main__":
    uvicorn.run(
        "vm_control_fastapi:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )