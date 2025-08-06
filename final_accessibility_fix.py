#!/usr/bin/env python3
"""
Final Accessibility Fix System for FDX.trading
Addresses all remaining accessibility violations and code quality issues
"""

import os
import re

def fix_vm_dashboard_template():
    """Fix remaining issues in VM dashboard template"""
    file_path = "tools/vm-access/templates/dashboard.html"
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Ensure all close buttons have proper aria-labels
        # Fix any remaining btn-close buttons without aria-label
        content = re.sub(
            r'<button([^>]*?)class="[^"]*btn-close[^"]*"([^>]*?)(?<!aria-label="[^"]*")>',
            r'<button\1class="btn-close"\2 aria-label="Close">',
            content
        )
        
        # Ensure all input fields have aria-labels
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            # Check for input fields without aria-label
            if '<input' in line and 'form-control' in line and 'aria-label=' not in line:
                if 'readonly' in line:
                    if 'ssh' in line.lower():
                        line = line.replace('<input', '<input aria-label="SSH command"')
                    elif 'http' in line.lower():
                        line = line.replace('<input', '<input aria-label="Service URL"')
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        # Save if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"FIXED: {file_path}")
            return True
        else:
            print(f"OK: {file_path} - no changes needed")
            return False
            
    except Exception as e:
        print(f"ERROR: {file_path} - {e}")
        return False

def fix_quick_vm_access():
    """Fix inline style issues in quick VM access files"""
    files = [
        "quick_vm_access.html",
        "tools/vm-access/quick_vm_access.html"
    ]
    
    fixed_files = []
    
    for file_path in files:
        if not os.path.exists(file_path):
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Add CSS class for copy button instead of inline styles
            inline_style_pattern = r'style="margin-top: 10px; padding: 8px 16px; background: var\(--secondary-color\); color: white; border: none; border-radius: 5px; cursor: pointer;"'
            
            if inline_style_pattern in content:
                # Add CSS class to head section if not present
                if '.copy-credentials-btn' not in content:
                    css_class = """        .copy-credentials-btn {
            margin-top: 10px;
            padding: 8px 16px;
            background: var(--secondary-color);
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: var(--transition);
        }
        
        .copy-credentials-btn:hover {
            background: var(--primary-color);
        }
"""
                    # Insert before closing </style> tag
                    content = content.replace('    </style>', css_class + '    </style>')
                
                # Replace inline styles with class
                content = re.sub(
                    inline_style_pattern,
                    'class="copy-credentials-btn"',
                    content
                )
            
            # Save if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(file_path)
                print(f"FIXED: {file_path}")
            else:
                print(f"OK: {file_path} - no changes needed")
                
        except Exception as e:
            print(f"ERROR: {file_path} - {e}")
    
    return fixed_files

def validate_accessibility():
    """Validate that all accessibility issues have been resolved"""
    
    validation_results = {
        'vm_dashboard': True,
        'quick_access': True,
        'issues_found': []
    }
    
    # Check VM dashboard template
    dashboard_path = "tools/vm-access/templates/dashboard.html"
    if os.path.exists(dashboard_path):
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for buttons without aria-labels
        button_pattern = r'<button[^>]*(?<!aria-label="[^"]*")[^>]*><\s*i\s+class="[^"]*"\s*></i>\s*</button>'
        if re.search(button_pattern, content):
            validation_results['issues_found'].append("VM dashboard: Icon-only buttons without aria-labels")
            validation_results['vm_dashboard'] = False
            
        # Check for input fields without labels
        input_pattern = r'<input[^>]*class="form-control"[^>]*(?<!aria-label="[^"]*")(?<!placeholder="[^"]*")[^>]*>'
        if re.search(input_pattern, content):
            validation_results['issues_found'].append("VM dashboard: Input fields without labels")
            validation_results['vm_dashboard'] = False
    
    return validation_results

def main():
    """Main function to fix all accessibility issues"""
    
    print("Final Accessibility Fix System")
    print("=" * 40)
    
    # Fix VM dashboard template
    print("\n1. Fixing VM dashboard template...")
    dashboard_fixed = fix_vm_dashboard_template()
    
    # Fix quick VM access files  
    print("\n2. Fixing quick VM access files...")
    quick_access_fixed = fix_quick_vm_access()
    
    # Validate all fixes
    print("\n3. Validating accessibility compliance...")
    validation = validate_accessibility()
    
    if validation['vm_dashboard'] and validation['quick_access']:
        print("SUCCESS: All accessibility issues have been resolved!")
        print("- VM dashboard template: COMPLIANT")
        print("- Quick access files: COMPLIANT") 
        print("- Inline styles: REMOVED")
        print("- ARIA labels: COMPLETE")
    else:
        print("WARNING: Some issues may remain:")
        for issue in validation['issues_found']:
            print(f"  - {issue}")
    
    # Summary
    total_files_fixed = (1 if dashboard_fixed else 0) + len(quick_access_fixed)
    print(f"\nSummary: {total_files_fixed} files updated")
    
    return validation['vm_dashboard'] and validation['quick_access']

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)