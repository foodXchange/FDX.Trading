"""
Find Large Files in FoodXchange
Identifies Python files with more than 500 lines
"""

import os
import sys
from pathlib import Path

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def find_large_python_files(threshold=500):
    """Find Python files exceeding line threshold"""
    print(f"🔍 Finding Python files with >{threshold} lines")
    print("=" * 50)
    
    large_files = []
    
    for py_file in Path('.').rglob('*.py'):
        # Skip virtual environments and cache
        if any(skip in str(py_file) for skip in ['.venv', '__pycache__', 'archive', 'backup']):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            if lines > threshold:
                large_files.append({
                    'path': str(py_file),
                    'lines': lines,
                    'size_kb': py_file.stat().st_size / 1024
                })
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    # Sort by line count
    large_files.sort(key=lambda x: x['lines'], reverse=True)
    
    # Display results
    print(f"\nFound {len(large_files)} files with >{threshold} lines:\n")
    
    for i, file_info in enumerate(large_files, 1):
        print(f"{i:2d}. {file_info['path']}")
        print(f"    Lines: {file_info['lines']:,} | Size: {file_info['size_kb']:.1f} KB")
        
        # Analyze file structure
        analyze_file_structure(file_info['path'])
        print()
    
    return large_files


def analyze_file_structure(file_path):
    """Analyze the structure of a large file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count different elements
        class_count = content.count('class ')
        def_count = content.count('def ')
        import_count = len([line for line in content.split('\n') if line.strip().startswith(('import ', 'from '))])
        
        print(f"    Structure: {class_count} classes, {def_count} functions, {import_count} imports")
        
        # Suggest refactoring
        if class_count > 3:
            print(f"    💡 Consider splitting into multiple modules (too many classes)")
        elif def_count > 20:
            print(f"    💡 Consider grouping related functions into separate modules")
        
    except Exception as e:
        print(f"    Error analyzing: {e}")


if __name__ == "__main__":
    large_files = find_large_python_files()
    
    print("\n📊 Summary:")
    print(f"Total large files: {len(large_files)}")
    total_lines = sum(f['lines'] for f in large_files)
    print(f"Total lines in large files: {total_lines:,}")
    
    if large_files:
        avg_lines = total_lines / len(large_files)
        print(f"Average lines per file: {avg_lines:.0f}")