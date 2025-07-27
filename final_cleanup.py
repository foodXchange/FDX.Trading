#!/usr/bin/env python3
"""
Final FoodXchange System Cleanup Script
Removes remaining unnecessary files for a completely clean workspace.
"""

import os
import shutil
import glob

def final_cleanup():
    """Final cleanup function"""
    print("🧹 Starting Final FoodXchange System Cleanup...")
    
    # Additional files to remove
    files_to_remove = [
        # Cleanup scripts
        "cleanup_system.py",
        "final_cleanup.py",
        
        # Node.js files (not needed for Python app)
        "package-lock.json",
        "package.json",
        
        # Remaining deployment and setup files
        "simple_server.py",
        "index.html",
        "deploy_now.bat",
        "setup_fullstory.ps1",
        "verify_fullstory.py",
        "check-fullstory.ps1",
        "implement_fullstory.py",
        "setup_uptimerobot_monitors.py",
        "optimize_monitoring.py",
        "sentry_optimizer.py",
        "sentry_middleware.py",
        "monitoring_optimizations.py",
        "sentry_optimized_config.py",
        "setup_sentry_complete.py",
        "test_sentry_setup.bat",
        "deploy_to_azure.py",
        "next_steps.bat",
        "implement_everything.py",
        "test_uptimerobot.py",
        "test_sentry.py",
        "uptimerobot_client.py",
        "setup_everything.bat",
        "setup_monitoring_complete.py",
        "deploy_complete.py",
        "start_production.py",
        "start_optimized.py",
        "fix_supabase_complete.bat",
        "fix_supabase_complete.py",
        "fix_supabase_final.bat",
        "fix_supabase_final.py",
        "fix_supabase_issues_improved.py",
        "fix_supabase_issues.ps1",
        "fix_supabase_issues.bat",
        "fix_supabase_issues.py",
        "setup_uptimerobot.py",
        "setup_monitoring.bat",
        "setup_sentry.py",
        "fix_database_indexes.py",
        "fix_rls_performance_simple.py",
        "fix_rls_performance.py",
        "supabase_health_check.py",
        "test_supabase_connection.py",
        "fix_cryptography_warning.bat",
        "check_python_architecture.py",
        "start_app.bat",
        "check_dns_google.bat",
        "check_dns_propagation.bat",
        "redirect_setup.py",
        "setup_custom_domain.ps1",
        
        # Configuration files
        "uptimerobot_config.json",
        "monitoring_config.json",
        "production.env.backup_20250726_203351",
        "startup.txt",
        "web.config",
        "requirements_production.txt",
        "API",
        
        # Documentation files (keeping only essential ones)
        "QUICK_DEPLOYMENT_GUIDE.md",
        "SENTRY_REMAINING_STEPS.md",
        "SENTRY_COMPLETION_SUMMARY.md",
        "FULLSTORY_SETUP_GUIDE.md",
        "FINAL_COMPLETE_SETUP_SUMMARY.md",
        "FINAL_OPTIMIZATION_SUMMARY.md",
        "MONITORING_OPTIMIZATION_SUMMARY.md",
        "SENTRY_FINAL_OPTIMIZATION_SUMMARY.md",
        "SENTRY_OPTIMIZATION_GUIDE.md",
        "SENTRY_IMPLEMENTATION_SUMMARY.md",
        "SENTRY_COMPLETE_SETUP_GUIDE.md",
        "FINAL_MANUAL_TASKS.md",
        "COMPLETE_IMPLEMENTATION_GUIDE.md",
        "FINAL_SUMMARY.md",
        "IMPLEMENTATION_REPORT.md",
        "MONITORING_GUIDE.md",
        "COMPLETE_SETUP_GUIDE.md",
        "DEPLOYMENT_CHECKLIST.md",
        "MONITORING_SETUP_GUIDE.md",
        "DNS_CHANGES_SUMMARY.md",
        "SUPABASE_COMPLETE_FIX_SUMMARY.md",
        "SUPABASE_FIX_RESULTS.md",
        "SUPABASE_ISSUES_FIX_SUMMARY.md",
        "UPTIMEROBOT_SETUP_GUIDE.md",
        "MONITORING_SETUP_SUMMARY.md",
        "INDEX_OPTIMIZATION_SUMMARY.md",
        "RLS_PERFORMANCE_FIX_SUMMARY.md",
        "SUPABASE_DATABASE_REPORT.md",
        "CLAUDE_CODE_REFERENCE.md",
        "DOMAIN_CHANGE_SUMMARY.md",
        "NAMECHEAP_DNS_SETUP.md",
        
        # HTML files
        "sentry_dashboard.html",
        "monitoring_dashboard.html",
        
        # Zip files
        "foodxchange_deployment.zip",
    ]
    
    # Directories to remove
    dirs_to_remove = [
        "node_modules",
        "__pycache__",
        ".claude"
    ]
    
    # Remove files
    removed_files = 0
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️  Removed: {file_path}")
                removed_files += 1
            except Exception as e:
                print(f"❌ Failed to remove {file_path}: {e}")
    
    # Remove directories
    removed_dirs = 0
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"🗑️  Removed directory: {dir_path}")
                removed_dirs += 1
            except Exception as e:
                print(f"❌ Failed to remove directory {dir_path}: {e}")
    
    # Clean up any remaining temporary files
    temp_patterns = [
        "*.tmp",
        "*.temp",
        "*.log",
        "*.bak",
        "*.backup",
        "*~",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    temp_files_removed = 0
    for pattern in temp_patterns:
        for file_path in glob.glob(pattern):
            try:
                os.remove(file_path)
                print(f"🗑️  Removed temp file: {file_path}")
                temp_files_removed += 1
            except Exception as e:
                print(f"❌ Failed to remove temp file {file_path}: {e}")
    
    # Summary
    print(f"\n✅ Final Cleanup Complete!")
    print(f"📊 Summary:")
    print(f"   - Files removed: {removed_files}")
    print(f"   - Directories removed: {removed_dirs}")
    print(f"   - Temporary files removed: {temp_files_removed}")
    print(f"   - Total items cleaned: {removed_files + removed_dirs + temp_files_removed}")
    
    print(f"\n🎯 Your FoodXchange workspace is now completely clean!")
    print(f"📁 Clean workspace structure:")
    print(f"   - app/ (main application)")
    print(f"   - database/ (database setup)")
    print(f"   - docs/ (documentation)")
    print(f"   - Logo/ (brand assets)")
    print(f"   - Fonts/ (custom fonts)")
    print(f"   - Photos/ (media assets)")
    print(f"   - backend/ (backend files)")
    print(f"   - requirements.txt (Python dependencies)")
    print(f"   - .git/ (version control)")

if __name__ == "__main__":
    final_cleanup() 