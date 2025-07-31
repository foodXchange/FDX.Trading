"""
Optimized Redis client for FoodXchange Python integration
Enhanced version with better serialization, connection pooling, and performance monitoring
"""

import redis
import json
import pickle
import hashlib
import os
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OptimizedRedisClient:
    """Redis client optimized for FoodXchange Python application"""
    
    def __init__(self):
        # Connection pool optimized for Python app
        self.pool = redis.ConnectionPool(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=False,  # We'll handle encoding/decoding
            max_connections=50,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        self.client = redis.Redis(connection_pool=self.pool)
        
        # Cache prefixes for different data types
        self.prefixes = {
            'analysis': 'fx:analysis:',
            'product': 'fx:product:',
            'session': 'fx:session:',
            'rate_limit': 'fx:rate:',
            'temp': 'fx:temp:'
        }
    
    def _serialize_data(self, data: Any) -> bytes:
        """Optimized serialization for Python objects"""
        if isinstance(data, (dict, list)):
            # Use JSON for simple structures (faster)
            return json.dumps(data, default=str).encode('utf-8')
        else:
            # Use pickle for complex Python objects
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Optimized deserialization"""
        try:
            # Try JSON first (faster)
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Fall back to pickle
            return pickle.loads(data)
    
    def cache_analysis_result(self, image_hash: str, analysis_data: dict, ttl: int = 3600):
        """Cache AI analysis result with optimized storage"""
        key = f"{self.prefixes['analysis']}{image_hash}"
        
        # Add metadata
        cache_data = {
            'data': analysis_data,
            'cached_at': datetime.now().isoformat(),
            'ttl': ttl
        }
        
        serialized = self._serialize_data(cache_data)
        self.client.setex(key, ttl, serialized)
        
        # Track cache statistics
        self.client.incr('fx:stats:cache_writes')
    
    def get_cached_analysis(self, image_hash: str) -> Optional[dict]:
        """Get cached analysis with hit/miss tracking"""
        key = f"{self.prefixes['analysis']}{image_hash}"
        
        cached = self.client.get(key)
        if cached:
            self.client.incr('fx:stats:cache_hits')
            result = self._deserialize_data(cached)
            return result.get('data') if isinstance(result, dict) else result
        else:
            self.client.incr('fx:stats:cache_misses')
            return None
    
    def cache_product_info(self, product_id: str, product_data: dict, ttl: int = 86400):
        """Cache product information for 24 hours"""
        key = f"{self.prefixes['product']}{product_id}"
        self.client.setex(key, ttl, self._serialize_data(product_data))
    
    def rate_limit_check(self, user_id: str, limit: int = 100, window: int = 3600) -> bool:
        """Rate limiting with sliding window"""
        key = f"{self.prefixes['rate_limit']}{user_id}"
        current = datetime.now().timestamp()
        
        # Use sorted set for sliding window
        pipe = self.client.pipeline()
        pipe.zremrangebyscore(key, 0, current - window)  # Remove old entries
        pipe.zcard(key)  # Count current requests
        pipe.zadd(key, {str(current): current})  # Add current request
        pipe.expire(key, window)  # Set expiration
        
        results = pipe.execute()
        request_count = results[1]
        
        return request_count < limit
    
    def store_temp_data(self, temp_id: str, data: Any, ttl: int = 1800):
        """Store temporary data (30 minutes default)"""
        key = f"{self.prefixes['temp']}{temp_id}"
        self.client.setex(key, ttl, self._serialize_data(data))
    
    def get_cache_stats(self) -> dict:
        """Get cache performance statistics"""
        try:
            stats = self.client.info('stats')
            custom_stats = {}
            
            # Get custom statistics
            for stat in ['cache_hits', 'cache_misses', 'cache_writes']:
                custom_stats[stat] = int(self.client.get(f'fx:stats:{stat}') or 0)
            
            hit_rate = 0
            if custom_stats['cache_hits'] + custom_stats['cache_misses'] > 0:
                hit_rate = custom_stats['cache_hits'] / (custom_stats['cache_hits'] + custom_stats['cache_misses'])
            
            return {
                'redis_stats': {
                    'connected_clients': stats['connected_clients'],
                    'used_memory_human': stats['used_memory_human'],
                    'keyspace_hits': stats['keyspace_hits'],
                    'keyspace_misses': stats['keyspace_misses']
                },
                'foodxchange_stats': custom_stats,
                'cache_hit_rate': f"{hit_rate:.2%}",
                'memory_efficiency': stats['used_memory'] / (1024 * 1024)  # MB
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}
    
    def health_check(self) -> dict:
        """Redis health check for Python application"""
        try:
            start_time = datetime.now()
            
            # Test basic operations
            test_key = 'fx:health_check'
            self.client.set(test_key, 'test', ex=60)
            value = self.client.get(test_key)
            self.client.delete(test_key)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'connection_pool_created_connections': self.pool.created_connections,
                'connection_pool_available_connections': len(self.pool._available_connections),
                'redis_version': self.client.info()['redis_version']
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }

# Global instance
redis_client = OptimizedRedisClient()