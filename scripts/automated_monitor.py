"""
Automated Monitoring System for FoodXchange
Continuously monitors system health and sends alerts
"""

import time
import json
import logging
import redis
import psutil
import requests
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'monitoring')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'monitor_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.redis_client = None
        self.check_interval = 60  # seconds
        self.alert_cooldown = 3600  # 1 hour between same alerts
        self.alerts_sent = {}
        self.thresholds = {
            'cpu_percent': 80,
            'memory_percent': 80,
            'disk_percent': 90,
            'redis_memory_mb': 200,
            'response_time_ms': 1000,
            'error_rate_percent': 5
        }
        self.metrics_history = []
        
    def initialize_redis(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis_client.ping()
            return True
        except:
            logger.warning("Redis not available for monitoring")
            return False
    
    def check_app_health(self):
        """Check if the application is responding"""
        try:
            start_time = time.time()
            response = requests.get('http://localhost:8003/', timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy' if response.status_code < 500 else 'unhealthy',
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2)
            }
        except requests.RequestException as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def check_redis_health(self):
        """Check Redis health and performance"""
        if not self.redis_client:
            return {'status': 'unavailable'}
        
        try:
            # Ping test
            start_time = time.time()
            self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            # Get info
            info = self.redis_client.info()
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'memory_mb': round(info.get('used_memory', 0) / (1024 * 1024), 2),
                'connected_clients': info.get('connected_clients', 0),
                'ops_per_sec': info.get('instantaneous_ops_per_sec', 0),
                'hit_rate': self._calculate_hit_rate(info)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def _calculate_hit_rate(self, info):
        """Calculate cache hit rate"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        return round((hits / total * 100) if total > 0 else 0, 2)
    
    def check_system_resources(self):
        """Check system resource usage"""
        try:
            # CPU usage (with interval for accuracy)
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': round(memory.available / (1024**3), 2),
                'disk_percent': disk.percent,
                'disk_free_gb': round(disk.free / (1024**3), 2),
                'process_count': process_count
            }
        except Exception as e:
            logger.error(f"Error checking system resources: {e}")
            return {}
    
    def check_azure_usage(self):
        """Check Azure API usage and costs"""
        # This would integrate with Azure cost management APIs
        # For now, return mock data
        return {
            'api_calls_today': 0,
            'estimated_cost': 0.0,
            'quota_remaining': 100
        }
    
    def collect_metrics(self):
        """Collect all metrics"""
        timestamp = datetime.now()
        
        metrics = {
            'timestamp': timestamp.isoformat(),
            'app': self.check_app_health(),
            'redis': self.check_redis_health(),
            'system': self.check_system_resources(),
            'azure': self.check_azure_usage()
        }
        
        # Store in history (keep last 24 hours)
        self.metrics_history.append(metrics)
        cutoff = timestamp - timedelta(hours=24)
        self.metrics_history = [m for m in self.metrics_history 
                               if datetime.fromisoformat(m['timestamp']) > cutoff]
        
        return metrics
    
    def check_thresholds(self, metrics):
        """Check if any metrics exceed thresholds"""
        alerts = []
        
        # System resources
        system = metrics.get('system', {})
        if system.get('cpu_percent', 0) > self.thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'message': f"CPU usage is {system['cpu_percent']}%",
                'severity': 'warning'
            })
        
        if system.get('memory_percent', 0) > self.thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'message': f"Memory usage is {system['memory_percent']}%",
                'severity': 'warning'
            })
        
        if system.get('disk_percent', 0) > self.thresholds['disk_percent']:
            alerts.append({
                'type': 'disk_high',
                'message': f"Disk usage is {system['disk_percent']}%",
                'severity': 'critical'
            })
        
        # Redis
        redis_info = metrics.get('redis', {})
        if redis_info.get('status') == 'unhealthy':
            alerts.append({
                'type': 'redis_down',
                'message': "Redis is not responding",
                'severity': 'critical'
            })
        elif redis_info.get('memory_mb', 0) > self.thresholds['redis_memory_mb']:
            alerts.append({
                'type': 'redis_memory_high',
                'message': f"Redis memory usage is {redis_info['memory_mb']}MB",
                'severity': 'warning'
            })
        
        # Application
        app = metrics.get('app', {})
        if app.get('status') == 'unhealthy':
            alerts.append({
                'type': 'app_down',
                'message': "Application is not responding",
                'severity': 'critical'
            })
        elif app.get('response_time_ms', 0) > self.thresholds['response_time_ms']:
            alerts.append({
                'type': 'app_slow',
                'message': f"Application response time is {app['response_time_ms']}ms",
                'severity': 'warning'
            })
        
        return alerts
    
    def send_alerts(self, alerts):
        """Send alerts (log for now, email/SMS in production)"""
        for alert in alerts:
            alert_key = f"{alert['type']}_{alert['severity']}"
            
            # Check cooldown
            last_sent = self.alerts_sent.get(alert_key, datetime.min)
            if datetime.now() - last_sent < timedelta(seconds=self.alert_cooldown):
                continue
            
            # Log alert
            if alert['severity'] == 'critical':
                logger.error(f"CRITICAL ALERT: {alert['message']}")
            else:
                logger.warning(f"WARNING: {alert['message']}")
            
            # Update last sent time
            self.alerts_sent[alert_key] = datetime.now()
            
            # In production, send email/SMS here
            self.save_alert(alert)
    
    def save_alert(self, alert):
        """Save alert to file"""
        alert_file = os.path.join(self.log_dir, 'alerts.json')
        alerts = []
        
        if os.path.exists(alert_file):
            with open(alert_file, 'r') as f:
                alerts = json.load(f)
        
        alert['timestamp'] = datetime.now().isoformat()
        alerts.append(alert)
        
        # Keep last 1000 alerts
        alerts = alerts[-1000:]
        
        with open(alert_file, 'w') as f:
            json.dump(alerts, f, indent=2)
    
    def save_metrics(self, metrics):
        """Save metrics to file"""
        metrics_file = os.path.join(self.log_dir, f'metrics_{datetime.now().strftime("%Y%m%d")}.jsonl')
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
    
    def generate_hourly_report(self):
        """Generate hourly summary report"""
        if len(self.metrics_history) < 2:
            return
        
        # Calculate averages
        cpu_avg = sum(m['system'].get('cpu_percent', 0) for m in self.metrics_history) / len(self.metrics_history)
        memory_avg = sum(m['system'].get('memory_percent', 0) for m in self.metrics_history) / len(self.metrics_history)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': 'hourly',
            'summary': {
                'metrics_collected': len(self.metrics_history),
                'avg_cpu_percent': round(cpu_avg, 2),
                'avg_memory_percent': round(memory_avg, 2),
                'app_uptime_percent': self._calculate_uptime(),
                'redis_uptime_percent': self._calculate_redis_uptime()
            }
        }
        
        report_file = os.path.join(self.log_dir, 'hourly_reports.json')
        reports = []
        
        if os.path.exists(report_file):
            with open(report_file, 'r') as f:
                reports = json.load(f)
        
        reports.append(report)
        reports = reports[-168:]  # Keep 7 days of hourly reports
        
        with open(report_file, 'w') as f:
            json.dump(reports, f, indent=2)
        
        logger.info(f"Hourly report generated: CPU {cpu_avg:.1f}%, Memory {memory_avg:.1f}%")
    
    def _calculate_uptime(self):
        """Calculate application uptime percentage"""
        if not self.metrics_history:
            return 0
        
        healthy_count = sum(1 for m in self.metrics_history 
                          if m['app'].get('status') == 'healthy')
        return round((healthy_count / len(self.metrics_history)) * 100, 2)
    
    def _calculate_redis_uptime(self):
        """Calculate Redis uptime percentage"""
        if not self.metrics_history:
            return 0
        
        healthy_count = sum(1 for m in self.metrics_history 
                          if m['redis'].get('status') == 'healthy')
        return round((healthy_count / len(self.metrics_history)) * 100, 2)
    
    def run(self):
        """Main monitoring loop"""
        logger.info("Starting FoodXchange System Monitor")
        self.log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'monitoring')
        
        # Initialize Redis
        self.initialize_redis()
        
        last_hourly_report = datetime.now()
        
        while True:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                
                # Check thresholds and send alerts
                alerts = self.check_thresholds(metrics)
                if alerts:
                    self.send_alerts(alerts)
                
                # Save metrics
                self.save_metrics(metrics)
                
                # Generate hourly report
                if datetime.now() - last_hourly_report > timedelta(hours=1):
                    self.generate_hourly_report()
                    last_hourly_report = datetime.now()
                
                # Log status
                logger.info(
                    f"Monitor cycle complete - "
                    f"App: {metrics['app'].get('status', 'unknown')}, "
                    f"Redis: {metrics['redis'].get('status', 'unknown')}, "
                    f"CPU: {metrics['system'].get('cpu_percent', 0):.1f}%, "
                    f"Memory: {metrics['system'].get('memory_percent', 0):.1f}%"
                )
                
                # Wait for next check
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()