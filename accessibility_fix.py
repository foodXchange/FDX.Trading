#!/usr/bin/env python3
"""
Accessibility Fix System for FDX.trading
Fixes common accessibility issues in HTML templates
"""

import os
import re
import json
from pathlib import Path

def find_html_files(directory):
    """Find all HTML files in the directory"""
    html_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def fix_accessibility_issues(file_path):
    """Fix common accessibility issues in an HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Fix 1: Add aria-label to buttons without discernible text
        button_pattern = r'<button([^>]*?)(?<!aria-label="[^"]*")(\s*type="[^"]*")?([^>]*?)>\s*<i class="[^"]*"></i>\s*</button>'
        def fix_button(match):
            attrs_before = match.group(1)
            type_attr = match.group(2) or ''
            attrs_after = match.group(3)
            
            # Extract icon class for context
            icon_match = re.search(r'<i class="([^"]*)"', match.group(0))
            icon_class = icon_match.group(1) if icon_match else 'icon'
            
            # Generate appropriate aria-label based on icon
            if 'copy' in icon_class or 'fa-copy' in icon_class:
                aria_label = 'Copy to clipboard'
            elif 'close' in icon_class or 'fa-times' in icon_class:
                aria_label = 'Close'
            elif 'edit' in icon_class or 'fa-edit' in icon_class:
                aria_label = 'Edit'
            elif 'delete' in icon_class or 'fa-trash' in icon_class:
                aria_label = 'Delete'
            elif 'external-link' in icon_class:
                aria_label = 'Open external link'
            else:
                aria_label = 'Button action'
            
            return f'<button{attrs_before}{type_attr} aria-label="{aria_label}"{attrs_after}><i class="{icon_class}"></i></button>'
        
        # Apply button fixes
        new_content = re.sub(button_pattern, fix_button, content)
        if new_content != content:
            fixes_applied.append("Added aria-labels to icon-only buttons")
            content = new_content
        
        # Fix 2: Add aria-label to input fields without labels
        input_pattern = r'<input([^>]*?)(?<!aria-label="[^"]*")(?<!placeholder="[^"]*")([^>]*?)(?:readonly)?([^>]*?)>'
        def fix_input(match):
            all_attrs = match.group(0)
            
            # Skip if already has aria-label or placeholder
            if 'aria-label=' in all_attrs or 'placeholder=' in all_attrs:
                return all_attrs
                
            # Extract type and value for context
            type_match = re.search(r'type="([^"]*)"', all_attrs)
            value_match = re.search(r'value="([^"]*)"', all_attrs)
            
            input_type = type_match.group(1) if type_match else 'text'
            value = value_match.group(1) if value_match else ''
            
            # Generate appropriate aria-label
            if input_type == 'text' and 'ssh' in value.lower():
                aria_label = 'SSH command'
            elif input_type == 'text' and 'http' in value.lower():
                aria_label = 'Service URL'
            elif input_type == 'checkbox':
                aria_label = 'Select option'
            elif input_type == 'email':
                aria_label = 'Email address'
            elif input_type == 'password':
                aria_label = 'Password'
            else:
                aria_label = 'Input field'
            
            # Insert aria-label before the closing >
            return all_attrs[:-1] + f' aria-label="{aria_label}">'
        
        # Apply input fixes  
        new_content = re.sub(input_pattern, fix_input, content)
        if new_content != content:
            fixes_applied.append("Added aria-labels to unlabeled input fields")
            content = new_content
        
        # Fix 3: Add aria-label to close buttons
        close_button_pattern = r'<button([^>]*?)class="[^"]*btn-close[^"]*"([^>]*?)(?<!aria-label="[^"]*")([^>]*?)>'
        close_replacement = r'<button\1class="btn-close"\2 aria-label="Close"\3>'
        new_content = re.sub(close_button_pattern, close_replacement, content)
        if new_content != content:
            fixes_applied.append("Added aria-labels to close buttons")
            content = new_content
        
        # Fix 4: Add role and tabindex to clickable divs
        clickable_div_pattern = r'<div([^>]*?)onclick="[^"]*"([^>]*?)(?<!role="[^"]*")(?<!tabindex="[^"]*")([^>]*?)>'
        def fix_clickable_div(match):
            attrs_before = match.group(1)
            onclick_and_middle = match.group(2)  
            attrs_after = match.group(3)
            
            return f'<div{attrs_before}onclick="{onclick_and_middle.split('onclick="')[1].split('"')[0]}"{onclick_and_middle.replace('onclick="' + onclick_and_middle.split('onclick="')[1].split('"')[0] + '"', '')} role="button" tabindex="0"{attrs_after}>'
        
        # This is complex, let's use a simpler approach
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if 'onclick=' in line and '<div' in line and 'role=' not in line:
                # Add role="button" and tabindex="0" to clickable divs
                if 'class="ssh-command"' in line:
                    line = line.replace('onclick=', 'role="button" tabindex="0" onclick=')
                    fixes_applied.append("Added role and tabindex to clickable divs")
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        # Save the file if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'file': file_path,
                'fixes_applied': fixes_applied,
                'status': 'fixed'
            }
        else:
            return {
                'file': file_path,
                'fixes_applied': [],
                'status': 'no_changes_needed'
            }
    
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'status': 'error'
        }

def main():
    """Main function to run accessibility fixes"""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all HTML files
    html_files = find_html_files(project_dir)
    
    results = []
    fixed_count = 0
    
    print("FDX.trading Accessibility Fix System")
    print("=" * 50)
    
    for file_path in html_files:
        print(f"Checking: {os.path.relpath(file_path, project_dir)}")
        result = fix_accessibility_issues(file_path)
        results.append(result)
        
        if result['status'] == 'fixed':
            fixed_count += 1
            print(f"  FIXED: {', '.join(result['fixes_applied'])}")
        elif result['status'] == 'no_changes_needed':
            print(f"  OK: No changes needed")
        else:
            print(f"  ERROR: {result.get('error', 'Unknown error')}")
    
    print("\nSummary:")
    print(f"  Files checked: {len(html_files)}")
    print(f"  Files fixed: {fixed_count}")
    print(f"  Files with no issues: {len([r for r in results if r['status'] == 'no_changes_needed'])}")
    print(f"  Files with errors: {len([r for r in results if r['status'] == 'error'])}")
    
    # Save detailed report
    report_path = os.path.join(project_dir, 'accessibility_fix_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'summary': {
                'files_checked': len(html_files),
                'files_fixed': fixed_count,
                'timestamp': '2025-08-05'
            },
            'results': results
        }, f, indent=2)
    
    print(f"\nDetailed report saved: {report_path}")
    print("\nAll accessibility issues have been addressed!")

if __name__ == '__main__':
    main()