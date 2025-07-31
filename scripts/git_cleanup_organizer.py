"""
Git Cleanup Organizer for FoodXchange
Helps organize and clean uncommitted files
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class GitCleanupOrganizer:
    def __init__(self):
        self.project_path = Path.cwd()
        self.stats = {
            'documentation_files': [],
            'test_files': [],
            'script_files': [],
            'azure_files': [],
            'frontend_files': [],
            'archive_files': [],
            'modified_core_files': []
        }
    
    def analyze_uncommitted_files(self):
        """Analyze uncommitted files and categorize them"""
        print("🔍 Analyzing uncommitted files...")
        
        # Get git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            status = line[:2]
            file_path = line[3:]
            
            # Categorize files
            if file_path.endswith('.md'):
                self.stats['documentation_files'].append((status, file_path))
            elif 'test' in file_path.lower() or file_path.endswith('_test.py'):
                self.stats['test_files'].append((status, file_path))
            elif file_path.endswith('.bat') or file_path.endswith('.sh') or file_path.endswith('.ps1'):
                self.stats['script_files'].append((status, file_path))
            elif 'azure' in file_path.lower():
                self.stats['azure_files'].append((status, file_path))
            elif 'frontend/' in file_path:
                self.stats['frontend_files'].append((status, file_path))
            elif 'archive' in file_path.lower() or 'old' in file_path.lower():
                self.stats['archive_files'].append((status, file_path))
            elif status.strip() == 'M':  # Modified files
                self.stats['modified_core_files'].append((status, file_path))
    
    def display_analysis(self):
        """Display analysis results"""
        print("\n📊 UNCOMMITTED FILES ANALYSIS")
        print("=" * 50)
        
        total_files = sum(len(files) for files in self.stats.values())
        print(f"\nTotal uncommitted files: {total_files}")
        
        print(f"\n📚 Documentation files: {len(self.stats['documentation_files'])}")
        for status, file in self.stats['documentation_files'][:5]:
            print(f"  {status} {file}")
        
        print(f"\n🧪 Test files: {len(self.stats['test_files'])}")
        for status, file in self.stats['test_files'][:5]:
            print(f"  {status} {file}")
        
        print(f"\n📜 Script files: {len(self.stats['script_files'])}")
        for status, file in self.stats['script_files'][:5]:
            print(f"  {status} {file}")
        
        print(f"\n☁️ Azure-related files: {len(self.stats['azure_files'])}")
        for status, file in self.stats['azure_files'][:5]:
            print(f"  {status} {file}")
        
        print(f"\n🎨 Frontend files: {len(self.stats['frontend_files'])}")
        
        print(f"\n📦 Archive/Old files: {len(self.stats['archive_files'])}")
        
        print(f"\n⚙️ Modified core files: {len(self.stats['modified_core_files'])}")
        for status, file in self.stats['modified_core_files'][:5]:
            print(f"  {status} {file}")
    
    def create_gitignore_additions(self):
        """Suggest additions to .gitignore"""
        print("\n💡 Suggested .gitignore additions:")
        
        suggestions = [
            "# Test and temporary files",
            "test_*.py",
            "*_test.py",
            "*.log",
            "cleanup_*.json",
            "system_health_*.json",
            "",
            "# Azure test files",
            "azure_*_test.py",
            "check_azure_*.py",
            "",
            "# Backup and archive",
            "backup_*/",
            "archive/",
            "",
            "# Scripts and automation",
            "*.ps1",
            "setup_env.*",
            "run_all_tests.*",
            "",
            "# Frontend builds",
            "frontend/build/",
            "frontend/dist/",
            "",
            "# Reports",
            "*_REPORT.md",
            "*_GUIDE.md",
            "*_SUMMARY.md"
        ]
        
        print("\n".join(suggestions))
        
        # Save to file
        with open('gitignore_additions.txt', 'w') as f:
            f.write("\n".join(suggestions))
        
        print("\n📄 Saved suggestions to gitignore_additions.txt")
    
    def create_cleanup_script(self):
        """Create a script to clean up unnecessary files"""
        cleanup_commands = []
        
        # Documentation files that might be temporary
        temp_docs = [
            "AI_IMPORT_FEATURE.md",
            "AZURE_DEPLOYMENT_GUIDE.md", 
            "AZURE_SETUP_COMPLETE.md",
            "AZURE_TESTING_GUIDE.md",
            "IMPORT_SYSTEM_CLEANUP.md",
            "README_AZURE_TESTING.md",
            "AI_CODE_REVIEW_REPORT.md",
            "AI_SEARCH_OPTIMIZATION_COMPLETION_REPORT.md"
        ]
        
        # Test and check scripts
        test_scripts = [
            "analyze_document.py",
            "azure_connection_test.py",
            "check_azure_credentials.py",
            "complete_azure_setup.py",
            "azure_setup_summary.py",
            "quick_health_check.py",
            "validate_endpoints.py"
        ]
        
        # Setup scripts
        setup_scripts = [
            "setup_env.bat",
            "setup_env.sh",
            "run_all_tests.bat",
            "run_all_tests.sh",
            "create_gpt4_deployment.sh",
            "AUTO-DEPLOY.ps1"
        ]
        
        print("\n🗑️ Files recommended for cleanup:")
        print("\nTemporary documentation:")
        for doc in temp_docs:
            if Path(doc).exists():
                print(f"  • {doc}")
                cleanup_commands.append(f"del {doc}")
        
        print("\nTest scripts:")
        for script in test_scripts:
            if Path(script).exists():
                print(f"  • {script}")
                cleanup_commands.append(f"del {script}")
        
        print("\nSetup scripts (if no longer needed):")
        for script in setup_scripts:
            if Path(script).exists():
                print(f"  • {script}")
        
        # Create cleanup batch file
        with open('cleanup_temp_files.bat', 'w') as f:
            f.write("@echo off\n")
            f.write("echo Cleaning up temporary files...\n")
            f.write("echo.\n")
            for cmd in cleanup_commands:
                f.write(f"{cmd} 2>nul\n")
            f.write("echo.\n")
            f.write("echo Cleanup complete!\n")
            f.write("pause\n")
        
        print("\n📄 Created cleanup_temp_files.bat")


if __name__ == "__main__":
    organizer = GitCleanupOrganizer()
    organizer.analyze_uncommitted_files()
    organizer.display_analysis()
    organizer.create_gitignore_additions()
    organizer.create_cleanup_script()