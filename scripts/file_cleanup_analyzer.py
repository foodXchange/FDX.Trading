"""
File Cleanup Analyzer for FoodXchange
Identifies safe-to-delete files and generates cleanup report
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class FileCleanupAnalyzer:
    def __init__(self, project_path="."):
        self.project_path = Path(project_path)
        self.cleanup_report = {
            'safe_to_delete': [],
            'duplicate_files': [],
            'large_files': [],
            'old_files': [],
            'cache_files': [],
            'temp_files': [],
            'log_files': [],
            'summary': {}
        }
    
    def analyze_filesystem(self):
        """Run complete filesystem analysis"""
        print("🧹 FoodXchange Filesystem Cleanup Analysis")
        print("=" * 50)
        
        self.find_cache_files()
        self.find_temp_files()
        self.find_log_files()
        self.find_duplicates()
        self.find_large_files()
        self.find_old_files()
        self.calculate_summary()
        self.save_report()
        self.display_summary()
    
    def find_cache_files(self):
        """Find Python cache and compiled files"""
        cache_patterns = [
            "**/__pycache__/**/*.pyc",
            "**/__pycache__/**/*.pyo",
            "**/*.pyc",
            "**/*.pyo",
            "**/.pytest_cache/**/*",
            "**/.mypy_cache/**/*",
            "**/node_modules/**/*",
            "**/.coverage",
            "**/coverage.xml",
            "**/htmlcov/**/*"
        ]
        
        for pattern in cache_patterns:
            for file_path in self.project_path.glob(pattern):
                if file_path.is_file() and '.venv' not in str(file_path):
                    size = file_path.stat().st_size
                    self.cleanup_report['cache_files'].append({
                        'path': str(file_path.relative_to(self.project_path)),
                        'size': size,
                        'type': 'cache'
                    })
    
    def find_temp_files(self):
        """Find temporary files"""
        temp_patterns = [
            "**/*.tmp",
            "**/*.temp",
            "**/*.bak",
            "**/*.swp",
            "**/*~",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/desktop.ini"
        ]
        
        for pattern in temp_patterns:
            for file_path in self.project_path.glob(pattern):
                if file_path.is_file():
                    size = file_path.stat().st_size
                    self.cleanup_report['temp_files'].append({
                        'path': str(file_path.relative_to(self.project_path)),
                        'size': size,
                        'type': 'temp'
                    })
    
    def find_log_files(self):
        """Find old log files"""
        cutoff_date = datetime.now() - timedelta(days=7)  # Logs older than 7 days
        
        for file_path in self.project_path.rglob("*.log"):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    size = file_path.stat().st_size
                    self.cleanup_report['log_files'].append({
                        'path': str(file_path.relative_to(self.project_path)),
                        'size': size,
                        'age_days': (datetime.now() - mtime).days,
                        'type': 'old_log'
                    })
    
    def find_duplicates(self):
        """Find duplicate files"""
        file_hashes = defaultdict(list)
        
        # Check common file types for duplicates
        patterns = ['**/*.py', '**/*.js', '**/*.css', '**/*.html', '**/*.json', '**/*.md']
        
        for pattern in patterns:
            for file_path in self.project_path.glob(pattern):
                if file_path.is_file() and '.venv' not in str(file_path):
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        
                        file_hashes[file_hash].append({
                            'path': str(file_path.relative_to(self.project_path)),
                            'size': file_path.stat().st_size
                        })
                    except Exception:
                        continue
        
        # Find duplicates
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                self.cleanup_report['duplicate_files'].append({
                    'files': files,
                    'hash': file_hash,
                    'count': len(files),
                    'total_size': sum(f['size'] for f in files)
                })
    
    def find_large_files(self):
        """Find unusually large files"""
        large_threshold = 10 * 1024 * 1024  # 10MB
        
        exclude_dirs = {'.venv', '.git', 'node_modules', '__pycache__'}
        
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                # Skip if in excluded directory
                if any(excluded in str(file_path) for excluded in exclude_dirs):
                    continue
                
                size = file_path.stat().st_size
                if size > large_threshold:
                    self.cleanup_report['large_files'].append({
                        'path': str(file_path.relative_to(self.project_path)),
                        'size': size,
                        'size_mb': round(size / (1024*1024), 2)
                    })
    
    def find_old_files(self):
        """Find old, potentially unused files"""
        cutoff_date = datetime.now() - timedelta(days=90)  # 3 months
        
        extensions = ['.py', '.js', '.css', '.html']
        exclude_dirs = {'.venv', '.git', 'migrations', 'static'}
        
        for ext in extensions:
            for file_path in self.project_path.rglob(f"*{ext}"):
                # Skip if in excluded directory
                if any(excluded in str(file_path) for excluded in exclude_dirs):
                    continue
                
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mtime < cutoff_date:
                    self.cleanup_report['old_files'].append({
                        'path': str(file_path.relative_to(self.project_path)),
                        'last_modified': mtime.strftime('%Y-%m-%d'),
                        'age_days': (datetime.now() - mtime).days,
                        'size': file_path.stat().st_size
                    })
    
    def calculate_summary(self):
        """Calculate summary statistics"""
        total_cache = sum(f['size'] for f in self.cleanup_report['cache_files'])
        total_temp = sum(f['size'] for f in self.cleanup_report['temp_files'])
        total_logs = sum(f['size'] for f in self.cleanup_report['log_files'])
        
        duplicate_waste = sum(
            dup['total_size'] - min(f['size'] for f in dup['files'])
            for dup in self.cleanup_report['duplicate_files']
        )
        
        self.cleanup_report['summary'] = {
            'total_cache_size': total_cache,
            'total_temp_size': total_temp,
            'total_log_size': total_logs,
            'duplicate_waste': duplicate_waste,
            'total_safe_to_delete': total_cache + total_temp + total_logs,
            'cache_files_count': len(self.cleanup_report['cache_files']),
            'temp_files_count': len(self.cleanup_report['temp_files']),
            'log_files_count': len(self.cleanup_report['log_files']),
            'duplicate_groups': len(self.cleanup_report['duplicate_files']),
            'large_files_count': len(self.cleanup_report['large_files']),
            'old_files_count': len(self.cleanup_report['old_files'])
        }
    
    def save_report(self):
        """Save detailed report to JSON"""
        report_path = self.project_path / 'cleanup_report.json'
        with open(report_path, 'w') as f:
            json.dump(self.cleanup_report, f, indent=2, default=str)
        print(f"\n📄 Detailed report saved to: {report_path}")
    
    def display_summary(self):
        """Display cleanup summary"""
        summary = self.cleanup_report['summary']
        
        print("\n📊 CLEANUP SUMMARY")
        print("=" * 50)
        
        # Safe to delete
        safe_size_mb = summary['total_safe_to_delete'] / (1024*1024)
        print(f"\n✅ Safe to Delete:")
        print(f"  • Cache files: {summary['cache_files_count']} files ({summary['total_cache_size']/(1024*1024):.1f} MB)")
        print(f"  • Temp files: {summary['temp_files_count']} files ({summary['total_temp_size']/(1024*1024):.1f} MB)")
        print(f"  • Old logs: {summary['log_files_count']} files ({summary['total_log_size']/(1024*1024):.1f} MB)")
        print(f"  • Total: {safe_size_mb:.1f} MB can be safely deleted")
        
        # Duplicates
        if summary['duplicate_groups'] > 0:
            print(f"\n🔄 Duplicates Found:")
            print(f"  • {summary['duplicate_groups']} groups of duplicate files")
            print(f"  • {summary['duplicate_waste']/(1024*1024):.1f} MB could be saved")
        
        # Large files
        if summary['large_files_count'] > 0:
            print(f"\n📦 Large Files:")
            print(f"  • {summary['large_files_count']} files over 10MB")
            for lf in self.cleanup_report['large_files'][:5]:  # Show top 5
                print(f"    - {lf['path']} ({lf['size_mb']} MB)")
        
        # Old files
        if summary['old_files_count'] > 0:
            print(f"\n📅 Old Files (>90 days):")
            print(f"  • {summary['old_files_count']} files haven't been modified in 3+ months")
        
        print("\n💡 Next Steps:")
        print("  1. Review cleanup_report.json for detailed file list")
        print("  2. Run safe_cleanup.py to remove safe files")
        print("  3. Manually review duplicates and large files")


if __name__ == "__main__":
    analyzer = FileCleanupAnalyzer()
    analyzer.analyze_filesystem()