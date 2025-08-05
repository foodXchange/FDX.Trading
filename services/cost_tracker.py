"""
Cost Tracking Service for Microsoft Founders Hub
Real-time tracking of Azure service usage and costs
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal

class CostTracker:
    """Track and optimize Azure service costs"""
    
    # Pricing as of 2025 (approximate)
    PRICING = {
        'openai': {
            'gpt-4o-mini': {
                'input': 0.00015,  # per 1K tokens
                'output': 0.0006   # per 1K tokens
            },
            'gpt-4o': {
                'input': 0.005,    # per 1K tokens
                'output': 0.015    # per 1K tokens
            }
        },
        'postgresql': {
            'flexible_b1ms': 12.41,    # per month
            'flexible_b2s': 24.82,     # per month
            'storage_gb': 0.115        # per GB per month
        },
        'monitoring': {
            'app_insights_gb': 2.30,   # per GB ingested
            'log_analytics_gb': 2.30,  # per GB ingested
            'metrics_series': 0.16     # per metric time series per month
        }
    }
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self._create_tables()
    
    def _create_tables(self):
        """Create cost tracking tables"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        
        cur.execute("""
            CREATE TABLE IF NOT EXISTS cost_tracking (
                id SERIAL PRIMARY KEY,
                service VARCHAR(50) NOT NULL,
                resource VARCHAR(100),
                usage_amount DECIMAL(10, 4),
                usage_unit VARCHAR(50),
                cost DECIMAL(10, 4),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB
            );
            
            CREATE INDEX IF NOT EXISTS idx_cost_tracking_timestamp 
            ON cost_tracking(timestamp);
            
            CREATE INDEX IF NOT EXISTS idx_cost_tracking_service 
            ON cost_tracking(service);
            
            CREATE TABLE IF NOT EXISTS cost_alerts (
                id SERIAL PRIMARY KEY,
                alert_name VARCHAR(100),
                threshold DECIMAL(10, 2),
                current_value DECIMAL(10, 2),
                triggered_at TIMESTAMP,
                alert_type VARCHAR(50),
                status VARCHAR(50) DEFAULT 'active'
            );
            
            CREATE TABLE IF NOT EXISTS cost_budgets (
                id SERIAL PRIMARY KEY,
                service VARCHAR(50),
                monthly_budget DECIMAL(10, 2),
                alert_thresholds JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
    
    def track_openai_usage(self, model: str, input_tokens: int, output_tokens: int, 
                          metadata: Dict = None):
        """Track OpenAI API usage and costs"""
        pricing = self.PRICING['openai'].get(model, self.PRICING['openai']['gpt-4o-mini'])
        
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        total_cost = input_cost + output_cost
        
        self._record_cost(
            service='openai',
            resource=model,
            usage_amount=input_tokens + output_tokens,
            usage_unit='tokens',
            cost=total_cost,
            metadata={
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'input_cost': input_cost,
                'output_cost': output_cost,
                **(metadata or {})
            }
        )
        
        # Check budget alerts
        self._check_budget_alerts('openai')
        
        return total_cost
    
    def track_database_usage(self, storage_gb: float, compute_hours: float = 24):
        """Track PostgreSQL usage (daily)"""
        # Assume B2S tier
        daily_compute_cost = (self.PRICING['postgresql']['flexible_b2s'] / 30)
        storage_cost = (storage_gb * self.PRICING['postgresql']['storage_gb'] / 30)
        total_cost = daily_compute_cost + storage_cost
        
        self._record_cost(
            service='postgresql',
            resource='flexible_server_b2s',
            usage_amount=compute_hours,
            usage_unit='hours',
            cost=total_cost,
            metadata={
                'storage_gb': storage_gb,
                'storage_cost': storage_cost,
                'compute_cost': daily_compute_cost
            }
        )
        
        return total_cost
    
    def track_monitoring_usage(self, data_ingested_gb: float, metric_series: int = 100):
        """Track monitoring services usage"""
        data_cost = data_ingested_gb * self.PRICING['monitoring']['app_insights_gb']
        metrics_cost = (metric_series * self.PRICING['monitoring']['metrics_series'] / 30)
        total_cost = data_cost + metrics_cost
        
        self._record_cost(
            service='monitoring',
            resource='app_insights',
            usage_amount=data_ingested_gb,
            usage_unit='GB',
            cost=total_cost,
            metadata={
                'data_gb': data_ingested_gb,
                'metric_series': metric_series,
                'data_cost': data_cost,
                'metrics_cost': metrics_cost
            }
        )
        
        return total_cost
    
    def _record_cost(self, service: str, resource: str, usage_amount: float, 
                    usage_unit: str, cost: float, metadata: Dict = None):
        """Record cost entry in database"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO cost_tracking 
            (service, resource, usage_amount, usage_unit, cost, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            service,
            resource,
            usage_amount,
            usage_unit,
            cost,
            json.dumps(metadata or {})
        ))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def get_current_spend(self, period: str = 'month') -> Dict:
        """Get current spending by service"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Determine period
        if period == 'month':
            start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        elif period == 'day':
            start_date = datetime.now().replace(hour=0, minute=0, second=0)
        else:
            start_date = datetime.now() - timedelta(days=30)
        
        # Get spending by service
        cur.execute("""
            SELECT 
                service,
                SUM(cost) as total_cost,
                COUNT(*) as transaction_count,
                MAX(timestamp) as last_usage
            FROM cost_tracking
            WHERE timestamp >= %s
            GROUP BY service
            ORDER BY total_cost DESC
        """, (start_date,))
        
        by_service = cur.fetchall()
        
        # Get total
        cur.execute("""
            SELECT SUM(cost) as total
            FROM cost_tracking
            WHERE timestamp >= %s
        """, (start_date,))
        
        total = cur.fetchone()['total'] or 0
        
        # Get daily trend
        cur.execute("""
            SELECT 
                DATE(timestamp) as date,
                SUM(cost) as daily_cost
            FROM cost_tracking
            WHERE timestamp >= %s
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (start_date - timedelta(days=7),))
        
        daily_trend = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            'period': period,
            'start_date': start_date.isoformat(),
            'total_spend': float(total),
            'by_service': by_service,
            'daily_trend': daily_trend,
            'founders_hub_credits': {
                'monthly_credits': 5000,  # Assuming base tier
                'remaining': max(0, 5000 - float(total)),
                'percentage_used': min(100, (float(total) / 5000) * 100)
            }
        }
    
    def set_budget_alerts(self, service: str, monthly_budget: float, 
                         alert_thresholds: List[float] = None):
        """Set budget alerts for a service"""
        if alert_thresholds is None:
            alert_thresholds = [0.5, 0.8, 1.0, 1.2]  # 50%, 80%, 100%, 120%
        
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO cost_budgets (service, monthly_budget, alert_thresholds)
            VALUES (%s, %s, %s)
            ON CONFLICT (service) DO UPDATE
            SET monthly_budget = EXCLUDED.monthly_budget,
                alert_thresholds = EXCLUDED.alert_thresholds,
                updated_at = CURRENT_TIMESTAMP
        """, (service, monthly_budget, json.dumps(alert_thresholds)))
        
        conn.commit()
        cur.close()
        conn.close()
    
    def _check_budget_alerts(self, service: str):
        """Check if any budget alerts should be triggered"""
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get budget
        cur.execute("""
            SELECT monthly_budget, alert_thresholds
            FROM cost_budgets
            WHERE service = %s
        """, (service,))
        
        budget_info = cur.fetchone()
        if not budget_info:
            cur.close()
            conn.close()
            return
        
        # Get current month spend
        cur.execute("""
            SELECT SUM(cost) as total
            FROM cost_tracking
            WHERE service = %s
            AND DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', CURRENT_DATE)
        """, (service,))
        
        current_spend = cur.fetchone()['total'] or 0
        monthly_budget = budget_info['monthly_budget']
        
        # Check thresholds
        for threshold in budget_info['alert_thresholds']:
            alert_value = monthly_budget * threshold
            alert_name = f"{service}_budget_{int(threshold * 100)}pct"
            
            if current_spend >= alert_value:
                # Check if alert already triggered this month
                cur.execute("""
                    SELECT id FROM cost_alerts
                    WHERE alert_name = %s
                    AND DATE_TRUNC('month', triggered_at) = DATE_TRUNC('month', CURRENT_DATE)
                    AND status = 'active'
                """, (alert_name,))
                
                if not cur.fetchone():
                    # Trigger new alert
                    cur.execute("""
                        INSERT INTO cost_alerts 
                        (alert_name, threshold, current_value, triggered_at, alert_type)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        alert_name,
                        alert_value,
                        current_spend,
                        datetime.now(),
                        'budget_threshold'
                    ))
                    
                    print(f"BUDGET ALERT: {service} has reached {threshold * 100}% of monthly budget!")
        
        conn.commit()
        cur.close()
        conn.close()
    
    def get_optimization_recommendations(self) -> List[Dict]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check OpenAI usage patterns
        cur.execute("""
            SELECT 
                AVG((metadata->>'input_tokens')::int) as avg_input_tokens,
                AVG((metadata->>'output_tokens')::int) as avg_output_tokens,
                COUNT(*) as request_count
            FROM cost_tracking
            WHERE service = 'openai'
            AND timestamp > NOW() - INTERVAL '7 days'
        """)
        
        openai_stats = cur.fetchone()
        
        if openai_stats and openai_stats['request_count'] > 0:
            avg_input = openai_stats['avg_input_tokens'] or 0
            avg_output = openai_stats['avg_output_tokens'] or 0
            
            if avg_input > 1000:
                recommendations.append({
                    'service': 'openai',
                    'issue': 'High input token usage',
                    'recommendation': 'Consider optimizing prompts to be more concise',
                    'potential_savings': '20-30%'
                })
            
            if avg_output > 500:
                recommendations.append({
                    'service': 'openai',
                    'issue': 'High output token usage',
                    'recommendation': f'Reduce max_tokens from current to {int(avg_output * 0.8)}',
                    'potential_savings': '15-20%'
                })
        
        # Check for unused resources
        cur.execute("""
            SELECT service, MAX(timestamp) as last_used
            FROM cost_tracking
            GROUP BY service
            HAVING MAX(timestamp) < NOW() - INTERVAL '7 days'
        """)
        
        unused = cur.fetchall()
        for resource in unused:
            recommendations.append({
                'service': resource['service'],
                'issue': 'Service not used in 7+ days',
                'recommendation': 'Consider pausing or removing this service',
                'potential_savings': '100%'
            })
        
        cur.close()
        conn.close()
        
        return recommendations
    
    def generate_cost_report(self, month: str = None) -> Dict:
        """Generate detailed cost report"""
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get summary
        cur.execute("""
            SELECT 
                service,
                resource,
                SUM(cost) as total_cost,
                SUM(usage_amount) as total_usage,
                COUNT(*) as transaction_count,
                MIN(timestamp) as first_usage,
                MAX(timestamp) as last_usage
            FROM cost_tracking
            WHERE TO_CHAR(timestamp, 'YYYY-MM') = %s
            GROUP BY service, resource
            ORDER BY total_cost DESC
        """, (month,))
        
        details = cur.fetchall()
        
        # Get daily breakdown
        cur.execute("""
            SELECT 
                DATE(timestamp) as date,
                service,
                SUM(cost) as daily_cost
            FROM cost_tracking
            WHERE TO_CHAR(timestamp, 'YYYY-MM') = %s
            GROUP BY DATE(timestamp), service
            ORDER BY date, service
        """, (month,))
        
        daily_breakdown = cur.fetchall()
        
        # Calculate totals
        total_cost = sum(d['total_cost'] for d in details)
        
        cur.close()
        conn.close()
        
        return {
            'month': month,
            'total_cost': total_cost,
            'founders_hub_status': {
                'credits_used': total_cost,
                'credits_remaining': max(0, 5000 - total_cost),
                'next_credit_date': (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).strftime('%Y-%m-%d')
            },
            'service_breakdown': details,
            'daily_breakdown': daily_breakdown,
            'recommendations': self.get_optimization_recommendations(),
            'generated_at': datetime.now().isoformat()
        }


# Singleton instance
_cost_tracker = None

def get_cost_tracker() -> CostTracker:
    """Get singleton cost tracker instance"""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker