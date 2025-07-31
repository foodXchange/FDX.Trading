"""
Find TODO Items in FoodXchange
Locates all TODO, FIXME, and similar markers in the codebase
"""

import os
import sys
from pathlib import Path
import re

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def find_todo_items():
    """Find all TODO, FIXME, HACK, NOTE items in Python files"""
    print("🔍 Finding TODO items in codebase")
    print("=" * 50)
    
    patterns = {
        'TODO': re.compile(r'#\s*TODO:?\s*(.*)$', re.IGNORECASE),
        'FIXME': re.compile(r'#\s*FIXME:?\s*(.*)$', re.IGNORECASE),
        'HACK': re.compile(r'#\s*HACK:?\s*(.*)$', re.IGNORECASE),
        'NOTE': re.compile(r'#\s*NOTE:?\s*(.*)$', re.IGNORECASE),
        'XXX': re.compile(r'#\s*XXX:?\s*(.*)$', re.IGNORECASE)
    }
    
    todos_by_type = {key: [] for key in patterns}
    
    for py_file in Path('.').rglob('*.py'):
        # Skip virtual environments and cache
        if any(skip in str(py_file) for skip in ['.venv', '__pycache__', 'archive', 'backup']):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                for todo_type, pattern in patterns.items():
                    match = pattern.search(line)
                    if match:
                        todos_by_type[todo_type].append({
                            'file': str(py_file),
                            'line': line_num,
                            'text': match.group(1).strip(),
                            'full_line': line.strip()
                        })
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    # Display results
    total_todos = sum(len(items) for items in todos_by_type.values())
    print(f"\nFound {total_todos} items total:\n")
    
    for todo_type, items in todos_by_type.items():
        if items:
            print(f"\n📌 {todo_type} items ({len(items)}):")
            print("-" * 40)
            
            # Group by file
            files = {}
            for item in items:
                if item['file'] not in files:
                    files[item['file']] = []
                files[item['file']].append(item)
            
            for file_path, file_items in files.items():
                print(f"\n{file_path}:")
                for item in file_items[:3]:  # Show first 3 per file
                    print(f"  Line {item['line']}: {item['text'][:60]}{'...' if len(item['text']) > 60 else ''}")
                if len(file_items) > 3:
                    print(f"  ... and {len(file_items) - 3} more")
    
    # Generate summary report
    print("\n\n📊 Priority TODOs to address:")
    print("=" * 50)
    
    # Find high priority items
    priority_keywords = ['urgent', 'important', 'critical', 'fix', 'bug', 'security', 'performance']
    high_priority = []
    
    for todo_type, items in todos_by_type.items():
        for item in items:
            if any(keyword in item['text'].lower() for keyword in priority_keywords):
                high_priority.append(item)
    
    if high_priority:
        print(f"\n🚨 High Priority Items ({len(high_priority)}):")
        for item in high_priority[:10]:
            print(f"  {item['file']}:{item['line']}")
            print(f"    {item['full_line']}")
    
    return todos_by_type


if __name__ == "__main__":
    todos = find_todo_items()
    
    # Save detailed report
    with open('todo_report.txt', 'w', encoding='utf-8') as f:
        f.write("FoodXchange TODO Report\n")
        f.write("=" * 50 + "\n\n")
        
        for todo_type, items in todos.items():
            if items:
                f.write(f"\n{todo_type} Items ({len(items)}):\n")
                f.write("-" * 40 + "\n")
                for item in items:
                    f.write(f"{item['file']}:{item['line']} - {item['text']}\n")
    
    print("\n\n📄 Detailed report saved to todo_report.txt")