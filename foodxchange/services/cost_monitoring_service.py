"""
Cost Monitoring and Alert Service for Azure Usage
Monitors costs and sends alerts when thresholds are exceeded
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class AlertType(Enum):
    COST_THRESHOLD = "cost_threshold"
    LIMIT_WARNING = "limit_warning"
    BUDGET_EXCEEDED = "budget_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"
    DAILY_SUMMARY = "daily_summary"

@dataclass
class CostAlert:
    """Cost alert configuration"""
    id: str
    name: str
    type: AlertType
    threshold: float
    period: str  # daily, weekly, monthly
    services: List[str]  # specific services or ['all']
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    notification_email: Optional[str] = None
    notification_webhook: Optional[str] = None

@dataclass
class AlertEvent:
    """Alert event that was triggered"""
    alert_id: str
    alert_name: str
    type: AlertType
    triggered_at: datetime
    value: float
    threshold: float
    message: str
    details: Dict[str, Any]
    notified: bool = False

class CostMonitoringService:
    """Service for monitoring Azure costs and sending alerts"""
    
    def __init__(self, azure_testing_service):
        self.azure_testing_service = azure_testing_service
        self.alerts: List[CostAlert] = []
        self.alert_history: List[AlertEvent] = []
        self.config_file = "cost_monitoring_config.json"
        self.history_file = "cost_alert_history.json"
        self._load_configuration()
        
    def _load_configuration(self):
        """Load saved configuration and history"""
        # Load alerts configuration
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.alerts = [
                        CostAlert(**{
                            **alert,
                            'type': AlertType(alert['type']),
                            'last_triggered': datetime.fromisoformat(alert['last_triggered']) 
                                            if alert.get('last_triggered') else None
                        })
                        for alert in data.get('alerts', [])
                    ]
            except Exception as e:
                logger.error(f"Error loading cost monitoring config: {e}")
                self._create_default_alerts()
        else:
            self._create_default_alerts()
            
        # Load alert history
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.alert_history = [
                        AlertEvent(**{
                            **event,
                            'type': AlertType(event['type']),
                            'triggered_at': datetime.fromisoformat(event['triggered_at'])
                        })
                        for event in data.get('events', [])
                    ]
            except Exception as e:
                logger.error(f"Error loading alert history: {e}")
                
    def _create_default_alerts(self):
        """Create default alert configurations"""
        self.alerts = [
            CostAlert(
                id='daily_budget',
                name='Daily Budget Alert',
                type=AlertType.COST_THRESHOLD,
                threshold=5.0,  # $5 per day
                period='daily',
                services=['all']
            ),
            CostAlert(
                id='monthly_budget',
                name='Monthly Budget Alert',
                type=AlertType.BUDGET_EXCEEDED,
                threshold=50.0,  # $50 per month
                period='monthly',
                services=['all']
            ),
            CostAlert(
                id='openai_limit',
                name='OpenAI Rate Limit Warning',
                type=AlertType.LIMIT_WARNING,
                threshold=80.0,  # 80% of limit
                period='realtime',
                services=['openai']
            ),
            CostAlert(
                id='cost_anomaly',
                name='Cost Anomaly Detection',
                type=AlertType.ANOMALY_DETECTED,
                threshold=3.0,  # 3x normal usage
                period='hourly',
                services=['all']
            )
        ]
        self._save_configuration()
        
    def _save_configuration(self):
        """Save alerts configuration"""
        try:
            data = {
                'alerts': [
                    {
                        **asdict(alert),
                        'type': alert.type.value,
                        'last_triggered': alert.last_triggered.isoformat() 
                                        if alert.last_triggered else None
                    }
                    for alert in self.alerts
                ]
            }
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cost monitoring config: {e}")
            
    def _save_history(self):
        """Save alert history"""
        try:
            # Keep only last 30 days of history
            cutoff = datetime.now() - timedelta(days=30)
            recent_events = [e for e in self.alert_history if e.triggered_at > cutoff]
            
            data = {
                'events': [
                    {
                        **asdict(event),
                        'type': event.type.value,
                        'triggered_at': event.triggered_at.isoformat()
                    }
                    for event in recent_events
                ]
            }
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving alert history: {e}")
            
    def check_alerts(self) -> List[AlertEvent]:
        """Check all alerts and return triggered ones"""
        triggered_alerts = []
        
        for alert in self.alerts:
            if not alert.enabled:
                continue
                
            # Check if alert should be evaluated
            if self._should_check_alert(alert):
                event = self._evaluate_alert(alert)
                if event:
                    triggered_alerts.append(event)
                    alert.last_triggered = event.triggered_at
                    self.alert_history.append(event)
                    
        # Save updates
        if triggered_alerts:
            self._save_configuration()
            self._save_history()
            
            # Send notifications
            for event in triggered_alerts:
                self._send_notification(event)
                
        return triggered_alerts
        
    def _should_check_alert(self, alert: CostAlert) -> bool:
        """Determine if alert should be checked based on period"""
        if not alert.last_triggered:
            return True
            
        now = datetime.now()
        time_since_last = now - alert.last_triggered
        
        if alert.period == 'realtime':
            return True
        elif alert.period == 'hourly':
            return time_since_last >= timedelta(hours=1)
        elif alert.period == 'daily':
            return time_since_last >= timedelta(days=1)
        elif alert.period == 'weekly':
            return time_since_last >= timedelta(days=7)
        elif alert.period == 'monthly':
            return time_since_last >= timedelta(days=30)
            
        return False
        
    def _evaluate_alert(self, alert: CostAlert) -> Optional[AlertEvent]:
        """Evaluate if alert should be triggered"""
        # Create a copy to avoid dictionary iteration issues
        history = list(self.azure_testing_service.usage_history)
        
        if alert.type == AlertType.COST_THRESHOLD:
            return self._check_cost_threshold(alert, history)
        elif alert.type == AlertType.LIMIT_WARNING:
            return self._check_limit_warning(alert)
        elif alert.type == AlertType.BUDGET_EXCEEDED:
            return self._check_budget_exceeded(alert, history)
        elif alert.type == AlertType.ANOMALY_DETECTED:
            return self._check_anomaly(alert, history)
            
        return None
        
    def _check_cost_threshold(self, alert: CostAlert, history: List) -> Optional[AlertEvent]:
        """Check if cost threshold is exceeded"""
        now = datetime.now()
        
        # Get relevant time period
        if alert.period == 'daily':
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif alert.period == 'weekly':
            start_time = now - timedelta(days=7)
        elif alert.period == 'monthly':
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_time = now - timedelta(hours=1)
            
        # Calculate cost for period
        period_cost = sum(
            h.estimated_cost for h in history
            if h.timestamp > start_time and (
                'all' in alert.services or h.service in alert.services
            )
        )
        
        if period_cost > alert.threshold:
            return AlertEvent(
                alert_id=alert.id,
                alert_name=alert.name,
                type=alert.type,
                triggered_at=now,
                value=period_cost,
                threshold=alert.threshold,
                message=f"{alert.name}: ${period_cost:.2f} exceeds threshold of ${alert.threshold:.2f}",
                details={
                    'period': alert.period,
                    'services': alert.services,
                    'cost_breakdown': self._get_cost_breakdown(history, start_time, alert.services)
                }
            )
            
        return None
        
    def _check_limit_warning(self, alert: CostAlert) -> Optional[AlertEvent]:
        """Check if service limits are approaching"""
        limits_status = self.azure_testing_service.get_current_limits_status()
        
        for service in alert.services:
            if service in limits_status:
                service_limits = limits_status[service]
                
                for metric, value in service_limits.items():
                    if '_percentage' in metric and value >= alert.threshold:
                        return AlertEvent(
                            alert_id=alert.id,
                            alert_name=alert.name,
                            type=alert.type,
                            triggered_at=datetime.now(),
                            value=value,
                            threshold=alert.threshold,
                            message=f"{service} {metric.replace('_percentage', '')} at {value:.1f}% of limit",
                            details={
                                'service': service,
                                'metric': metric,
                                'current_usage': service_limits.get(metric.replace('_percentage', '_used'), 0),
                                'limit': service_limits.get(metric.replace('_percentage', '_limit'), 0)
                            }
                        )
                        
        return None
        
    def _check_budget_exceeded(self, alert: CostAlert, history: List) -> Optional[AlertEvent]:
        """Check if budget is exceeded"""
        now = datetime.now()
        
        if alert.period == 'monthly':
            start_time = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            start_time = now - timedelta(days=30)
            
        period_cost = sum(
            h.estimated_cost for h in history
            if h.timestamp > start_time and (
                'all' in alert.services or h.service in alert.services
            )
        )
        
        if period_cost > alert.threshold:
            # Calculate projected end-of-period cost
            days_elapsed = (now - start_time).days + 1
            days_in_period = 30 if alert.period == 'monthly' else 30
            projected_cost = (period_cost / days_elapsed) * days_in_period
            
            return AlertEvent(
                alert_id=alert.id,
                alert_name=alert.name,
                type=alert.type,
                triggered_at=now,
                value=period_cost,
                threshold=alert.threshold,
                message=f"Budget exceeded: ${period_cost:.2f} spent (${alert.threshold:.2f} budget)",
                details={
                    'period': alert.period,
                    'days_elapsed': days_elapsed,
                    'projected_cost': projected_cost,
                    'daily_average': period_cost / days_elapsed,
                    'services': self._get_cost_breakdown(history, start_time, alert.services)
                }
            )
            
        return None
        
    def _check_anomaly(self, alert: CostAlert, history: List) -> Optional[AlertEvent]:
        """Check for cost anomalies"""
        now = datetime.now()
        
        # Get last hour's cost
        hour_ago = now - timedelta(hours=1)
        last_hour_cost = sum(
            h.estimated_cost for h in history
            if h.timestamp > hour_ago
        )
        
        # Get average hourly cost for last 7 days
        week_ago = now - timedelta(days=7)
        week_history = [h for h in history if h.timestamp > week_ago and h.timestamp < hour_ago]
        
        if len(week_history) > 0:
            total_week_cost = sum(h.estimated_cost for h in week_history)
            hours_in_week = (hour_ago - week_ago).total_seconds() / 3600
            avg_hourly_cost = total_week_cost / hours_in_week
            
            if avg_hourly_cost > 0 and last_hour_cost > (avg_hourly_cost * alert.threshold):
                return AlertEvent(
                    alert_id=alert.id,
                    alert_name=alert.name,
                    type=alert.type,
                    triggered_at=now,
                    value=last_hour_cost,
                    threshold=avg_hourly_cost * alert.threshold,
                    message=f"Cost anomaly detected: ${last_hour_cost:.2f} in last hour ({alert.threshold}x normal)",
                    details={
                        'last_hour_cost': last_hour_cost,
                        'average_hourly_cost': avg_hourly_cost,
                        'multiplier': last_hour_cost / avg_hourly_cost if avg_hourly_cost > 0 else 0,
                        'operations': self._get_recent_operations(history, hour_ago)
                    }
                )
                
        return None
        
    def _get_cost_breakdown(self, history: List, start_time: datetime, 
                           services: List[str]) -> Dict[str, float]:
        """Get cost breakdown by service"""
        breakdown = {}
        
        for h in history:
            if h.timestamp > start_time and (
                'all' in services or h.service in services
            ):
                if h.service not in breakdown:
                    breakdown[h.service] = 0
                breakdown[h.service] += h.estimated_cost
                
        return breakdown
        
    def _get_recent_operations(self, history: List, start_time: datetime) -> List[Dict[str, Any]]:
        """Get recent operations for anomaly analysis"""
        recent = []
        
        for h in history:
            if h.timestamp > start_time:
                recent.append({
                    'timestamp': h.timestamp.isoformat(),
                    'service': h.service,
                    'operation': h.operation,
                    'cost': h.estimated_cost,
                    'success': h.success
                })
                
        return sorted(recent, key=lambda x: x['cost'], reverse=True)[:10]
        
    def _send_notification(self, event: AlertEvent):
        """Send notification for triggered alert"""
        alert = next((a for a in self.alerts if a.id == event.alert_id), None)
        if not alert:
            return
            
        # Log the alert
        logger.warning(f"Cost Alert: {event.message}")
        
        # Send email if configured
        if alert.notification_email and os.getenv('SMTP_SERVER'):
            try:
                self._send_email_notification(alert, event)
                event.notified = True
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}")
                
        # Send webhook if configured
        if alert.notification_webhook:
            try:
                self._send_webhook_notification(alert, event)
                event.notified = True
            except Exception as e:
                logger.error(f"Failed to send webhook notification: {e}")
                
    def _send_email_notification(self, alert: CostAlert, event: AlertEvent):
        """Send email notification"""
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_user = os.getenv('SMTP_USER')
        smtp_pass = os.getenv('SMTP_PASS')
        
        if not all([smtp_server, smtp_user, smtp_pass]):
            return
            
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = alert.notification_email
        msg['Subject'] = f"FoodXchange Cost Alert: {event.alert_name}"
        
        body = f"""
Cost Alert Triggered

Alert: {event.alert_name}
Type: {event.type.value}
Time: {event.triggered_at.strftime('%Y-%m-%d %H:%M:%S')}

{event.message}

Current Value: ${event.value:.2f}
Threshold: ${event.threshold:.2f}

Details:
{json.dumps(event.details, indent=2)}

--
FoodXchange Cost Monitoring
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            
    def _send_webhook_notification(self, alert: CostAlert, event: AlertEvent):
        """Send webhook notification"""
        import requests
        
        payload = {
            'alert_id': event.alert_id,
            'alert_name': event.alert_name,
            'type': event.type.value,
            'triggered_at': event.triggered_at.isoformat(),
            'message': event.message,
            'value': event.value,
            'threshold': event.threshold,
            'details': event.details
        }
        
        response = requests.post(
            alert.notification_webhook,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
    def add_alert(self, alert: CostAlert) -> bool:
        """Add a new alert"""
        # Check for duplicate ID
        if any(a.id == alert.id for a in self.alerts):
            return False
            
        self.alerts.append(alert)
        self._save_configuration()
        return True
        
    def update_alert(self, alert_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing alert"""
        alert = next((a for a in self.alerts if a.id == alert_id), None)
        if not alert:
            return False
            
        for key, value in updates.items():
            if hasattr(alert, key):
                if key == 'type':
                    value = AlertType(value)
                setattr(alert, key, value)
                
        self._save_configuration()
        return True
        
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        self.alerts = [a for a in self.alerts if a.id != alert_id]
        self._save_configuration()
        return True
        
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alerts and recent events"""
        now = datetime.now()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        
        recent_events = [e for e in self.alert_history if e.triggered_at > day_ago]
        week_events = [e for e in self.alert_history if e.triggered_at > week_ago]
        
        return {
            'total_alerts': len(self.alerts),
            'enabled_alerts': sum(1 for a in self.alerts if a.enabled),
            'events_last_24h': len(recent_events),
            'events_last_7d': len(week_events),
            'alerts': [
                {
                    **asdict(alert),
                    'type': alert.type.value,
                    'last_triggered': alert.last_triggered.isoformat() 
                                    if alert.last_triggered else None
                }
                for alert in self.alerts
            ],
            'recent_events': [
                {
                    **asdict(event),
                    'type': event.type.value,
                    'triggered_at': event.triggered_at.isoformat()
                }
                for event in recent_events
            ]
        }

# Export function to create monitoring service
def create_monitoring_service(azure_testing_service):
    """Create cost monitoring service instance"""
    return CostMonitoringService(azure_testing_service)