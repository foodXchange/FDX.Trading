#!/usr/bin/env python3
"""
Script to fix all import statements from 'app.' to 'foodxchange.'
"""
import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix from app. imports
        original_content = content
        content = re.sub(r'from app\.', 'from foodxchange.', content)
        content = re.sub(r'import app\.', 'import foodxchange.', content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed imports in {file_path}")
            return True
        return False
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix all imports"""
    print("🔧 Fixing import statements from 'app.' to 'foodxchange.'")
    print("=" * 60)
    
    # Get all Python files in the foodxchange directory
    foodxchange_dir = Path("foodxchange")
    python_files = list(foodxchange_dir.rglob("*.py"))
    
    fixed_count = 0
    total_count = len(python_files)
    
    for file_path in python_files:
        if fix_imports_in_file(file_path):
            fixed_count += 1
    
    print(f"\n🎉 Import fix complete!")
    print(f"📊 Fixed {fixed_count} out of {total_count} files")
    
    if fixed_count > 0:
        print("\n✅ All import statements have been updated from 'app.' to 'foodxchange.'")
        print("🚀 You can now try running the local server again!")
    else:
        print("\nℹ️ No files needed fixing - imports are already correct!")

if __name__ == "__main__":
    main() 