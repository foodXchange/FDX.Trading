"""
Usage Analytics Service for Azure Testing
Provides detailed analytics, insights, and cost projections
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class UsageInsight:
    """Analytics insight"""
    type: str  # cost_spike, limit_warning, optimization, pattern
    severity: str  # info, warning, critical
    title: str
    description: str
    recommendation: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class UsageAnalyticsService:
    """Service for analyzing Azure usage patterns and providing insights"""
    
    def __init__(self, azure_testing_service):
        self.azure_testing_service = azure_testing_service
        self.insights_cache = []
        self.analytics_file = "azure_usage_analytics.json"
        self._load_analytics()
        
    def _load_analytics(self):
        """Load saved analytics data"""
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, 'r') as f:
                    data = json.load(f)
                    self.insights_cache = [
                        UsageInsight(**{
                            **item,
                            'timestamp': datetime.fromisoformat(item['timestamp'])
                        })
                        for item in data.get('insights', [])
                    ]
            except Exception as e:
                logger.error(f"Error loading analytics: {e}")
                
    def _save_analytics(self):
        """Save analytics data"""
        try:
            data = {
                'insights': [
                    {**asdict(insight), 'timestamp': insight.timestamp.isoformat()}
                    for insight in self.insights_cache
                ],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.analytics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")
            
    def analyze_usage_patterns(self) -> Dict[str, Any]:
        """Analyze usage patterns and generate insights"""
        history = self.azure_testing_service.usage_history
        
        if not history:
            return {
                'patterns': {},
                'insights': [],
                'recommendations': []
            }
            
        # Convert to DataFrame for analysis
        df = pd.DataFrame([asdict(h) for h in history])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        patterns = {
            'hourly': self._analyze_hourly_patterns(df),
            'daily': self._analyze_daily_patterns(df),
            'service': self._analyze_service_patterns(df),
            'cost': self._analyze_cost_patterns(df),
            'errors': self._analyze_error_patterns(df)
        }
        
        # Generate insights
        insights = self._generate_insights(patterns, df)
        
        # Save insights
        self.insights_cache.extend(insights)
        self._save_analytics()
        
        return {
            'patterns': patterns,
            'insights': [asdict(i) for i in insights],
            'recommendations': self._generate_recommendations(patterns, insights)
        }
        
    def _analyze_hourly_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze hourly usage patterns"""
        df['hour'] = df['timestamp'].dt.hour
        
        hourly_stats = df.groupby('hour').agg({
            'api_calls': 'count',
            'estimated_cost': 'sum',
            'processing_time': 'mean',
            'success': lambda x: x.sum() / len(x) if len(x) > 0 else 0
        }).to_dict('index')
        
        # Find peak hours
        peak_hours = sorted(hourly_stats.items(), 
                          key=lambda x: x[1]['api_calls'], 
                          reverse=True)[:3]
        
        return {
            'stats': hourly_stats,
            'peak_hours': [h[0] for h in peak_hours],
            'peak_cost_hour': max(hourly_stats.items(), 
                                 key=lambda x: x[1]['estimated_cost'])[0]
        }
        
    def _analyze_daily_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze daily usage patterns"""
        df['date'] = df['timestamp'].dt.date
        
        daily_stats = df.groupby('date').agg({
            'api_calls': 'count',
            'estimated_cost': 'sum',
            'processing_time': 'mean',
            'tokens_used': 'sum',
            'characters_processed': 'sum'
        })
        
        # Calculate trends
        if len(daily_stats) > 1:
            cost_trend = np.polyfit(range(len(daily_stats)), 
                                  daily_stats['estimated_cost'].values, 1)[0]
            usage_trend = np.polyfit(range(len(daily_stats)), 
                                   daily_stats['api_calls'].values, 1)[0]
        else:
            cost_trend = 0
            usage_trend = 0
            
        return {
            'stats': daily_stats.to_dict('index'),
            'cost_trend': cost_trend,  # positive = increasing
            'usage_trend': usage_trend,
            'average_daily_cost': daily_stats['estimated_cost'].mean(),
            'max_daily_cost': daily_stats['estimated_cost'].max()
        }
        
    def _analyze_service_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns by service"""
        service_stats = {}
        
        for service in df['service'].unique():
            service_df = df[df['service'] == service]
            
            service_stats[service] = {
                'total_calls': len(service_df),
                'total_cost': service_df['estimated_cost'].sum(),
                'success_rate': service_df['success'].mean(),
                'avg_processing_time': service_df['processing_time'].mean(),
                'operations': service_df['operation'].value_counts().to_dict(),
                'peak_usage_hour': service_df['timestamp'].dt.hour.mode().values[0] if len(service_df) > 0 else None
            }
            
        return service_stats
        
    def _analyze_cost_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze cost patterns"""
        # Cost by operation
        cost_by_operation = df.groupby('operation')['estimated_cost'].agg(['sum', 'mean', 'count'])
        
        # Cost spikes
        df['cost_zscore'] = (df['estimated_cost'] - df['estimated_cost'].mean()) / df['estimated_cost'].std()
        cost_spikes = df[df['cost_zscore'] > 2][['timestamp', 'operation', 'estimated_cost']].to_dict('records')
        
        # Projected monthly cost
        days_of_data = (df['timestamp'].max() - df['timestamp'].min()).days + 1
        if days_of_data > 0:
            daily_avg_cost = df['estimated_cost'].sum() / days_of_data
            projected_monthly = daily_avg_cost * 30
        else:
            projected_monthly = 0
            
        return {
            'by_operation': cost_by_operation.to_dict('index'),
            'spikes': cost_spikes,
            'projected_monthly': projected_monthly,
            'total_spent': df['estimated_cost'].sum(),
            'most_expensive_operation': cost_by_operation['sum'].idxmax() if len(cost_by_operation) > 0 else None
        }
        
    def _analyze_error_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze error patterns"""
        errors_df = df[~df['success']]
        
        if len(errors_df) == 0:
            return {
                'total_errors': 0,
                'error_rate': 0,
                'by_service': {},
                'common_errors': []
            }
            
        error_patterns = {
            'total_errors': len(errors_df),
            'error_rate': len(errors_df) / len(df),
            'by_service': errors_df['service'].value_counts().to_dict(),
            'by_operation': errors_df['operation'].value_counts().to_dict(),
            'common_errors': []
        }
        
        # Analyze error messages
        if 'error_message' in errors_df.columns:
            error_messages = errors_df['error_message'].dropna()
            if len(error_messages) > 0:
                # Group similar errors
                error_groups = defaultdict(int)
                for msg in error_messages:
                    if 'limit' in str(msg).lower():
                        error_groups['Rate/Limit Errors'] += 1
                    elif 'auth' in str(msg).lower() or 'key' in str(msg).lower():
                        error_groups['Authentication Errors'] += 1
                    elif 'timeout' in str(msg).lower():
                        error_groups['Timeout Errors'] += 1
                    else:
                        error_groups['Other Errors'] += 1
                        
                error_patterns['common_errors'] = [
                    {'type': k, 'count': v} 
                    for k, v in sorted(error_groups.items(), 
                                     key=lambda x: x[1], 
                                     reverse=True)
                ]
                
        return error_patterns
        
    def _generate_insights(self, patterns: Dict[str, Any], df: pd.DataFrame) -> List[UsageInsight]:
        """Generate insights from patterns"""
        insights = []
        
        # Cost insights
        cost_patterns = patterns.get('cost', {})
        if cost_patterns.get('projected_monthly', 0) > 100:
            insights.append(UsageInsight(
                type='cost_spike',
                severity='warning',
                title='High Projected Monthly Cost',
                description=f"Your projected monthly cost is ${cost_patterns['projected_monthly']:.2f}",
                recommendation='Consider implementing caching or reducing API calls to lower costs',
                data={'projected_cost': cost_patterns['projected_monthly']}
            ))
            
        # Limit warnings
        limits_status = self.azure_testing_service.get_current_limits_status()
        for service, limits in limits_status.items():
            for metric, value in limits.items():
                if '_percentage' in metric and value > 80:
                    insights.append(UsageInsight(
                        type='limit_warning',
                        severity='critical' if value > 95 else 'warning',
                        title=f'{service.replace("_", " ").title()} Approaching Limit',
                        description=f'{metric.replace("_percentage", "")} is at {value:.1f}% of limit',
                        recommendation='Reduce usage or wait for limit reset',
                        data={'service': service, 'usage_percentage': value}
                    ))
                    
        # Error insights
        error_patterns = patterns.get('errors', {})
        if error_patterns.get('error_rate', 0) > 0.1:
            insights.append(UsageInsight(
                type='pattern',
                severity='warning',
                title='High Error Rate',
                description=f"Error rate is {error_patterns['error_rate']*100:.1f}%",
                recommendation='Review error logs and fix common issues',
                data={'error_rate': error_patterns['error_rate']}
            ))
            
        # Usage pattern insights
        hourly_patterns = patterns.get('hourly', {})
        if hourly_patterns.get('peak_hours'):
            peak_hours_str = ', '.join([f"{h}:00" for h in hourly_patterns['peak_hours']])
            insights.append(UsageInsight(
                type='pattern',
                severity='info',
                title='Peak Usage Hours Identified',
                description=f"Your peak usage hours are: {peak_hours_str}",
                recommendation='Schedule batch operations during off-peak hours',
                data={'peak_hours': hourly_patterns['peak_hours']}
            ))
            
        # Service optimization
        service_patterns = patterns.get('service', {})
        for service, stats in service_patterns.items():
            if stats.get('success_rate', 1) < 0.8:
                insights.append(UsageInsight(
                    type='optimization',
                    severity='warning',
                    title=f'Low Success Rate for {service}',
                    description=f"Success rate is only {stats['success_rate']*100:.1f}%",
                    recommendation='Check service configuration and error logs',
                    data={'service': service, 'success_rate': stats['success_rate']}
                ))
                
        return insights
        
    def _generate_recommendations(self, patterns: Dict[str, Any], 
                                insights: List[UsageInsight]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Cost optimization
        cost_patterns = patterns.get('cost', {})
        if cost_patterns.get('most_expensive_operation'):
            recommendations.append({
                'category': 'Cost Optimization',
                'title': 'Optimize Most Expensive Operation',
                'description': f"The '{cost_patterns['most_expensive_operation']}' operation accounts for the highest costs",
                'actions': [
                    'Implement caching for repeated requests',
                    'Batch multiple operations together',
                    'Consider using lower-cost alternatives'
                ],
                'priority': 'high' if cost_patterns.get('projected_monthly', 0) > 50 else 'medium'
            })
            
        # Performance optimization
        service_patterns = patterns.get('service', {})
        slow_services = [
            (service, stats['avg_processing_time']) 
            for service, stats in service_patterns.items() 
            if stats.get('avg_processing_time', 0) > 5
        ]
        
        if slow_services:
            slowest = max(slow_services, key=lambda x: x[1])
            recommendations.append({
                'category': 'Performance',
                'title': f'Optimize {slowest[0]} Performance',
                'description': f'Average processing time is {slowest[1]:.1f} seconds',
                'actions': [
                    'Review data size and complexity',
                    'Consider preprocessing data',
                    'Use async operations where possible'
                ],
                'priority': 'medium'
            })
            
        # Reliability improvements
        error_patterns = patterns.get('errors', {})
        if error_patterns.get('common_errors'):
            most_common = error_patterns['common_errors'][0]
            recommendations.append({
                'category': 'Reliability',
                'title': f'Address {most_common["type"]}',
                'description': f'This error type occurred {most_common["count"]} times',
                'actions': [
                    'Implement retry logic with backoff',
                    'Add better error handling',
                    'Monitor service health before operations'
                ],
                'priority': 'high' if error_patterns.get('error_rate', 0) > 0.2 else 'medium'
            })
            
        return recommendations
        
    def get_cost_forecast(self, days: int = 30) -> Dict[str, Any]:
        """Generate cost forecast for the specified period"""
        history = self.azure_testing_service.usage_history
        
        if not history:
            return {
                'forecast': [],
                'total_projected': 0,
                'confidence': 'low'
            }
            
        # Convert to DataFrame
        df = pd.DataFrame([asdict(h) for h in history])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        # Calculate daily costs
        daily_costs = df.groupby('date')['estimated_cost'].sum()
        
        # Simple forecast using moving average
        if len(daily_costs) >= 7:
            ma_7 = daily_costs.rolling(window=7).mean().iloc[-1]
            confidence = 'high'
        elif len(daily_costs) >= 3:
            ma_7 = daily_costs.rolling(window=3).mean().iloc[-1]
            confidence = 'medium'
        else:
            ma_7 = daily_costs.mean()
            confidence = 'low'
            
        # Generate forecast
        forecast = []
        start_date = datetime.now().date()
        
        for i in range(days):
            date = start_date + timedelta(days=i)
            # Add some variation
            variation = np.random.normal(0, ma_7 * 0.1)
            daily_forecast = max(0, ma_7 + variation)
            
            forecast.append({
                'date': date.isoformat(),
                'projected_cost': daily_forecast,
                'confidence_interval': {
                    'low': max(0, daily_forecast - ma_7 * 0.2),
                    'high': daily_forecast + ma_7 * 0.2
                }
            })
            
        total_projected = sum(f['projected_cost'] for f in forecast)
        
        return {
            'forecast': forecast,
            'total_projected': total_projected,
            'daily_average': ma_7,
            'confidence': confidence,
            'based_on_days': len(daily_costs)
        }
        
    def get_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities"""
        history = self.azure_testing_service.usage_history
        opportunities = []
        
        if not history:
            return opportunities
            
        # Analyze for duplicate operations
        recent_history = [h for h in history if h.timestamp > datetime.now() - timedelta(hours=1)]
        
        # Check for repeated similar operations
        operation_counts = defaultdict(int)
        for h in recent_history:
            if h.success:
                key = f"{h.service}:{h.operation}"
                operation_counts[key] += 1
                
        for op, count in operation_counts.items():
            if count > 5:
                opportunities.append({
                    'type': 'caching',
                    'operation': op,
                    'description': f'Operation {op} was called {count} times in the last hour',
                    'potential_savings': count * 0.01,  # Rough estimate
                    'implementation': 'Implement caching layer for repeated requests'
                })
                
        # Check for batch opportunities
        df = pd.DataFrame([asdict(h) for h in history])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Group operations by 1-minute windows
        df['minute'] = df['timestamp'].dt.floor('min')
        minute_groups = df.groupby(['minute', 'service', 'operation']).size()
        
        for (minute, service, operation), count in minute_groups.items():
            if count > 3:
                opportunities.append({
                    'type': 'batching',
                    'service': service,
                    'operation': operation,
                    'description': f'{count} separate {operation} calls made within 1 minute',
                    'potential_savings': (count - 1) * 0.005,
                    'implementation': 'Batch multiple operations into single API call'
                })
                
        return opportunities

# Export function to create analytics service
def create_analytics_service(azure_testing_service):
    """Create analytics service instance"""
    return UsageAnalyticsService(azure_testing_service)