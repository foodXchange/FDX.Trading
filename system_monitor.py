#!/usr/bin/env python3
"""
FoodXchange System Monitor
Comprehensive monitoring for database, Azure services, and application health
"""

import os
import sys
import time
import json
import psutil
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import subprocess
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            'timestamp': self.start_time.isoformat(),
            'system_info': {},
            'database': {},
            'azure_services': {},
            'application': {},
            'performance': {},
            'alerts': []
        }
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        try:
            info = {
                'platform': platform.platform(),
                'python_version': sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'disk_usage': {},
                'uptime': self.get_uptime()
            }
            
            # Disk usage
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    info['disk_usage'][partition.device] = {
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'percent_used': round((usage.used / usage.total) * 100, 2)
                    }
                except PermissionError:
                    continue
                    
            self.results['system_info'] = info
            logger.info("System info collected successfully")
            return info
            
        except Exception as e:
            logger.error(f"Error collecting system info: {e}")
            self.add_alert("SYSTEM_ERROR", f"Failed to collect system info: {e}")
            return {}
    
    def get_uptime(self) -> str:
        """Get system uptime"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime = timedelta(seconds=uptime_seconds)
            return str(uptime)
        except:
            return "Unknown"
    
    def check_database_connection(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        db_info = {
            'status': 'unknown',
            'connection_time': None,
            'query_time': None,
            'error': None
        }
        
        try:
            # Get database URL from environment
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                raise Exception("DATABASE_URL not found in environment")
            
            # Test connection time
            start_time = time.time()
            engine = create_engine(database_url)
            with engine.connect() as conn:
                db_info['connection_time'] = round((time.time() - start_time) * 1000, 2)
                
                # Test query performance
                start_time = time.time()
                result = conn.execute(text("SELECT 1 as test, NOW() as timestamp"))
                row = result.fetchone()
                db_info['query_time'] = round((time.time() - start_time) * 1000, 2)
                
                db_info['status'] = 'healthy'
                db_info['server_time'] = str(row.timestamp) if row else None
                
        except Exception as e:
            db_info['status'] = 'error'
            db_info['error'] = str(e)
            self.add_alert("DATABASE_ERROR", f"Database connection failed: {e}")
            logger.error(f"Database connection error: {e}")
        
        self.results['database'] = db_info
        return db_info
    
    def check_azure_services(self) -> Dict[str, Any]:
        """Check Azure services status"""
        azure_info = {
            'openai': {'status': 'unknown', 'error': None},
            'storage': {'status': 'unknown', 'error': None},
            'postgresql': {'status': 'unknown', 'error': None}
        }
        
        # Check Azure OpenAI
        try:
            openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            openai_key = os.getenv('AZURE_OPENAI_API_KEY')
            
            if openai_endpoint and openai_key:
                # Simple connectivity test
                response = requests.get(
                    f"{openai_endpoint}/openai/deployments",
                    headers={'api-key': openai_key},
                    timeout=10
                )
                if response.status_code == 200:
                    azure_info['openai']['status'] = 'healthy'
                else:
                    azure_info['openai']['status'] = 'error'
                    azure_info['openai']['error'] = f"HTTP {response.status_code}"
            else:
                azure_info['openai']['status'] = 'not_configured'
                
        except Exception as e:
            azure_info['openai']['status'] = 'error'
            azure_info['openai']['error'] = str(e)
            self.add_alert("AZURE_OPENAI_ERROR", f"Azure OpenAI check failed: {e}")
        
        # Check Azure Storage
        try:
            storage_conn_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
            if storage_conn_string:
                # Test storage connectivity
                from azure.storage.blob import BlobServiceClient
                blob_service = BlobServiceClient.from_connection_string(storage_conn_string)
                containers = blob_service.list_containers(max_results=1)
                list(containers)  # Force evaluation
                azure_info['storage']['status'] = 'healthy'
            else:
                azure_info['storage']['status'] = 'not_configured'
                
        except Exception as e:
            azure_info['storage']['status'] = 'error'
            azure_info['storage']['error'] = str(e)
            self.add_alert("AZURE_STORAGE_ERROR", f"Azure Storage check failed: {e}")
        
        # Check Azure PostgreSQL
        try:
            database_url = os.getenv('DATABASE_URL')
            if database_url and 'azure.com' in database_url:
                # Test connection
                engine = create_engine(database_url)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                azure_info['postgresql']['status'] = 'healthy'
            else:
                azure_info['postgresql']['status'] = 'not_azure'
                
        except Exception as e:
            azure_info['postgresql']['status'] = 'error'
            azure_info['postgresql']['error'] = str(e)
            self.add_alert("AZURE_POSTGRESQL_ERROR", f"Azure PostgreSQL check failed: {e}")
        
        self.results['azure_services'] = azure_info
        return azure_info
    
    def check_application_health(self) -> Dict[str, Any]:
        """Check application health endpoints"""
        app_info = {
            'status': 'unknown',
            'endpoints': {},
            'error': None
        }
        
        try:
            # Check if application is running locally
            base_url = os.getenv('APP_BASE_URL', 'http://localhost:8000')
            
            # Health check endpoint
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                app_info['endpoints']['health'] = {
                    'status': 'healthy' if response.status_code == 200 else 'error',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            except Exception as e:
                app_info['endpoints']['health'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # API status endpoint
            try:
                response = requests.get(f"{base_url}/api/v1/status", timeout=5)
                app_info['endpoints']['api'] = {
                    'status': 'healthy' if response.status_code == 200 else 'error',
                    'response_time': response.elapsed.total_seconds(),
                    'status_code': response.status_code
                }
            except Exception as e:
                app_info['endpoints']['api'] = {
                    'status': 'error',
                    'error': str(e)
                }
            
            # Overall status
            healthy_endpoints = sum(1 for ep in app_info['endpoints'].values() 
                                  if ep.get('status') == 'healthy')
            total_endpoints = len(app_info['endpoints'])
            
            if total_endpoints == 0:
                app_info['status'] = 'unknown'
            elif healthy_endpoints == total_endpoints:
                app_info['status'] = 'healthy'
            elif healthy_endpoints > 0:
                app_info['status'] = 'degraded'
            else:
                app_info['status'] = 'error'
                self.add_alert("APPLICATION_ERROR", "All application endpoints are failing")
                
        except Exception as e:
            app_info['status'] = 'error'
            app_info['error'] = str(e)
            self.add_alert("APPLICATION_ERROR", f"Application health check failed: {e}")
        
        self.results['application'] = app_info
        return app_info
    
    def check_performance_metrics(self) -> Dict[str, Any]:
        """Check system performance metrics"""
        perf_info = {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_io': {},
            'network_io': {},
            'process_count': len(psutil.pids())
        }
        
        # Disk I/O
        try:
            disk_io = psutil.disk_io_counters()
            if disk_io:
                perf_info['disk_io'] = {
                    'read_bytes_mb': round(disk_io.read_bytes / (1024**2), 2),
                    'write_bytes_mb': round(disk_io.write_bytes / (1024**2), 2),
                    'read_count': disk_io.read_count,
                    'write_count': disk_io.write_count
                }
        except:
            pass
        
        # Network I/O
        try:
            net_io = psutil.net_io_counters()
            if net_io:
                perf_info['network_io'] = {
                    'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
                    'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
        except:
            pass
        
        # Check for performance alerts
        if perf_info['cpu_usage'] > 80:
            self.add_alert("PERFORMANCE_WARNING", f"High CPU usage: {perf_info['cpu_usage']}%")
        
        if perf_info['memory_usage'] > 85:
            self.add_alert("PERFORMANCE_WARNING", f"High memory usage: {perf_info['memory_usage']}%")
        
        self.results['performance'] = perf_info
        return perf_info
    
    def add_alert(self, alert_type: str, message: str):
        """Add an alert to the results"""
        alert = {
            'type': alert_type,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'severity': 'high' if 'ERROR' in alert_type else 'medium'
        }
        self.results['alerts'].append(alert)
        logger.warning(f"ALERT [{alert_type}]: {message}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        logger.info("Starting system monitoring...")
        
        # Collect all metrics
        self.get_system_info()
        self.check_database_connection()
        self.check_azure_services()
        self.check_application_health()
        self.check_performance_metrics()
        
        # Add summary
        self.results['summary'] = {
            'total_alerts': len(self.results['alerts']),
            'critical_alerts': len([a for a in self.results['alerts'] if a['severity'] == 'high']),
            'overall_status': self.get_overall_status(),
            'monitoring_duration': (datetime.now() - self.start_time).total_seconds()
        }
        
        logger.info(f"Monitoring completed. Overall status: {self.results['summary']['overall_status']}")
        return self.results
    
    def get_overall_status(self) -> str:
        """Determine overall system status"""
        if any(alert['severity'] == 'high' for alert in self.results['alerts']):
            return 'critical'
        elif any(alert['severity'] == 'medium' for alert in self.results['alerts']):
            return 'warning'
        elif self.results['database'].get('status') == 'healthy' and \
             self.results['application'].get('status') == 'healthy':
            return 'healthy'
        else:
            return 'degraded'
    
    def save_report(self, filename: str = None):
        """Save monitoring report to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"monitoring_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            logger.info(f"Report saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return None
    
    def print_summary(self):
        """Print a human-readable summary"""
        print("\n" + "="*60)
        print("FOODXCHANGE SYSTEM MONITORING REPORT")
        print("="*60)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Overall Status: {self.results['summary']['overall_status'].upper()}")
        print(f"Alerts: {self.results['summary']['total_alerts']} (Critical: {self.results['summary']['critical_alerts']})")
        
        print("\n--- SYSTEM INFO ---")
        sys_info = self.results['system_info']
        print(f"Platform: {sys_info.get('platform', 'Unknown')}")
        print(f"CPU Usage: {self.results['performance'].get('cpu_usage', 'Unknown')}%")
        print(f"Memory Usage: {self.results['performance'].get('memory_usage', 'Unknown')}%")
        
        print("\n--- DATABASE ---")
        db_info = self.results['database']
        print(f"Status: {db_info.get('status', 'Unknown')}")
        if db_info.get('connection_time'):
            print(f"Connection Time: {db_info['connection_time']}ms")
        if db_info.get('error'):
            print(f"Error: {db_info['error']}")
        
        print("\n--- AZURE SERVICES ---")
        azure_info = self.results['azure_services']
        for service, info in azure_info.items():
            print(f"{service.title()}: {info.get('status', 'Unknown')}")
            if info.get('error'):
                print(f"  Error: {info['error']}")
        
        print("\n--- APPLICATION ---")
        app_info = self.results['application']
        print(f"Status: {app_info.get('status', 'Unknown')}")
        for endpoint, info in app_info.get('endpoints', {}).items():
            print(f"  {endpoint}: {info.get('status', 'Unknown')}")
        
        if self.results['alerts']:
            print("\n--- ALERTS ---")
            for alert in self.results['alerts']:
                print(f"[{alert['severity'].upper()}] {alert['type']}: {alert['message']}")
        
        print("="*60)

def main():
    """Main monitoring function"""
    monitor = SystemMonitor()
    
    try:
        # Generate comprehensive report
        report = monitor.generate_report()
        
        # Print summary
        monitor.print_summary()
        
        # Save report
        filename = monitor.save_report()
        
        # Return exit code based on status
        if report['summary']['overall_status'] == 'critical':
            sys.exit(1)
        elif report['summary']['overall_status'] == 'warning':
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 