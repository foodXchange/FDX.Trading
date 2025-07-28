#!/usr/bin/env python3
"""
Script to fix all path references from 'app/' to 'foodxchange/'
"""
import os
import re
from pathlib import Path

def fix_paths_in_file(file_path):
    """Fix paths in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix path references
        original_content = content
        content = re.sub(r'"app/templates"', '"foodxchange/templates"', content)
        content = re.sub(r'"app/static"', '"foodxchange/static"', content)
        content = re.sub(r"'app/templates'", "'foodxchange/templates'", content)
        content = re.sub(r"'app/static'", "'foodxchange/static'", content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed paths in {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix all paths"""
    print("🔧 Fixing path references from 'app/' to 'foodxchange/'")
    print("=" * 60)
    
    # Get all Python files in the foodxchange directory
    foodxchange_dir = Path("foodxchange")
    python_files = list(foodxchange_dir.rglob("*.py"))
    
    fixed_count = 0
    total_count = len(python_files)
    
    for file_path in python_files:
        if fix_paths_in_file(file_path):
            fixed_count += 1
    
    print(f"\n🎉 Path fix complete!")
    print(f"📊 Fixed {fixed_count} out of {total_count} files")
    
    if fixed_count > 0:
        print("\n✅ All path references have been updated!")
        print("🚀 You can now try running the local server again!")
    else:
        print("\nℹ️ No files needed fixing - paths are already correct!")

if __name__ == "__main__":
    main() 