"""
Azure Monitoring Service for Microsoft Founders Hub
Implements monitoring to qualify for additional credits
Requirement: Spend $100+/month on monitoring services
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from azure.monitor.query import LogsQueryClient, MetricsQueryClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import requests

class AzureMonitoringService:
    """
    Implements Azure monitoring services to qualify for additional credits:
    - Application Insights
    - Log Analytics
    - Azure Monitor Metrics
    - Cost tracking
    """
    
    def __init__(self):
        # Azure credentials
        self.credential = DefaultAzureCredential()
        
        # Initialize clients
        self.logs_client = LogsQueryClient(self.credential)
        self.metrics_client = MetricsQueryClient(self.credential)
        
        # Configuration from environment
        self.workspace_id = os.getenv('AZURE_LOG_ANALYTICS_WORKSPACE_ID')
        self.app_insights_key = os.getenv('AZURE_APP_INSIGHTS_KEY')
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'foodxchange-rg')
        
        # Database connection
        self.db_url = os.getenv('DATABASE_URL')
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure Azure Application Insights logging"""
        if self.app_insights_key:
            # Setup Application Insights handler
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            
            logger = logging.getLogger(__name__)
            logger.addHandler(AzureLogHandler(
                connection_string=f'InstrumentationKey={self.app_insights_key}'
            ))
            logger.setLevel(logging.INFO)
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
    
    def track_event(self, event_name: str, properties: Dict = None, measurements: Dict = None):
        """Track custom events in Application Insights"""
        try:
            if self.app_insights_key:
                from applicationinsights import TelemetryClient
                tc = TelemetryClient(self.app_insights_key)
                tc.track_event(event_name, properties or {}, measurements or {})
                tc.flush()
            
            # Also log to database for redundancy
            self._log_to_database('event', event_name, properties, measurements)
            
        except Exception as e:
            print(f"Error tracking event: {e}")
    
    def track_metric(self, metric_name: str, value: float, properties: Dict = None):
        """Track custom metrics"""
        try:
            if self.app_insights_key:
                from applicationinsights import TelemetryClient
                tc = TelemetryClient(self.app_insights_key)
                tc.track_metric(metric_name, value, properties=properties)
                tc.flush()
            
            self._log_to_database('metric', metric_name, {'value': value}, properties)
            
        except Exception as e:
            print(f"Error tracking metric: {e}")
    
    def track_api_request(self, method: str, url: str, duration_ms: int, 
                         success: bool, response_code: int = 200):
        """Track API requests for performance monitoring"""
        self.track_event('api_request', {
            'method': method,
            'url': url,
            'success': str(success),
            'response_code': str(response_code)
        }, {
            'duration_ms': duration_ms
        })
    
    def track_database_query(self, query_type: str, table: str, duration_ms: int):
        """Track database query performance"""
        self.track_metric('db_query_duration', duration_ms, {
            'query_type': query_type,
            'table': table
        })
    
    def track_email_sent(self, supplier_id: int, template_type: str, tokens_used: int):
        """Track email sending metrics"""
        self.track_event('email_sent', {
            'supplier_id': str(supplier_id),
            'template_type': template_type
        }, {
            'tokens_used': tokens_used
        })
    
    def track_cost_metric(self, service: str, cost: float, usage_type: str = 'api_call'):
        """Track Azure service costs"""
        self.track_metric('azure_cost', cost, {
            'service': service,
            'usage_type': usage_type
        })
        
        # Track OpenAI specific costs
        if service == 'openai':
            self.track_metric('openai_tokens_cost', cost, {
                'model': os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4o-mini')
            })
    
    def get_application_health(self) -> Dict:
        """Get application health metrics"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get various health metrics
            metrics = {}
            
            # Database health
            cur.execute("SELECT COUNT(*) as count FROM suppliers")
            metrics['total_suppliers'] = cur.fetchone()['count']
            
            # Email metrics (last 24h)
            cur.execute("""
                SELECT 
                    COUNT(*) as total_emails,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    SUM(tokens_used) as total_tokens
                FROM email_log 
                WHERE sent_at > NOW() - INTERVAL '24 hours'
            """)
            email_stats = cur.fetchone()
            metrics['email_24h'] = email_stats
            
            # API usage (if tracked)
            cur.execute("""
                SELECT COUNT(*) as api_calls 
                FROM monitoring_logs 
                WHERE log_type = 'event' 
                AND event_name = 'api_request'
                AND created_at > NOW() - INTERVAL '1 hour'
            """)
            metrics['api_calls_hour'] = cur.fetchone()['count']
            
            cur.close()
            conn.close()
            
            # Track the health check itself
            self.track_event('health_check', metrics)
            
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def setup_cost_alerts(self, monthly_budget: float = 100):
        """Setup Azure cost alerts"""
        alert_rules = {
            '50_percent': monthly_budget * 0.5,
            '80_percent': monthly_budget * 0.8,
            '100_percent': monthly_budget,
            '110_percent': monthly_budget * 1.1  # Overage alert
        }
        
        # Log alert configuration
        self.track_event('cost_alerts_configured', {
            'monthly_budget': str(monthly_budget),
            'alerts': json.dumps(alert_rules)
        })
        
        return alert_rules
    
    def get_cost_analysis(self, days: int = 30) -> Dict:
        """Analyze costs for the specified period"""
        try:
            # This would integrate with Azure Cost Management API
            # For now, we'll estimate based on tracked metrics
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get token usage
            cur.execute("""
                SELECT 
                    DATE(sent_at) as date,
                    SUM(tokens_used) as daily_tokens
                FROM email_log
                WHERE sent_at > NOW() - INTERVAL '%s days'
                GROUP BY DATE(sent_at)
                ORDER BY date DESC
            """, (days,))
            
            token_usage = cur.fetchall()
            
            # Calculate costs
            cost_per_1k_tokens = 0.00015  # gpt-4o-mini pricing
            total_tokens = sum(day['daily_tokens'] or 0 for day in token_usage)
            openai_cost = (total_tokens / 1000) * cost_per_1k_tokens
            
            # Estimate other costs
            postgres_cost = 25  # Estimated monthly
            monitoring_cost = 50  # Target for credit qualification
            
            cur.close()
            conn.close()
            
            analysis = {
                'period_days': days,
                'costs': {
                    'openai': round(openai_cost, 2),
                    'postgresql': round(postgres_cost * days / 30, 2),
                    'monitoring': round(monitoring_cost * days / 30, 2),
                    'total': round(openai_cost + (postgres_cost + monitoring_cost) * days / 30, 2)
                },
                'token_usage': {
                    'total': total_tokens,
                    'daily_average': round(total_tokens / max(len(token_usage), 1), 0)
                },
                'qualification_status': {
                    'target_spend': 100,
                    'current_monitoring_spend': round(monitoring_cost, 2),
                    'qualified': monitoring_cost >= 100
                }
            }
            
            # Track cost analysis
            self.track_event('cost_analysis_generated', analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Cost analysis failed: {e}")
            return {'error': str(e)}
    
    def _log_to_database(self, log_type: str, event_name: str, 
                        properties: Dict = None, measurements: Dict = None):
        """Log monitoring data to database"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Create monitoring table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS monitoring_logs (
                    id SERIAL PRIMARY KEY,
                    log_type VARCHAR(50),
                    event_name VARCHAR(255),
                    properties JSONB,
                    measurements JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert log
            cur.execute("""
                INSERT INTO monitoring_logs (log_type, event_name, properties, measurements)
                VALUES (%s, %s, %s, %s)
            """, (
                log_type,
                event_name,
                json.dumps(properties or {}),
                json.dumps(measurements or {})
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Database logging error: {e}")
    
    def export_metrics_for_billing(self, month: str = None) -> Dict:
        """Export metrics for Azure billing verification"""
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get all monitoring service usage
            cur.execute("""
                SELECT 
                    log_type,
                    COUNT(*) as event_count,
                    DATE_TRUNC('day', created_at) as date
                FROM monitoring_logs
                WHERE TO_CHAR(created_at, 'YYYY-MM') = %s
                GROUP BY log_type, DATE_TRUNC('day', created_at)
                ORDER BY date
            """, (month,))
            
            usage_data = cur.fetchall()
            
            cur.close()
            conn.close()
            
            # Format for export
            export_data = {
                'month': month,
                'monitoring_services': {
                    'application_insights': True,
                    'log_analytics': bool(self.workspace_id),
                    'metrics': True
                },
                'usage_summary': usage_data,
                'export_date': datetime.now().isoformat()
            }
            
            # Track export
            self.track_event('metrics_exported', {'month': month})
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Metrics export failed: {e}")
            return {'error': str(e)}


# Singleton instance
_monitoring_service = None

def get_monitoring_service() -> AzureMonitoringService:
    """Get singleton monitoring service instance"""
    global _monitoring_service
    if _monitoring_service is None:
        _monitoring_service = AzureMonitoringService()
    return _monitoring_service