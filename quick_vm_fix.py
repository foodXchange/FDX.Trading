"""
Quick fix to deploy search updates to VM
"""
import subprocess
import time

VM_IP = "4.206.1.15"
KEY_PATH = r"C:\Users\foodz\.ssh\fdx-vm-key.pem"

print("=" * 50)
print("DEPLOYING SEARCH FIX TO AZURE VM")
print("=" * 50)

# Files to copy
files_to_copy = [
    "fixed_search_system.py",
    "app.py"
]

# Copy files
for file in files_to_copy:
    print(f"\nCopying {file} to VM...")
    cmd = f'scp -i "{KEY_PATH}" {file} azureuser@{VM_IP}:~/foodxchange/'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ {file} copied successfully")
    else:
        print(f"❌ Failed to copy {file}: {result.stderr}")

# Restart the app
print("\nRestarting the application...")
restart_cmd = f'''ssh -i "{KEY_PATH}" azureuser@{VM_IP} "cd ~/foodxchange && pkill -f 'python3.*app.py' ; sleep 2 ; nohup python3 app.py > app.log 2>&1 &"'''
subprocess.run(restart_cmd, shell=True)

print("\nWaiting for app to start...")
time.sleep(5)

# Check if running
check_cmd = f'''ssh -i "{KEY_PATH}" azureuser@{VM_IP} "ps aux | grep 'python3.*app.py' | grep -v grep"'''
result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)

if "python3" in result.stdout:
    print("✅ App is running!")
else:
    print("⚠️ App may not be running. Check manually.")

print("\n" + "=" * 50)
print("DEPLOYMENT COMPLETE!")
print("=" * 50)
print(f"\nTest the search at: http://{VM_IP}:8000/suppliers")
print("Try searching for 'oil' or 'olive'")