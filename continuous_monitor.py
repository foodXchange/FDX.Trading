#!/usr/bin/env python3
"""
FoodXchange Continuous System Monitor
Runs monitoring checks at regular intervals and sends alerts
"""

import os
import sys
import time
import json
import asyncio
import logging
import smtplib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import threading
from system_monitor import SystemMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('continuous_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ContinuousMonitor:
    def __init__(self, interval_minutes: int = 5, alert_threshold: int = 3):
        self.interval_minutes = interval_minutes
        self.alert_threshold = alert_threshold
        self.running = False
        self.consecutive_failures = 0
        self.last_alert_time = None
        self.alert_cooldown_minutes = 30  # Don't spam alerts
        
        # Load configuration
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        config = {
            'email_alerts': {
                'enabled': os.getenv('EMAIL_ALERTS_ENABLED', 'false').lower() == 'true',
                'smtp_host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
                'smtp_port': int(os.getenv('SMTP_PORT', '587')),
                'smtp_user': os.getenv('SMTP_USER'),
                'smtp_password': os.getenv('SMTP_PASSWORD'),
                'from_email': os.getenv('EMAILS_FROM_EMAIL', 'noreply@foodxchange.com'),
                'to_emails': os.getenv('ALERT_EMAILS', '').split(','),
                'from_name': os.getenv('EMAILS_FROM_NAME', 'FoodXchange Monitor')
            },
            'webhook_alerts': {
                'enabled': os.getenv('WEBHOOK_ALERTS_ENABLED', 'false').lower() == 'true',
                'webhook_url': os.getenv('WEBHOOK_URL'),
                'webhook_secret': os.getenv('WEBHOOK_SECRET')
            },
            'monitoring': {
                'check_interval_minutes': self.interval_minutes,
                'alert_threshold': self.alert_threshold,
                'alert_cooldown_minutes': self.alert_cooldown_minutes
            }
        }
        return config
    
    def should_send_alert(self) -> bool:
        """Check if we should send an alert based on cooldown and threshold"""
        if self.consecutive_failures < self.alert_threshold:
            return False
            
        if self.last_alert_time:
            time_since_last_alert = datetime.now() - self.last_alert_time
            if time_since_last_alert.total_seconds() < (self.alert_cooldown_minutes * 60):
                return False
                
        return True
    
    def send_email_alert(self, subject: str, body: str):
        """Send email alert"""
        if not self.config['email_alerts']['enabled']:
            return
            
        try:
            smtp_config = self.config['email_alerts']
            
            if not smtp_config['smtp_user'] or not smtp_config['smtp_password']:
                logger.warning("Email alerts enabled but SMTP credentials not configured")
                return
                
            msg = MimeMultipart()
            msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
            msg['To'] = ', '.join(smtp_config['to_emails'])
            msg['Subject'] = subject
            
            msg.attach(MimeText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_config['smtp_host'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['smtp_user'], smtp_config['smtp_password'])
            
            text = msg.as_string()
            server.sendmail(smtp_config['from_email'], smtp_config['to_emails'], text)
            server.quit()
            
            logger.info(f"Email alert sent to {smtp_config['to_emails']}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    def send_webhook_alert(self, data: Dict[str, Any]):
        """Send webhook alert"""
        if not self.config['webhook_alerts']['enabled']:
            return
            
        try:
            webhook_config = self.config['webhook_alerts']
            
            if not webhook_config['webhook_url']:
                logger.warning("Webhook alerts enabled but URL not configured")
                return
                
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'FoodXchange-Monitor/1.0'
            }
            
            if webhook_config['webhook_secret']:
                headers['X-Webhook-Secret'] = webhook_config['webhook_secret']
            
            response = requests.post(
                webhook_config['webhook_url'],
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Webhook alert sent successfully")
            else:
                logger.warning(f"Webhook alert failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def send_alert(self, report: Dict[str, Any]):
        """Send alerts through configured channels"""
        if not self.should_send_alert():
            return
            
        # Prepare alert data
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'status': report['summary']['overall_status'],
            'alerts': report['alerts'],
            'critical_alerts': report['summary']['critical_alerts'],
            'total_alerts': report['summary']['total_alerts'],
            'consecutive_failures': self.consecutive_failures
        }
        
        # Email alert
        subject = f"🚨 FoodXchange System Alert - {report['summary']['overall_status'].upper()}"
        body = self.format_email_body(report)
        self.send_email_alert(subject, body)
        
        # Webhook alert
        self.send_webhook_alert(alert_data)
        
        # Update last alert time
        self.last_alert_time = datetime.now()
        logger.info(f"Alert sent for status: {report['summary']['overall_status']}")
    
    def format_email_body(self, report: Dict[str, Any]) -> str:
        """Format email body for alerts"""
        body = f"""
FoodXchange System Monitoring Alert

Status: {report['summary']['overall_status'].upper()}
Timestamp: {report['timestamp']}
Consecutive Failures: {self.consecutive_failures}

ALERTS ({report['summary']['total_alerts']} total, {report['summary']['critical_alerts']} critical):
"""
        
        for alert in report['alerts']:
            body += f"- [{alert['severity'].upper()}] {alert['type']}: {alert['message']}\n"
        
        body += f"""

SYSTEM STATUS:
- Database: {report['database'].get('status', 'Unknown')}
- Application: {report['application'].get('status', 'Unknown')}
- CPU Usage: {report['performance'].get('cpu_usage', 'Unknown')}%
- Memory Usage: {report['performance'].get('memory_usage', 'Unknown')}%

AZURE SERVICES:
"""
        
        for service, info in report['azure_services'].items():
            body += f"- {service.title()}: {info.get('status', 'Unknown')}\n"
            if info.get('error'):
                body += f"  Error: {info['error']}\n"
        
        body += f"""

This is an automated alert from the FoodXchange monitoring system.
Please check the system immediately if status is CRITICAL.

---
FoodXchange Monitoring System
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return body
    
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""
        try:
            logger.info("Starting monitoring cycle...")
            
            # Run system monitor
            monitor = SystemMonitor()
            report = monitor.generate_report()
            
            # Check if we need to send alerts
            status = report['summary']['overall_status']
            
            if status in ['critical', 'error']:
                self.consecutive_failures += 1
                logger.warning(f"System status: {status} (failure #{self.consecutive_failures})")
                
                if self.should_send_alert():
                    self.send_alert(report)
            else:
                # Reset failure counter on success
                if self.consecutive_failures > 0:
                    logger.info(f"System recovered. Previous failures: {self.consecutive_failures}")
                self.consecutive_failures = 0
            
            # Save report
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"monitoring_reports/monitoring_report_{timestamp}.json"
            
            # Ensure directory exists
            os.makedirs('monitoring_reports', exist_ok=True)
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Monitoring cycle completed. Status: {status}")
            
        except Exception as e:
            logger.error(f"Monitoring cycle failed: {e}")
            self.consecutive_failures += 1
    
    def cleanup_old_reports(self, days_to_keep: int = 7):
        """Clean up old monitoring reports"""
        try:
            reports_dir = 'monitoring_reports'
            if not os.path.exists(reports_dir):
                return
                
            cutoff_time = datetime.now() - timedelta(days=days_to_keep)
            
            for filename in os.listdir(reports_dir):
                if filename.startswith('monitoring_report_') and filename.endswith('.json'):
                    filepath = os.path.join(reports_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"Cleaned up old report: {filename}")
                        
        except Exception as e:
            logger.error(f"Failed to cleanup old reports: {e}")
    
    def start(self):
        """Start continuous monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {self.interval_minutes} minutes)")
        logger.info(f"Alert threshold: {self.alert_threshold} consecutive failures")
        logger.info(f"Alert cooldown: {self.alert_cooldown_minutes} minutes")
        
        self.running = True
        
        # Create monitoring reports directory
        os.makedirs('monitoring_reports', exist_ok=True)
        
        # Run initial cleanup
        self.cleanup_old_reports()
        
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"=== Monitoring Cycle #{cycle_count} ===")
                
                # Run monitoring cycle
                self.run_monitoring_cycle()
                
                # Cleanup old reports every 24 cycles (approximately daily)
                if cycle_count % 24 == 0:
                    self.cleanup_old_reports()
                
                # Wait for next cycle
                if self.running:
                    logger.info(f"Waiting {self.interval_minutes} minutes until next cycle...")
                    time.sleep(self.interval_minutes * 60)
                    
            except KeyboardInterrupt:
                logger.info("Monitoring interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
        
        logger.info("Continuous monitoring stopped")
    
    def stop(self):
        """Stop continuous monitoring"""
        logger.info("Stopping continuous monitoring...")
        self.running = False

def main():
    """Main function for continuous monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FoodXchange Continuous System Monitor')
    parser.add_argument('--interval', type=int, default=5, 
                       help='Monitoring interval in minutes (default: 5)')
    parser.add_argument('--threshold', type=int, default=3,
                       help='Alert threshold for consecutive failures (default: 3)')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (background process)')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = ContinuousMonitor(
        interval_minutes=args.interval,
        alert_threshold=args.threshold
    )
    
    if args.daemon:
        # Run as daemon
        import daemon
        with daemon.DaemonContext():
            monitor.start()
    else:
        # Run in foreground
        try:
            monitor.start()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            monitor.stop()

if __name__ == "__main__":
    main() 