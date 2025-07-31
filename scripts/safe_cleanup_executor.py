"""
Safe Cleanup Executor for FoodXchange
Removes files identified as safe to delete from cleanup_report.json
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class SafeCleanupExecutor:
    def __init__(self, project_path=".", dry_run=False):
        self.project_path = Path(project_path)
        self.dry_run = dry_run
        self.report_path = self.project_path / "cleanup_report.json"
        self.cleanup_log = []
        self.stats = {
            'files_deleted': 0,
            'bytes_freed': 0,
            'errors': 0
        }
    
    def load_cleanup_report(self):
        """Load the cleanup report"""
        if not self.report_path.exists():
            print("❌ No cleanup report found. Run file_cleanup_analyzer.py first.")
            return None
        
        with open(self.report_path, 'r') as f:
            return json.load(f)
    
    def execute_cleanup(self):
        """Execute the cleanup based on the report"""
        print(f"🧹 FoodXchange Safe Cleanup Executor {'(DRY RUN)' if self.dry_run else ''}")
        print("=" * 50)
        
        # Load report
        report = self.load_cleanup_report()
        if not report:
            return
        
        # Process cache files
        print("\n📁 Processing cache files...")
        self.process_file_list(report['cache_files'], "cache")
        
        # Process temp files
        print("\n📁 Processing temporary files...")
        self.process_file_list(report['temp_files'], "temp")
        
        # Process old log files
        print("\n📁 Processing old log files...")
        self.process_file_list(report['log_files'], "log")
        
        # Save cleanup log
        self.save_cleanup_log()
        
        # Display results
        self.display_results()
    
    def process_file_list(self, file_list, file_type):
        """Process a list of files for deletion"""
        for file_info in file_list:
            file_path = self.project_path / file_info['path']
            
            if not file_path.exists():
                self.log_action(f"Already deleted: {file_info['path']}", "skip")
                continue
            
            try:
                if self.dry_run:
                    self.log_action(f"Would delete: {file_info['path']} ({file_info['size']} bytes)", "dry_run")
                else:
                    # Actually delete the file
                    file_path.unlink()
                    self.stats['files_deleted'] += 1
                    self.stats['bytes_freed'] += file_info['size']
                    self.log_action(f"Deleted: {file_info['path']} ({file_info['size']} bytes)", "deleted")
                    
            except Exception as e:
                self.stats['errors'] += 1
                self.log_action(f"Error deleting {file_info['path']}: {str(e)}", "error")
    
    def remove_empty_directories(self):
        """Remove empty __pycache__ directories"""
        print("\n📁 Cleaning up empty directories...")
        
        for root, dirs, files in os.walk(self.project_path, topdown=False):
            for dir_name in dirs:
                if dir_name == "__pycache__":
                    dir_path = Path(root) / dir_name
                    try:
                        if not any(dir_path.iterdir()):  # Check if directory is empty
                            if self.dry_run:
                                self.log_action(f"Would remove empty dir: {dir_path}", "dry_run")
                            else:
                                dir_path.rmdir()
                                self.log_action(f"Removed empty directory: {dir_path}", "deleted")
                    except Exception as e:
                        self.log_action(f"Error removing directory {dir_path}: {str(e)}", "error")
    
    def log_action(self, message, action_type):
        """Log cleanup actions"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cleanup_log.append({
            'timestamp': timestamp,
            'action': action_type,
            'message': message
        })
        
        # Print with appropriate emoji
        emoji = {
            'deleted': '✅',
            'dry_run': '🔍',
            'skip': '⏭️',
            'error': '❌'
        }.get(action_type, '📝')
        
        print(f"{emoji} {message}")
    
    def save_cleanup_log(self):
        """Save detailed cleanup log"""
        log_path = self.project_path / f"cleanup_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        log_data = {
            'execution_time': datetime.now().isoformat(),
            'dry_run': self.dry_run,
            'stats': self.stats,
            'actions': self.cleanup_log
        }
        
        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"\n📄 Cleanup log saved to: {log_path}")
    
    def display_results(self):
        """Display cleanup results"""
        print("\n" + "=" * 50)
        print("📊 CLEANUP RESULTS")
        print("=" * 50)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No files were actually deleted")
        
        print(f"\n✅ Files deleted: {self.stats['files_deleted']}")
        print(f"💾 Space freed: {self.stats['bytes_freed'] / (1024*1024):.2f} MB")
        print(f"❌ Errors: {self.stats['errors']}")
        
        if not self.dry_run and self.stats['files_deleted'] > 0:
            print("\n🎉 Cleanup completed successfully!")
            print("💡 Run 'git status' to see the changes")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Safe cleanup executor for FoodXchange')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--path', default='.', 
                       help='Project path (default: current directory)')
    
    args = parser.parse_args()
    
    # Confirm before actual deletion
    if not args.dry_run:
        print("⚠️  WARNING: This will permanently delete files!")
        print("📄 Review cleanup_report.json first to see what will be deleted")
        response = input("\nAre you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Cleanup cancelled")
            return
    
    executor = SafeCleanupExecutor(args.path, args.dry_run)
    executor.execute_cleanup()
    executor.remove_empty_directories()


if __name__ == "__main__":
    main()