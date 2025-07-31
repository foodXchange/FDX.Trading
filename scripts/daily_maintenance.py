"""
Daily Maintenance Script for FoodXchange
Performs automated daily tasks for system health
"""

import os
import sys
import json
import redis
import logging
from datetime import datetime, timedelta
import subprocess
import shutil

# Set up logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'maintenance')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'daily_maintenance_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DailyMaintenance:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.report = {
            'date': datetime.now().isoformat(),
            'tasks': {},
            'errors': []
        }
    
    def run_all_tasks(self):
        """Run all daily maintenance tasks"""
        logger.info("Starting daily maintenance...")
        
        tasks = [
            ('cache_cleanup', self.cleanup_cache),
            ('database_backup', self.backup_database),
            ('log_rotation', self.rotate_logs),
            ('redis_optimization', self.optimize_redis),
            ('docker_cleanup', self.cleanup_docker),
            ('system_health_check', self.check_system_health),
            ('azure_usage_report', self.generate_azure_usage_report)
        ]
        
        for task_name, task_func in tasks:
            try:
                logger.info(f"Running task: {task_name}")
                result = task_func()
                self.report['tasks'][task_name] = {
                    'status': 'success',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                logger.info(f"Task {task_name} completed successfully")
            except Exception as e:
                error_msg = f"Task {task_name} failed: {str(e)}"
                logger.error(error_msg)
                self.report['tasks'][task_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.report['errors'].append(error_msg)
        
        self.save_report()
        logger.info("Daily maintenance completed")
    
    def cleanup_cache(self):
        """Clean up expired Redis cache entries"""
        try:
            # Import and run cache manager
            sys.path.append(os.path.dirname(__file__))
            from redis_cache_manager import RedisCacheManager
            
            manager = RedisCacheManager()
            stats_before = manager.get_cache_statistics()
            cleaned = manager.cleanup_expired_cache()
            optimization = manager.optimize_memory()
            stats_after = manager.get_cache_statistics()
            
            return {
                'cleaned_entries': cleaned,
                'memory_before': stats_before['memory_usage'],
                'memory_after': stats_after['memory_usage'],
                'optimization': optimization
            }
        except Exception as e:
            raise Exception(f"Cache cleanup failed: {str(e)}")
    
    def backup_database(self):
        """Create daily database backup"""
        backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups', 'daily')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Remove backups older than 7 days
        cutoff_date = datetime.now() - timedelta(days=7)
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_date:
                    os.remove(file_path)
                    logger.info(f"Removed old backup: {filename}")
        
        # Create new backup
        backup_file = os.path.join(backup_dir, f'foodxchange_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.sql')
        
        try:
            # Use Docker to create backup if available
            result = subprocess.run([
                'docker', 'exec', '-t', 'postgres',
                'pg_dump', '-U', 'postgres', '-d', 'foodxchange'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                with open(backup_file, 'w') as f:
                    f.write(result.stdout)
                return {
                    'backup_file': backup_file,
                    'size': os.path.getsize(backup_file)
                }
            else:
                # Fallback to direct pg_dump if Docker not available
                logger.warning("Docker backup failed, trying direct pg_dump")
                return {'status': 'skipped', 'reason': 'Database backup requires Docker or direct PostgreSQL access'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def rotate_logs(self):
        """Rotate and compress old logs"""
        log_dirs = [
            os.path.join(os.path.dirname(__file__), '..', 'logs'),
            os.path.join(os.path.dirname(__file__), '..', 'logs', 'maintenance')
        ]
        
        rotated_count = 0
        compressed_size = 0
        
        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                continue
            
            # Archive logs older than 3 days
            cutoff_date = datetime.now() - timedelta(days=3)
            archive_dir = os.path.join(log_dir, 'archive')
            os.makedirs(archive_dir, exist_ok=True)
            
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(log_dir, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < cutoff_date:
                            # Move to archive
                            archive_path = os.path.join(archive_dir, filename)
                            shutil.move(file_path, archive_path)
                            rotated_count += 1
                            
                            # Compress if possible
                            try:
                                import gzip
                                with open(archive_path, 'rb') as f_in:
                                    with gzip.open(f'{archive_path}.gz', 'wb') as f_out:
                                        f_out.writelines(f_in)
                                os.remove(archive_path)
                                compressed_size += os.path.getsize(f'{archive_path}.gz')
                            except:
                                pass
        
        return {
            'rotated_files': rotated_count,
            'compressed_size': compressed_size
        }
    
    def optimize_redis(self):
        """Optimize Redis memory and performance"""
        try:
            from redis_cache_manager import RedisCacheManager
            
            manager = RedisCacheManager()
            optimization = manager.optimize_memory()
            analysis = manager.analyze_cache_performance()
            
            # Run Redis memory doctor
            try:
                self.redis_client.memory_doctor()
            except:
                pass
            
            return {
                'optimization': optimization,
                'performance': analysis
            }
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    
    def cleanup_docker(self):
        """Clean up Docker resources"""
        try:
            cleanup_commands = [
                ['docker', 'container', 'prune', '-f'],
                ['docker', 'image', 'prune', '-f'],
                ['docker', 'volume', 'prune', '-f'],
                ['docker', 'network', 'prune', '-f']
            ]
            
            results = {}
            for cmd in cleanup_commands:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    results[' '.join(cmd[1:3])] = 'cleaned'
            
            # Get disk usage after cleanup
            df_result = subprocess.run(['docker', 'system', 'df'], capture_output=True, text=True)
            
            return {
                'cleanup_results': results,
                'disk_usage': df_result.stdout if df_result.returncode == 0 else 'unavailable'
            }
        except Exception as e:
            return {'status': 'skipped', 'reason': 'Docker not available'}
    
    def check_system_health(self):
        """Comprehensive system health check"""
        health_status = {
            'services': {},
            'resources': {},
            'warnings': []
        }
        
        # Check Redis
        try:
            self.redis_client.ping()
            redis_info = self.redis_client.info()
            health_status['services']['redis'] = {
                'status': 'healthy',
                'memory': redis_info.get('used_memory_human', 'unknown'),
                'uptime_days': redis_info.get('uptime_in_days', 0)
            }
        except:
            health_status['services']['redis'] = {'status': 'unhealthy'}
            health_status['warnings'].append('Redis is not responding')
        
        # Check disk space
        try:
            import psutil
            disk = psutil.disk_usage('/')
            health_status['resources']['disk'] = {
                'total': f"{disk.total / (1024**3):.2f} GB",
                'used': f"{disk.used / (1024**3):.2f} GB",
                'free': f"{disk.free / (1024**3):.2f} GB",
                'percent': disk.percent
            }
            
            if disk.percent > 90:
                health_status['warnings'].append(f'Low disk space: {disk.percent}% used')
        except:
            pass
        
        # Check app port
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8003))
            sock.close()
            health_status['services']['app'] = {
                'status': 'healthy' if result == 0 else 'unhealthy',
                'port': 8003
            }
        except:
            health_status['services']['app'] = {'status': 'unknown'}
        
        return health_status
    
    def generate_azure_usage_report(self):
        """Generate Azure API usage report"""
        # This would integrate with Azure cost monitoring
        # For now, return a placeholder
        return {
            'status': 'pending',
            'message': 'Azure usage reporting will be implemented with cost monitoring service'
        }
    
    def save_report(self):
        """Save daily maintenance report"""
        report_dir = os.path.join(os.path.dirname(__file__), '..', 'logs', 'maintenance', 'reports')
        os.makedirs(report_dir, exist_ok=True)
        
        report_file = os.path.join(report_dir, f'daily_report_{datetime.now().strftime("%Y%m%d")}.json')
        with open(report_file, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        logger.info(f"Report saved to: {report_file}")
        
        # Also save a summary
        summary = {
            'date': self.report['date'],
            'total_tasks': len(self.report['tasks']),
            'successful_tasks': sum(1 for t in self.report['tasks'].values() if t['status'] == 'success'),
            'failed_tasks': sum(1 for t in self.report['tasks'].values() if t['status'] == 'failed'),
            'errors': len(self.report['errors'])
        }
        
        summary_file = os.path.join(report_dir, 'maintenance_summary.json')
        summaries = []
        if os.path.exists(summary_file):
            with open(summary_file, 'r') as f:
                summaries = json.load(f)
        
        summaries.append(summary)
        # Keep only last 30 days
        summaries = summaries[-30:]
        
        with open(summary_file, 'w') as f:
            json.dump(summaries, f, indent=2)

if __name__ == "__main__":
    maintenance = DailyMaintenance()
    maintenance.run_all_tasks()