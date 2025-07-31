"""
Redis Performance Monitor for FoodXchange
Collects and tracks Redis performance metrics
"""

import redis
import time
import json
from datetime import datetime
import os

class RedisMonitor:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
    
    def collect_metrics(self):
        """Collect Redis performance metrics"""
        try:
            info = self.redis_client.info()
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'memory': {
                    'used_memory': info.get('used_memory', 0),
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'used_memory_peak': info.get('used_memory_peak_human', '0B'),
                    'memory_fragmentation_ratio': info.get('mem_fragmentation_ratio', 0)
                },
                'performance': {
                    'connected_clients': info.get('connected_clients', 0),
                    'blocked_clients': info.get('blocked_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'instantaneous_ops_per_sec': info.get('instantaneous_ops_per_sec', 0)
                },
                'persistence': {
                    'aof_enabled': info.get('aof_enabled', 0),
                    'rdb_last_save_time': info.get('rdb_last_save_time', 0),
                    'rdb_changes_since_last_save': info.get('rdb_changes_since_last_save', 0)
                },
                'cache_stats': {
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': self.calculate_hit_ratio(info)
                }
            }
            
            return metrics
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def calculate_hit_ratio(self, info):
        """Calculate cache hit ratio"""
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        
        if hits + misses == 0:
            return 0
        
        return round(hits / (hits + misses) * 100, 2)
    
    def save_metrics(self, metrics):
        """Save metrics to file"""
        metrics_file = os.path.join(self.log_dir, 'redis_metrics.json')
        with open(metrics_file, 'a') as f:
            f.write(json.dumps(metrics) + '\n')
    
    def check_health(self):
        """Redis health check with detailed info"""
        try:
            # Basic ping
            response_time_start = time.time()
            self.redis_client.ping()
            response_time = (time.time() - response_time_start) * 1000
            
            # Get metrics
            metrics = self.collect_metrics()
            
            health_status = {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'memory_usage_mb': round(metrics['memory']['used_memory'] / (1024 * 1024), 2),
                'connected_clients': metrics['performance']['connected_clients'],
                'ops_per_sec': metrics['performance']['instantaneous_ops_per_sec'],
                'cache_hit_rate': metrics['cache_stats']['hit_rate']
            }
            
            # Check for issues
            warnings = []
            if response_time > 100:
                warnings.append('High response time')
            
            if metrics['memory']['memory_fragmentation_ratio'] > 1.5:
                warnings.append('High memory fragmentation')
            
            if metrics['cache_stats']['hit_rate'] < 80:
                warnings.append(f'Low cache hit rate: {metrics["cache_stats"]["hit_rate"]}%')
            
            if warnings:
                health_status['warnings'] = warnings
            
            return health_status
            
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
    
    def generate_report(self):
        """Generate comprehensive Redis report"""
        try:
            info = self.redis_client.info()
            metrics = self.collect_metrics()
            
            report = f"""
Redis Performance Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
=====================================================

Memory Usage:
- Used Memory: {metrics['memory']['used_memory_human']}
- Peak Memory: {metrics['memory']['used_memory_peak']}
- Fragmentation Ratio: {metrics['memory']['memory_fragmentation_ratio']}

Performance:
- Connected Clients: {metrics['performance']['connected_clients']}
- Operations/sec: {metrics['performance']['instantaneous_ops_per_sec']}
- Total Commands: {metrics['performance']['total_commands_processed']:,}

Cache Performance:
- Hit Rate: {metrics['cache_stats']['hit_rate']}%
- Total Hits: {metrics['cache_stats']['keyspace_hits']:,}
- Total Misses: {metrics['cache_stats']['keyspace_misses']:,}

Database:
- Total Keys: {info.get('db0', {}).get('keys', 0)}
"""
            return report
        except Exception as e:
            return f"Error generating report: {e}"

if __name__ == "__main__":
    monitor = RedisMonitor()
    
    # Check health
    health = monitor.check_health()
    print(json.dumps(health, indent=2))
    
    # Collect and save metrics
    metrics = monitor.collect_metrics()
    monitor.save_metrics(metrics)
    
    # Generate report
    print("\n" + monitor.generate_report())