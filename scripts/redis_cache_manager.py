"""
Redis Cache Manager for FoodXchange
Smart cache management and optimization
"""

import redis
import json
from datetime import datetime, timedelta
import os

class RedisCacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    def get_cache_statistics(self):
        """Get detailed cache statistics"""
        stats = {
            'total_keys': self.redis_client.dbsize(),
            'memory_usage': self.redis_client.info('memory')['used_memory_human'],
            'cache_patterns': {}
        }
        
        # Analyze cache patterns
        patterns = [
            'ai_analysis:*',
            'product_analysis:*',
            'ocr_result:*',
            'vision_result:*',
            'user_session:*',
            'rate_limit:*'
        ]
        
        for pattern in patterns:
            keys = self.redis_client.keys(pattern)
            stats['cache_patterns'][pattern] = len(keys)
        
        return stats
    
    def cleanup_expired_cache(self):
        """Clean up expired cache entries"""
        cleaned = 0
        patterns = ['ai_analysis:*', 'product_analysis:*', 'ocr_result:*']
        
        for pattern in patterns:
            keys = self.redis_client.keys(pattern)
            for key in keys:
                ttl = self.redis_client.ttl(key)
                
                # Set expiration if not set
                if ttl == -1:
                    self.redis_client.expire(key, 86400)  # 24 hours
                    cleaned += 1
                
                # Remove very old entries
                elif ttl == -2:  # Key doesn't exist
                    continue
        
        print(f"[CLEANUP] Cleaned up {cleaned} cache entries")
        return cleaned
    
    def optimize_memory(self):
        """Optimize Redis memory usage"""
        info = self.redis_client.info('memory')
        used_memory = info['used_memory']
        
        optimization_report = {
            'before_memory': info['used_memory_human'],
            'actions_taken': []
        }
        
        # If using more than 80% of 256MB limit
        if used_memory > 200 * 1024 * 1024:
            print("[OPTIMIZE] Optimizing Redis memory...")
            
            # Remove old rate limit keys
            rate_limit_keys = self.redis_client.keys('rate_limit:*')
            for key in rate_limit_keys:
                if self.redis_client.ttl(key) < 60:  # Less than 1 minute
                    self.redis_client.delete(key)
            optimization_report['actions_taken'].append('Cleaned old rate limit keys')
            
            # Clear old session data
            session_keys = self.redis_client.keys('user_session:*')
            for key in session_keys:
                ttl = self.redis_client.ttl(key)
                if ttl == -1:  # No expiration
                    self.redis_client.expire(key, 3600)  # 1 hour
            optimization_report['actions_taken'].append('Set expiration on session keys')
            
            # Trigger memory optimization
            self.redis_client.memory_purge()
            optimization_report['actions_taken'].append('Purged memory')
        
        # Get after stats
        info_after = self.redis_client.info('memory')
        optimization_report['after_memory'] = info_after['used_memory_human']
        optimization_report['saved_memory'] = used_memory - info_after['used_memory']
        
        return optimization_report
    
    def analyze_cache_performance(self):
        """Analyze cache performance and provide recommendations"""
        info = self.redis_client.info()
        stats = self.get_cache_statistics()
        
        # Calculate hit ratio
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        hit_ratio = hits / (hits + misses) if (hits + misses) > 0 else 0
        
        analysis = {
            'cache_hit_ratio': f"{hit_ratio * 100:.2f}%",
            'total_keys': stats['total_keys'],
            'memory_usage': stats['memory_usage'],
            'recommendations': []
        }
        
        # Generate recommendations
        if hit_ratio < 0.8:
            analysis['recommendations'].append({
                'issue': 'Low cache hit ratio',
                'recommendation': 'Consider increasing cache TTL or pre-warming cache'
            })
        
        if stats['total_keys'] > 10000:
            analysis['recommendations'].append({
                'issue': 'High number of keys',
                'recommendation': 'Review key expiration policies'
            })
        
        # Check for specific pattern issues
        if stats['cache_patterns'].get('rate_limit:*', 0) > 1000:
            analysis['recommendations'].append({
                'issue': 'Many rate limit keys',
                'recommendation': 'Consider shorter TTL for rate limit keys'
            })
        
        return analysis
    
    def export_cache_report(self):
        """Export comprehensive cache report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'statistics': self.get_cache_statistics(),
            'performance': self.analyze_cache_performance(),
            'memory_info': self.redis_client.info('memory'),
            'persistence_info': self.redis_client.info('persistence')
        }
        
        # Save report
        report_path = os.path.join('logs', f'redis_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        os.makedirs('logs', exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_path
    
    def backup_redis_data(self):
        """Create Redis backup"""
        try:
            # Trigger background save
            self.redis_client.bgsave()
            
            # Wait for save to complete
            while self.redis_client.info('persistence')['rdb_bgsave_in_progress']:
                time.sleep(1)
            
            backup_info = {
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'last_save_time': self.redis_client.info('persistence')['rdb_last_save_time']
            }
            
            return backup_info
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}

if __name__ == "__main__":
    manager = RedisCacheManager()
    
    print("Redis Cache Management Report")
    print("=" * 50)
    
    # Get statistics
    stats = manager.get_cache_statistics()
    print(f"\nTotal Keys: {stats['total_keys']}")
    print(f"Memory Usage: {stats['memory_usage']}")
    print("\nCache Patterns:")
    for pattern, count in stats['cache_patterns'].items():
        print(f"  {pattern}: {count} keys")
    
    # Cleanup
    cleaned = manager.cleanup_expired_cache()
    
    # Optimize
    optimization = manager.optimize_memory()
    if optimization['actions_taken']:
        print(f"\n[MEMORY] Optimization:")
        print(f"  Before: {optimization['before_memory']}")
        print(f"  After: {optimization['after_memory']}")
        print(f"  Actions: {', '.join(optimization['actions_taken'])}")
    
    # Performance analysis
    analysis = manager.analyze_cache_performance()
    print(f"\n[PERFORMANCE] Analysis:")
    print(f"  Hit Ratio: {analysis['cache_hit_ratio']}")
    if analysis['recommendations']:
        print("\n[RECOMMENDATIONS]:")
        for rec in analysis['recommendations']:
            print(f"  - {rec['issue']}: {rec['recommendation']}")
    
    # Export report
    report_path = manager.export_cache_report()
    print(f"\n[REPORT] Full report saved to: {report_path}")