"""
System Health Monitor for FoodXchange
Generates comprehensive system health report after cleanup
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class SystemHealthMonitor:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'system_info': {},
            'file_statistics': {},
            'code_quality': {},
            'azure_services': {},
            'recommendations': []
        }
    
    def run_health_check(self):
        """Run complete system health check"""
        print("🏥 FoodXchange System Health Check")
        print("=" * 50)
        
        self.check_system_info()
        self.analyze_file_structure()
        self.check_code_quality()
        self.verify_azure_services()
        self.generate_recommendations()
        self.save_report()
        self.display_report()
    
    def check_system_info(self):
        """Check basic system information"""
        print("\n🖥️ Checking system information...")
        
        # Python version
        self.report['system_info']['python_version'] = sys.version.split()[0]
        
        # Git status
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            modified_files = len([l for l in result.stdout.split('\n') if l.strip()])
            self.report['system_info']['git_modified_files'] = modified_files
            
            # Get current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True)
            self.report['system_info']['git_branch'] = branch_result.stdout.strip()
        except:
            self.report['system_info']['git_status'] = 'Not available'
        
        # Check for .env file
        env_path = self.project_path / '.env'
        self.report['system_info']['env_file_exists'] = env_path.exists()
        
        # Check database
        db_path = self.project_path / 'foodxchange.db'
        if db_path.exists():
            self.report['system_info']['database_size'] = db_path.stat().st_size
        else:
            self.report['system_info']['database_exists'] = False
    
    def analyze_file_structure(self):
        """Analyze project file structure"""
        print("\n📁 Analyzing file structure...")
        
        stats = {
            'total_files': 0,
            'python_files': 0,
            'javascript_files': 0,
            'html_files': 0,
            'css_files': 0,
            'json_files': 0,
            'markdown_files': 0,
            'total_size': 0,
            'directories': 0
        }
        
        file_extensions = defaultdict(int)
        
        for root, dirs, files in os.walk(self.project_path):
            # Skip certain directories
            if any(skip in root for skip in ['.git', '.venv', 'node_modules', '__pycache__']):
                continue
            
            stats['directories'] += len(dirs)
            
            for file in files:
                file_path = Path(root) / file
                try:
                    stats['total_files'] += 1
                    stats['total_size'] += file_path.stat().st_size
                    
                    ext = file_path.suffix.lower()
                    file_extensions[ext] += 1
                    
                    # Count specific file types
                    if ext == '.py':
                        stats['python_files'] += 1
                    elif ext == '.js':
                        stats['javascript_files'] += 1
                    elif ext == '.html':
                        stats['html_files'] += 1
                    elif ext == '.css':
                        stats['css_files'] += 1
                    elif ext == '.json':
                        stats['json_files'] += 1
                    elif ext == '.md':
                        stats['markdown_files'] += 1
                except:
                    pass
        
        self.report['file_statistics'] = stats
        self.report['file_statistics']['file_extensions'] = dict(file_extensions)
    
    def check_code_quality(self):
        """Check code quality indicators"""
        print("\n🔍 Checking code quality...")
        
        quality = {
            'todo_count': 0,
            'fixme_count': 0,
            'deprecated_count': 0,
            'large_files': [],
            'empty_files': []
        }
        
        # Search for TODOs, FIXMEs, etc.
        for py_file in self.project_path.rglob("*.py"):
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                quality['todo_count'] += content.upper().count('TODO')
                quality['fixme_count'] += content.upper().count('FIXME')
                quality['deprecated_count'] += content.count('@deprecated')
                
                # Check file size
                lines = len(content.splitlines())
                if lines > 500:
                    quality['large_files'].append({
                        'file': str(py_file.relative_to(self.project_path)),
                        'lines': lines
                    })
                elif lines == 0:
                    quality['empty_files'].append(str(py_file.relative_to(self.project_path)))
            except:
                pass
        
        self.report['code_quality'] = quality
    
    def verify_azure_services(self):
        """Verify Azure service configuration"""
        print("\n☁️ Verifying Azure services...")
        
        services = {
            'configured': [],
            'missing': []
        }
        
        # Check environment variables
        azure_vars = {
            'AZURE_OPENAI_API_KEY': 'Azure OpenAI',
            'AZURE_VISION_KEY': 'Azure Computer Vision',
            'AZURE_DOCUMENT_INTELLIGENCE_KEY': 'Azure Document Intelligence',
            'AZURE_TRANSLATOR_KEY': 'Azure Translator',
            'AZURE_COMMUNICATION_EMAIL_CONNECTION_STRING': 'Azure Communication Services'
        }
        
        for var, service in azure_vars.items():
            if os.getenv(var):
                services['configured'].append(service)
            else:
                services['missing'].append(service)
        
        self.report['azure_services'] = services
    
    def generate_recommendations(self):
        """Generate recommendations based on health check"""
        print("\n💡 Generating recommendations...")
        
        recommendations = []
        
        # File structure recommendations
        if self.report['file_statistics']['total_files'] > 100:
            recommendations.append({
                'type': 'optimization',
                'priority': 'medium',
                'message': 'Consider archiving old or unused files to improve project organization'
            })
        
        # Code quality recommendations
        if self.report['code_quality']['todo_count'] > 10:
            recommendations.append({
                'type': 'maintenance',
                'priority': 'low',
                'message': f"Found {self.report['code_quality']['todo_count']} TODO items - consider addressing them"
            })
        
        if self.report['code_quality']['large_files']:
            recommendations.append({
                'type': 'refactoring',
                'priority': 'medium',
                'message': f"Found {len(self.report['code_quality']['large_files'])} files with >500 lines - consider refactoring"
            })
        
        # Azure service recommendations
        if self.report['azure_services']['missing']:
            recommendations.append({
                'type': 'configuration',
                'priority': 'high',
                'message': f"Configure missing Azure services: {', '.join(self.report['azure_services']['missing'])}"
            })
        
        # Git recommendations
        if self.report['system_info'].get('git_modified_files', 0) > 20:
            recommendations.append({
                'type': 'version_control',
                'priority': 'high',
                'message': 'Many uncommitted changes detected - consider committing your work'
            })
        
        self.report['recommendations'] = recommendations
    
    def save_report(self):
        """Save health report to file"""
        report_path = self.project_path / f"system_health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        print(f"\n📄 Health report saved to: {report_path}")
    
    def display_report(self):
        """Display health report summary"""
        print("\n" + "=" * 50)
        print("📊 SYSTEM HEALTH SUMMARY")
        print("=" * 50)
        
        # System info
        print("\n🖥️ System Information:")
        print(f"  • Python version: {self.report['system_info']['python_version']}")
        print(f"  • Git branch: {self.report['system_info'].get('git_branch', 'Unknown')}")
        print(f"  • Modified files: {self.report['system_info'].get('git_modified_files', 0)}")
        print(f"  • Environment configured: {'✅' if self.report['system_info']['env_file_exists'] else '❌'}")
        
        # File statistics
        stats = self.report['file_statistics']
        print(f"\n📁 File Statistics:")
        print(f"  • Total files: {stats['total_files']}")
        print(f"  • Total size: {stats['total_size'] / (1024*1024):.1f} MB")
        print(f"  • Python files: {stats['python_files']}")
        print(f"  • JavaScript files: {stats['javascript_files']}")
        print(f"  • HTML templates: {stats['html_files']}")
        
        # Code quality
        quality = self.report['code_quality']
        print(f"\n🔍 Code Quality:")
        print(f"  • TODO items: {quality['todo_count']}")
        print(f"  • FIXME items: {quality['fixme_count']}")
        print(f"  • Large files (>500 lines): {len(quality['large_files'])}")
        print(f"  • Empty files: {len(quality['empty_files'])}")
        
        # Azure services
        services = self.report['azure_services']
        print(f"\n☁️ Azure Services:")
        print(f"  • Configured: {len(services['configured'])}")
        print(f"  • Missing: {len(services['missing'])}")
        if services['configured']:
            for service in services['configured'][:3]:  # Show first 3
                print(f"    ✅ {service}")
        
        # Recommendations
        if self.report['recommendations']:
            print(f"\n💡 Top Recommendations:")
            high_priority = [r for r in self.report['recommendations'] if r['priority'] == 'high']
            for rec in high_priority[:3]:  # Show top 3 high priority
                print(f"  • {rec['message']}")
        
        print("\n✅ System health check completed!")


if __name__ == "__main__":
    monitor = SystemHealthMonitor()
    monitor.run_health_check()