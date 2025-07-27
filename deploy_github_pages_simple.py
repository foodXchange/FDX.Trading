#!/usr/bin/env python3
"""
Deploy FullStory test page to GitHub Pages
"""

import os
import shutil
import zipfile
from pathlib import Path

def deploy_to_github_pages():
    print("🚀 Deploying FullStory test to GitHub Pages...")
    
    # Create deployment directory
    deploy_dir = Path("github_pages_deploy")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()
    
    # Copy the test file
    test_file = Path("fullstory_simple_test.html")
    if test_file.exists():
        shutil.copy2(test_file, deploy_dir / "index.html")
        print("✅ Copied test file to deployment directory")
    else:
        print("❌ Test file not found")
        return
    
    # Create ZIP for easy upload
    zip_path = "fullstory_github_pages.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in deploy_dir.rglob('*'):
            if file_path.is_file():
                zipf.write(file_path, file_path.relative_to(deploy_dir))
    
    print(f"✅ Created deployment package: {zip_path}")
    print("\n📋 Manual Steps to Deploy:")
    print("1. Go to https://github.com/")
    print("2. Create a new repository (e.g., 'fdx-fullstory-test')")
    print("3. Upload the files from the 'github_pages_deploy' folder")
    print("4. Go to Settings > Pages")
    print("5. Set Source to 'Deploy from a branch'")
    print("6. Select 'main' branch and '/ (root)' folder")
    print("7. Click 'Save'")
    print("8. Wait for deployment (usually 1-2 minutes)")
    print("9. Your site will be available at: https://[username].github.io/[repo-name]/")
    print("\n🔍 After deployment:")
    print("- Visit your GitHub Pages URL")
    print("- Click the test buttons")
    print("- Check your FullStory dashboard for sessions")
    
    # Open GitHub
    import webbrowser
    webbrowser.open("https://github.com/new")
    
    print(f"\n📁 Files ready in: {deploy_dir.absolute()}")

if __name__ == "__main__":
    deploy_to_github_pages() 