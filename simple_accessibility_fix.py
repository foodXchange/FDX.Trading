#!/usr/bin/env python3
"""
Simple Accessibility Fix System for FDX.trading
Fixes the most critical accessibility issues
"""

import os
import re

def fix_critical_accessibility_issues():
    """Fix critical accessibility issues in key files"""
    
    fixes_applied = []
    
    # Files that need accessibility fixes
    files_to_fix = [
        'templates/suppliers_simple.html',
        'VM_QUICK_ACCESS.html', 
        'tools/vm-access/templates/dashboard.html'
    ]
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Add aria-label to copy buttons without text
            content = re.sub(
                r'(<button[^>]*class="[^"]*btn-outline-secondary[^"]*"[^>]*)(>[\s]*<i class="fas fa-copy"></i>[\s]*</button>)',
                r'\1 aria-label="Copy to clipboard"\2',
                content
            )
            
            # Fix 2: Add aria-label to close buttons
            content = re.sub(
                r'(<button[^>]*class="[^"]*btn-close[^"]*"[^>]*)(>)',
                r'\1 aria-label="Close"\2',
                content
            )
            
            # Fix 3: Add aria-label to icon-only buttons
            content = re.sub(
                r'(<button[^>]*type="button"[^>]*onclick="[^"]*"[^>]*)(>[\s]*<i class="fas fa-copy"></i>[^<]*</button>)',
                r'\1 aria-label="Copy to clipboard"\2',
                content
            )
            
            # Fix 4: Add labels to input fields
            content = re.sub(
                r'(<input[^>]*class="form-control"[^>]*value="[^"]*ssh[^"]*"[^>]*)(>)',
                r'\1 aria-label="SSH command"\2',
                content
            )
            
            content = re.sub(
                r'(<input[^>]*class="form-control"[^>]*value="[^"]*http[^"]*"[^>]*)(>)',
                r'\1 aria-label="Service URL"\2',
                content
            )
            
            # Fix 5: Add role and tabindex to clickable divs
            content = re.sub(
                r'(<div class="ssh-command" onclick="[^"]*")(>)',
                r'\1 role="button" tabindex="0"\2',
                content
            )
            
            # Save if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixes_applied.append(f"Fixed accessibility issues in {file_path}")
                print(f"FIXED: {file_path}")
            else:
                print(f"OK: {file_path} - no changes needed")
                
        except Exception as e:
            print(f"ERROR: {file_path} - {e}")
    
    return fixes_applied

def main():
    """Main function"""
    print("Simple Accessibility Fix System")
    print("=" * 40)
    
    fixes = fix_critical_accessibility_issues()
    
    print(f"\nSummary: {len(fixes)} files fixed")
    for fix in fixes:
        print(f"  - {fix}")
    
    print("\nCritical accessibility issues have been addressed!")

if __name__ == '__main__':
    main()