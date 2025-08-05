#!/usr/bin/env python3
"""
FDX VM Control Panel - Robust GUI for Linux/Ubuntu Operations
Author: FDX Trading
Version: 2.0
"""

import os
import subprocess
import json
import psutil
import platform
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_file
import threading
import time
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdx-vm-control-2024'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VMController:
    def __init__(self):
        self.system_info = self.get_system_info()
        self.services = {
            'foodxchange': {
                'name': 'FoodXchange App',
                'port': 80,
                'process': 'uvicorn',
                'path': '/home/fdxfounder/fdx/app',
                'url': 'http://4.206.1.15'
            },
            'fdx_crawler': {
                'name': 'FDX Crawler',
                'port': 8003,
                'process': 'uvicorn',
                'path': '/home/fdxfounder/fdx/crawler',
                'url': 'http://4.206.1.15:8003'
            },
            'postgresql': {
                'name': 'PostgreSQL Database',
                'port': 5432,
                'process': 'postgres',
                'service': 'postgresql'
            },
            'nginx': {
                'name': 'Nginx Web Server',
                'port': 80,
                'process': 'nginx',
                'service': 'nginx'
            }
        }
    
    def get_system_info(self):
        """Get comprehensive system information"""
        try:
            info = {
                'hostname': platform.node(),
                'platform': platform.platform(),
                'processor': platform.processor(),
                'architecture': platform.machine(),
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_total': psutil.disk_usage('/').total,
                'python_version': platform.python_version(),
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            }
            return info
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {}
    
    def execute_command(self, command, shell=True):
        """Execute system command safely"""
        try:
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': command
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_service_status(self, service_name):
        """Check if a service is running"""
        try:
            result = self.execute_command(f"systemctl is-active {service_name}")
            return result['stdout'].strip() == 'active'
        except:
            return False
    
    def manage_service(self, service_name, action):
        """Start, stop, or restart a service"""
        valid_actions = ['start', 'stop', 'restart', 'status']
        if action not in valid_actions:
            return {'success': False, 'error': 'Invalid action'}
        
        command = f"sudo systemctl {action} {service_name}"
        return self.execute_command(command)
    
    def get_system_metrics(self):
        """Get real-time system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq().current if psutil.cpu_freq() else 0
                },
                'memory': {
                    'total': memory.total,
                    'used': memory.used,
                    'percent': memory.percent,
                    'available': memory.available
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {}
    
    def get_process_list(self):
        """Get list of running processes"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    pinfo = proc.info
                    if pinfo['cpu_percent'] > 0 or pinfo['memory_percent'] > 0:
                        processes.append(pinfo)
                except:
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            return processes[:20]  # Top 20 processes
        except Exception as e:
            logger.error(f"Error getting process list: {e}")
            return []
    
    def check_port(self, port):
        """Check if a port is open"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == 'LISTEN':
                    return True
            return False
        except:
            return False
    
    def get_logs(self, service, lines=100):
        """Get service logs"""
        log_commands = {
            'foodxchange': f"journalctl -u foodxchange -n {lines} --no-pager",
            'fdx_crawler': f"journalctl -u fdx-crawler -n {lines} --no-pager",
            'nginx': f"sudo tail -n {lines} /var/log/nginx/error.log",
            'system': f"sudo journalctl -n {lines} --no-pager"
        }
        
        command = log_commands.get(service, f"sudo journalctl -n {lines} --no-pager")
        result = self.execute_command(command)
        return result['stdout'] if result['success'] else result.get('error', 'Failed to get logs')
    
    def backup_database(self):
        """Create database backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/home/fdxfounder/backups/fdx_backup_{timestamp}.sql"
        
        commands = [
            f"mkdir -p /home/fdxfounder/backups",
            f"pg_dump -U fdxfounder -d foodxchange > {backup_file}",
            f"gzip {backup_file}"
        ]
        
        for cmd in commands:
            result = self.execute_command(cmd)
            if not result['success']:
                return result
        
        return {
            'success': True,
            'backup_file': f"{backup_file}.gz",
            'size': os.path.getsize(f"{backup_file}.gz") if os.path.exists(f"{backup_file}.gz") else 0
        }
    
    def update_system(self):
        """Update system packages"""
        commands = [
            "sudo apt update",
            "sudo apt upgrade -y",
            "sudo apt autoremove -y",
            "sudo apt autoclean"
        ]
        
        results = []
        for cmd in commands:
            result = self.execute_command(cmd)
            results.append({
                'command': cmd,
                'success': result['success'],
                'output': result.get('stdout', '')[:500]  # Limit output
            })
        
        return results

# Initialize controller
vm = VMController()

# Flask Routes
@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html', system_info=vm.system_info)

@app.route('/api/metrics')
def get_metrics():
    """Get system metrics"""
    return jsonify(vm.get_system_metrics())

@app.route('/api/services')
def get_services():
    """Get service statuses"""
    statuses = {}
    for service_id, service_info in vm.services.items():
        if 'port' in service_info:
            statuses[service_id] = {
                'name': service_info['name'],
                'running': vm.check_port(service_info['port']),
                'port': service_info['port'],
                'url': service_info.get('url', '')
            }
    return jsonify(statuses)

@app.route('/api/service/<service_name>/<action>')
def manage_service(service_name, action):
    """Manage a service"""
    result = vm.manage_service(service_name, action)
    return jsonify(result)

@app.route('/api/processes')
def get_processes():
    """Get process list"""
    return jsonify(vm.get_process_list())

@app.route('/api/logs/<service>')
def get_logs(service):
    """Get service logs"""
    lines = request.args.get('lines', 100, type=int)
    logs = vm.get_logs(service, lines)
    return jsonify({'logs': logs})

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute a command (with restrictions)"""
    data = request.get_json()
    command = data.get('command', '')
    
    # Security: Whitelist safe commands
    safe_commands = [
        'ls', 'pwd', 'whoami', 'date', 'uptime', 'df', 'free',
        'ps', 'top', 'htop', 'netstat', 'ss', 'ip', 'ifconfig'
    ]
    
    cmd_parts = command.split()
    if not cmd_parts or cmd_parts[0] not in safe_commands:
        return jsonify({'success': False, 'error': 'Command not allowed'}), 403
    
    result = vm.execute_command(command)
    return jsonify(result)

@app.route('/api/backup', methods=['POST'])
def backup_database():
    """Create database backup"""
    result = vm.backup_database()
    return jsonify(result)

@app.route('/api/update', methods=['POST'])
def update_system():
    """Update system packages"""
    results = vm.update_system()
    return jsonify({'results': results})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Background monitoring
def monitor_system():
    """Background system monitoring"""
    while True:
        try:
            metrics = vm.get_system_metrics()
            # Could send alerts here if thresholds exceeded
            if metrics.get('cpu', {}).get('percent', 0) > 90:
                logger.warning(f"High CPU usage: {metrics['cpu']['percent']}%")
            if metrics.get('memory', {}).get('percent', 0) > 90:
                logger.warning(f"High memory usage: {metrics['memory']['percent']}%")
            if metrics.get('disk', {}).get('percent', 0) > 90:
                logger.warning(f"High disk usage: {metrics['disk']['percent']}%")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    # Start monitoring thread
    monitor_thread = threading.Thread(target=monitor_system, daemon=True)
    monitor_thread.start()
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5555, debug=False)