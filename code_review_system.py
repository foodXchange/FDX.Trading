#!/usr/bin/env python3
"""
Comprehensive Code Review System for FDX.trading
Automatically checks code quality, security, and best practices
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class CodeReviewSystem:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.fixes_applied = []
        
    def review_all(self) -> Dict[str, Any]:
        """Run comprehensive code review"""
        print("🔍 Starting comprehensive code review...")
        
        # Review different file types
        self.review_python_files()
        self.review_html_templates()
        self.review_security()
        self.review_performance()
        self.review_accessibility()
        
        return self.generate_report()
    
    def review_python_files(self):
        """Review Python files for best practices"""
        print("📝 Reviewing Python files...")
        
        for py_file in self.project_root.rglob("*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            self.review_python_file(py_file)
    
    def review_python_file(self, file_path: Path):
        """Review individual Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Check for security issues
            if "password" in content.lower() and "=" in content:
                if not re.search(r'password.*=.*os\.getenv|password.*=.*\*', content.lower()):
                    self.add_issue("security", f"Potential hardcoded password in {file_path}")
            
            # Check for SQL injection vulnerabilities
            if "execute(" in content and "%" in content:
                if not re.search(r'execute\([^)]*%s', content):
                    self.add_issue("security", f"Potential SQL injection in {file_path}")
            
            # Check for proper error handling
            if "except:" in content:
                self.add_issue("quality", f"Bare except clause in {file_path}")
            
            # Check for print statements (should use logging)
            print_count = len(re.findall(r'\bprint\(', content))
            if print_count > 5:
                self.add_issue("quality", f"Too many print statements ({print_count}) in {file_path}")
                
        except Exception as e:
            self.add_issue("error", f"Could not review {file_path}: {e}")
    
    def review_html_templates(self):
        """Review HTML templates"""
        print("🌐 Reviewing HTML templates...")
        
        for html_file in self.project_root.rglob("*.html"):
            self.review_html_file(html_file)
    
    def review_html_file(self, file_path: Path):
        """Review individual HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check for missing button types
            button_matches = re.findall(r'<button[^>]*>', content)
            for button in button_matches:
                if 'type=' not in button:
                    self.add_issue("accessibility", f"Button missing type attribute in {file_path}")
                    # Auto-fix suggestion
                    self.suggest_fix(file_path, "Add type='button' to buttons")
            
            # Check for missing alt attributes on images
            img_matches = re.findall(r'<img[^>]*>', content)
            for img in img_matches:
                if 'alt=' not in img:
                    self.add_issue("accessibility", f"Image missing alt attribute in {file_path}")
            
            # Check for proper charset and viewport
            if '<meta charset=' not in content:
                self.add_issue("html", f"Missing charset meta tag in {file_path}")
            
            if '<meta name="viewport"' not in content:
                self.add_issue("html", f"Missing viewport meta tag in {file_path}")
                
        except Exception as e:
            self.add_issue("error", f"Could not review {file_path}: {e}")
    
    def review_security(self):
        """Review security configurations"""
        print("🔒 Reviewing security...")
        
        # Check for .env file exposure
        gitignore_path = self.project_root / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
                if ".env" not in gitignore_content:
                    self.add_issue("security", ".env file not in .gitignore")
        
        # Check for exposed secrets
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.html', '.env']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check for API keys or passwords
                    secret_patterns = [
                        r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                        r'password\s*=\s*["\'][^"\']+["\']',
                        r'secret\s*=\s*["\'][^"\']{20,}["\']'
                    ]
                    
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.add_issue("security", f"Potential exposed secret in {file_path}")
                            
                except:
                    continue
    
    def review_performance(self):
        """Review performance issues"""
        print("⚡ Reviewing performance...")
        
        # Check for missing cache headers
        app_files = list(self.project_root.rglob("app.py"))
        for app_file in app_files:
            with open(app_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if "Cache-Control" not in content:
                self.add_issue("performance", f"Missing cache control headers in {app_file}")
    
    def review_accessibility(self):
        """Review accessibility issues"""
        print("♿ Reviewing accessibility...")
        
        # Already covered in HTML review
        pass
    
    def add_issue(self, category: str, description: str):
        """Add an issue to the review"""
        self.issues.append({
            "category": category,
            "description": description,
            "timestamp": datetime.now().isoformat()
        })
    
    def suggest_fix(self, file_path: Path, fix_description: str):
        """Suggest a fix for an issue"""
        self.fixes_applied.append({
            "file": str(file_path),
            "fix": fix_description,
            "timestamp": datetime.now().isoformat()
        })
    
    def auto_fix_issues(self):
        """Automatically fix common issues"""
        print("🔧 Applying automatic fixes...")
        
        # Fix button type attributes
        for html_file in self.project_root.rglob("*.html"):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Fix buttons without type attribute
                original_content = content
                content = re.sub(
                    r'<button(\s+[^>]*)?(?<!type=")(\s*)>',
                    r'<button\1 type="button"\2>',
                    content
                )
                
                # Fix submit buttons
                content = re.sub(
                    r'<button([^>]*onclick="[^"]*submit[^"]*"[^>]*)type="button"',
                    r'<button\1type="submit"',
                    content
                )
                
                if content != original_content:
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixes_applied.append({
                        "file": str(html_file),
                        "fix": "Added type attributes to buttons",
                        "timestamp": datetime.now().isoformat()
                    })
                    print(f"✅ Fixed button types in {html_file}")
                    
            except Exception as e:
                print(f"❌ Could not fix {html_file}: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive review report"""
        issues_by_category = {}
        for issue in self.issues:
            category = issue["category"]
            if category not in issues_by_category:
                issues_by_category[category] = []
            issues_by_category[category].append(issue)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_issues": len(self.issues),
            "issues_by_category": issues_by_category,
            "fixes_applied": self.fixes_applied,
            "summary": {
                "critical": len([i for i in self.issues if i["category"] == "security"]),
                "warnings": len([i for i in self.issues if i["category"] in ["performance", "quality"]]),
                "info": len([i for i in self.issues if i["category"] in ["accessibility", "html"]])
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = "code_review_report.json"):
        """Save report to file"""
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📋 Report saved to {filename}")
    
    def print_summary(self, report: Dict[str, Any]):
        """Print review summary"""
        print("\n" + "="*60)
        print("📊 CODE REVIEW SUMMARY")
        print("="*60)
        print(f"Total Issues Found: {report['total_issues']}")
        print(f"Critical (Security): {report['summary']['critical']}")
        print(f"Warnings (Performance/Quality): {report['summary']['warnings']}")
        print(f"Info (Accessibility/HTML): {report['summary']['info']}")
        print(f"Fixes Applied: {len(report['fixes_applied'])}")
        
        if report['issues_by_category']:
            print("\n📝 Issues by Category:")
            for category, issues in report['issues_by_category'].items():
                print(f"\n{category.upper()}:")
                for issue in issues[:5]:  # Show first 5 issues per category
                    print(f"  • {issue['description']}")
                if len(issues) > 5:
                    print(f"  ... and {len(issues) - 5} more")
        
        if report['fixes_applied']:
            print("\n🔧 Fixes Applied:")
            for fix in report['fixes_applied']:
                print(f"  ✅ {fix['fix']} - {fix['file']}")
        
        print("\n" + "="*60)

def main():
    """Main function to run code review"""
    reviewer = CodeReviewSystem()
    
    # Apply automatic fixes first
    reviewer.auto_fix_issues()
    
    # Run comprehensive review
    report = reviewer.review_all()
    
    # Print summary
    reviewer.print_summary(report)
    
    # Save detailed report
    reviewer.save_report(report)
    
    return report

if __name__ == "__main__":
    main()