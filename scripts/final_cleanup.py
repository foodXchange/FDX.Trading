"""
Final Cleanup Script for FoodXchange
Organizes files and prepares for commit
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class FinalCleanup:
    def __init__(self):
        self.project_path = Path.cwd()
        self.actions_taken = []
    
    def run_cleanup(self):
        """Execute final cleanup tasks"""
        print("🧹 FoodXchange Final Cleanup")
        print("=" * 50)
        
        # 1. Move test files to archive
        self.archive_test_files()
        
        # 2. Move documentation to archive
        self.archive_documentation()
        
        # 3. Clean up script files
        self.cleanup_scripts()
        
        # 4. Remove temporary files
        self.remove_temp_files()
        
        # 5. Update .gitignore
        self.update_gitignore()
        
        # 6. Display summary
        self.display_summary()
    
    def archive_test_files(self):
        """Archive test files"""
        print("\n📦 Archiving test files...")
        
        test_patterns = [
            '*_test.py',
            'test_*.py',
            'check_*.py',
            'validate_*.py'
        ]
        
        archive_dir = self.project_path / 'archive' / 'test_scripts'
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        moved = 0
        for pattern in test_patterns:
            for file in self.project_path.glob(pattern):
                if file.is_file() and 'archive' not in str(file):
                    try:
                        shutil.move(str(file), str(archive_dir / file.name))
                        self.actions_taken.append(f"Archived: {file.name}")
                        moved += 1
                    except Exception as e:
                        print(f"  Error moving {file}: {e}")
        
        print(f"  ✅ Archived {moved} test files")
    
    def archive_documentation(self):
        """Archive temporary documentation"""
        print("\n📚 Archiving documentation...")
        
        doc_patterns = [
            '*_REPORT.md',
            '*_GUIDE.md',
            '*_SUMMARY.md',
            'AI_*.md',
            'AZURE_*.md'
        ]
        
        archive_dir = self.project_path / 'archive' / 'documentation'
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Keep essential docs
        keep_docs = ['README.md', 'LICENSE', 'SECURITY_DEPLOYMENT_CHECKLIST.md']
        
        moved = 0
        for pattern in doc_patterns:
            for file in self.project_path.glob(pattern):
                if file.is_file() and file.name not in keep_docs:
                    try:
                        shutil.move(str(file), str(archive_dir / file.name))
                        self.actions_taken.append(f"Archived: {file.name}")
                        moved += 1
                    except Exception as e:
                        print(f"  Error moving {file}: {e}")
        
        print(f"  ✅ Archived {moved} documentation files")
    
    def cleanup_scripts(self):
        """Clean up unnecessary scripts"""
        print("\n🔧 Cleaning up scripts...")
        
        script_patterns = [
            'setup_env.*',
            'run_all_tests.*',
            'create_*_deployment.sh',
            'azure_setup_*.py',
            'complete_*.py',
            'analyze_*.py'
        ]
        
        archive_dir = self.project_path / 'archive' / 'setup_scripts'
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        moved = 0
        for pattern in script_patterns:
            for file in self.project_path.glob(pattern):
                if file.is_file():
                    try:
                        shutil.move(str(file), str(archive_dir / file.name))
                        self.actions_taken.append(f"Archived: {file.name}")
                        moved += 1
                    except Exception as e:
                        print(f"  Error moving {file}: {e}")
        
        print(f"  ✅ Archived {moved} setup scripts")
    
    def remove_temp_files(self):
        """Remove temporary files"""
        print("\n🗑️ Removing temporary files...")
        
        temp_patterns = [
            'cleanup_*.json',
            'system_health_*.json',
            'cleanup_*.bat',
            'gitignore_additions.txt',
            'todo_report.txt'
        ]
        
        removed = 0
        for pattern in temp_patterns:
            for file in self.project_path.glob(pattern):
                if file.is_file():
                    try:
                        file.unlink()
                        self.actions_taken.append(f"Removed: {file.name}")
                        removed += 1
                    except Exception as e:
                        print(f"  Error removing {file}: {e}")
        
        print(f"  ✅ Removed {removed} temporary files")
    
    def update_gitignore(self):
        """Ensure .gitignore is up to date"""
        print("\n📝 Updating .gitignore...")
        
        gitignore_additions = [
            "\n# Archive folders",
            "archive/",
            "backup_*/",
            "",
            "# Temporary analysis files",
            "cleanup_*.json",
            "system_health_*.json",
            "todo_report.txt",
            "",
            "# Test scripts",
            "test_*.py",
            "*_test.py"
        ]
        
        gitignore_path = self.project_path / '.gitignore'
        
        try:
            with open(gitignore_path, 'r') as f:
                content = f.read()
            
            # Check if archive/ is already in gitignore
            if 'archive/' not in content:
                with open(gitignore_path, 'a') as f:
                    f.write('\n'.join(gitignore_additions))
                print("  ✅ Updated .gitignore")
            else:
                print("  ✅ .gitignore already up to date")
        except Exception as e:
            print(f"  Error updating .gitignore: {e}")
    
    def display_summary(self):
        """Display cleanup summary"""
        print("\n" + "=" * 50)
        print("📊 CLEANUP SUMMARY")
        print("=" * 50)
        
        print(f"\nTotal actions taken: {len(self.actions_taken)}")
        
        # Group actions by type
        archived = [a for a in self.actions_taken if 'Archived' in a]
        removed = [a for a in self.actions_taken if 'Removed' in a]
        
        print(f"\n📦 Files archived: {len(archived)}")
        print(f"🗑️ Files removed: {len(removed)}")
        
        # Check git status
        print("\n📊 Git Status:")
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        modified = len([l for l in result.stdout.split('\n') if l.startswith(' M')])
        untracked = len([l for l in result.stdout.split('\n') if l.startswith('??')])
        
        print(f"  Modified files: {modified}")
        print(f"  Untracked files: {untracked}")
        
        print("\n✅ Cleanup complete!")
        print("\n💡 Next steps:")
        print("  1. Review changes with 'git status'")
        print("  2. Stage changes with 'git add -A'")
        print("  3. Commit with descriptive message")
        print("  4. Consider creating a new branch for large refactoring tasks")


if __name__ == "__main__":
    cleanup = FinalCleanup()
    cleanup.run_cleanup()