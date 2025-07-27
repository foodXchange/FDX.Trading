import os
import sys
from pathlib import Path

print("=== FoodXchange System Health Summary ===\n")

# Basic system info
print(f"Python: {sys.version.split()[0]}")
print(f"Platform: {sys.platform}")
print(f"Working Directory: {os.getcwd()}")

# Check critical files
critical_files = {
    ".env": "Environment configuration",
    ".env.blob": "Azure Blob Storage config",
    "app/main.py": "Main application file",
    "foodxchange.db": "SQLite database"
}

print("\nCritical Files:")
issues = []
for file, desc in critical_files.items():
    if Path(file).exists():
        print(f"  [OK] {file} - {desc}")
    else:
        print(f"  [MISSING] {file} - {desc}")
        issues.append(f"Missing {file}")

# Check Azure configuration
print("\nAzure Services:")
azure_configs = {
    "AZURE_OPENAI_API_KEY": "OpenAI API",
    "AZURE_STORAGE_CONNECTION_STRING": "Blob Storage",
    "AZURE_EMAIL_CONNECTION_STRING": "Email Service"
}

for var, service in azure_configs.items():
    if os.getenv(var):
        print(f"  [OK] {service} configured")
    else:
        # Check .env.blob for storage config
        if var == "AZURE_STORAGE_CONNECTION_STRING" and Path(".env.blob").exists():
            print(f"  [OK] {service} configured (in .env.blob)")
        else:
            print(f"  [NOT SET] {service}")
            issues.append(f"{service} not configured")

# Summary
print(f"\n=== Summary ===")
if not issues:
    print("System Status: HEALTHY")
    print("All critical components are configured properly.")
else:
    print("System Status: NEEDS ATTENTION")
    print(f"Found {len(issues)} issue(s):")
    for issue in issues:
        print(f"  - {issue}")

print("\nRecommendation: Use 'python app/main.py' to start the application")