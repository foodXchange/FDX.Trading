#!/usr/bin/env python3
"""
FoodXchange System Cleanup Script
Removes unnecessary files and organizes the workspace for a lean development environment.
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_system():
    """Main cleanup function"""
    print("Starting FoodXchange System Cleanup...")
    
    # Files to remove (deployment and test files)
    files_to_remove = [
        # Deployment scripts and files
        "deploy_fdx_test.ps1",
        "setup-v0-pro-complete.ps1",
        "setup-v0-pro-simple.ps1",
        "setup-v0-pro.ps1",
        "deploy_test_page.bat",
        "deploy_full.bat",
        "deploy_full.ps1",
        "deploy_minimal.bat",
        "deploy_simple.bat",
        "deploy_powershell.ps1",
        "deploy_simple.ps1",
        "deploy_via_powershell.ps1",
        "deploy_via_portal.ps1",
        "restart_app.ps1",
        "open_azure_portal.ps1",
        "get_gtm_container_id.ps1",
        "quick_start_gtm_fullstory.bat",
        "quick-v0-setup.bat",
        "v0-deploy.ps1",
        "integrate-v0.ps1",
        "v0-components.ps1",
        "test_sentry_simple.bat",
        
        # Python deployment scripts
        "deploy_full_app.py",
        "deploy_to_fdx_trading.py",
        "deploy_simple_server.py",
        "deploy_static.py",
        "deploy_minimal.py",
        "make_deploy_zip.py",
        "fix_deployment.py",
        "create_full_deployment.py",
        "configure_gtm_container.py",
        "test_gtm_integration.py",
        "update_gtm_config.py",
        "setup_gtm_fullstory.py",
        "fullstory_fdx_optimization.py",
        "test_sentry_setup.py",
        "install_dependencies.py",
        "app_backup.py",
        "app_minimal.py",
        "sentry_config.py",
        
        # Test and temporary files
        "test_fullstory_simple.html",
        "deploy_to_netlify.html",
        "fullstory_test.html",
        "simple_app.py",
        "app.py",
        
        # Zip files
        "fdx_fullstory_test.zip",
        "full_app.zip",
        "simple_server.zip",
        "static_app.zip",
        "minimal_app.zip",
        "fullstory_test.zip",
        "app.zip",
        "foodxchange_full.zip",
        "app-logs-new.zip",
        "app-logs.zip",
        
        # Configuration files (keep only essential ones)
        "gtm_config.json",
        "fdx_fullstory_dashboard.json",
        "fdx_fullstory_funnels.json",
        "fdx_fullstory_segments.json",
        "fdx_fullstory_events.json",
        "fdx_fullstory_tracking.js",
        "fdx_fullstory_optimization.py",
        
        # Documentation files (keep only essential ones)
        "V0_PRO_FINAL_SUMMARY.md",
        "V0_PRO_COMPLETE_SETUP_GUIDE.md",
        "V0_PRO_FINAL_SETUP.md",
        "V0_PRO_CUSTOM_FONTS_SETUP.md",
        "V0_PRO_SETUP_SUMMARY.md",
        "V0_PRO_QUICK_START.md",
        "MANUAL_DEPLOYMENT_GUIDE.md",
        "V0_SETUP_SUMMARY.md",
        "V0_SETUP_GUIDE.md",
        "FDX_FULLSTORY_IMPLEMENTATION_GUIDE.md",
        "FDX_MANUAL_STEPS.md",
        "FDX_USER_IDENTIFICATION_GUIDE.md",
        "FULLSTORY_USER_IDENTIFICATION_COMPLETE.md",
        "FULLSTORY_INSTALLATION_COMPLETE.md",
        "GTM_FULLSTORY_SETUP_COMPLETE.md",
        "GTM_FULLSTORY_INTEGRATION_GUIDE.md",
        "FINAL_GTM_FULLSTORY_COMPLETE.md",
        "SENTRY_SETUP_SUMMARY.md",
        "sentry_setup_guide.md",
        "v0-prompts.md",
        "v0-pro-optimized-prompts.md",
        "v0-pro-config.md",
        "deploy_github_pages.md",
        
        # Other temporary files
        "Kudu",
        "Go",
        "requirements_minimal.txt",
        "production.env"
    ]
    
    # Directories to remove
    dirs_to_remove = [
        "deploy_fdx_test",
        "deploy_working",
        "app-logs",
        "app-logs-new",
        "node_modules"
    ]
    
    # Remove files
    removed_files = 0
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
                removed_files += 1
            except Exception as e:
                print(f"Failed to remove {file_path}: {e}")
    
    # Remove directories
    removed_dirs = 0
    for dir_path in dirs_to_remove:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Removed directory: {dir_path}")
                removed_dirs += 1
            except Exception as e:
                print(f"Failed to remove directory {dir_path}: {e}")
    
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
                print(f"Removed temp file: {file_path}")
                temp_files_removed += 1
            except Exception as e:
                print(f"Failed to remove temp file {file_path}: {e}")
    
    # Create a clean .gitignore if it doesn't exist
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
*.bak
*~

# Uploads
uploads/

# Environment files
.env
.env.local
.env.production

# Node modules (if any)
node_modules/

# Deployment artifacts
*.zip
deploy_*/
setup-*.ps1
deploy_*.bat
deploy_*.py
test_*.py
*_test.*
fullstory_*
gtm_*
sentry_*
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("Created .gitignore file")
    
    # Summary
    print(f"\nCleanup Complete!")
    print(f"Summary:")
    print(f"   - Files removed: {removed_files}")
    print(f"   - Directories removed: {removed_dirs}")
    print(f"   - Temporary files removed: {temp_files_removed}")
    print(f"   - Total items cleaned: {removed_files + removed_dirs + temp_files_removed}")
    
    print(f"\nYour FoodXchange workspace is now clean and organized!")
    print(f"Core application structure preserved:")
    print(f"   - app/ (main application)")
    print(f"   - database/ (database setup)")
    print(f"   - docs/ (documentation)")
    print(f"   - Logo/ (brand assets)")
    print(f"   - Fonts/ (custom fonts)")
    print(f"   - Photos/ (media assets)")

if __name__ == "__main__":
    cleanup_system() 