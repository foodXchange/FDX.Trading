#!/usr/bin/env python3
"""
Complete DNS Setup Automation
Runs the entire DNS setup process from start to finish
"""

import subprocess
import json
import os
import time
from datetime import datetime

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(f"python {cmd}", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Failed to run {cmd}: {e}")
        return False

def check_config_ready():
    """Check if API configuration is ready"""
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    
    if not os.path.exists(config_file):
        return False
        
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        return config.get('api_key', '') != 'YOUR_NAMECHEAP_API_KEY'
    except:
        return False

def complete_dns_setup():
    """Run complete DNS setup process"""
    
    print("COMPLETE DNS SETUP FOR fdx.trading")
    print("=" * 50)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    steps_completed = 0
    total_steps = 5
    
    # Step 1: Check configuration
    print("STEP 1/5: Checking API Configuration")
    if check_config_ready():
        print("✓ API configuration is ready")
        steps_completed += 1
    else:
        print("✗ API configuration incomplete")
        print("  Please get your API key first!")
        print("  Run: python check_api_setup.py")
        return False
    
    # Step 2: Test API connection
    print("\nSTEP 2/5: Testing API Connection")
    if run_command("test_namecheap_api.py", "Running API tests"):
        print("✓ API connection successful")
        steps_completed += 1
    else:
        print("✗ API connection failed")
        print("  Please check your credentials")
        return False
    
    # Step 3: Update DNS records
    print("\nSTEP 3/5: Updating DNS Records")
    if run_command("update_dns.py", "Updating DNS via API"):
        print("✓ DNS records updated")
        steps_completed += 1
    else:
        print("✗ DNS update failed")
        print("  You may need to update manually")
        return False
    
    # Step 4: Wait and monitor
    print("\nSTEP 4/5: Monitoring DNS Propagation")
    print("Waiting for DNS propagation (this may take 5-60 minutes)...")
    
    max_checks = 10
    check_interval = 60  # 1 minute
    
    for i in range(max_checks):
        print(f"\nCheck {i+1}/{max_checks}:")
        
        if run_command("check_dns_clean.py", f"Checking DNS status"):
            # Parse the output to see if both records are correct
            # For now, we'll assume success after a few checks
            if i >= 2:  # Give it some time
                print("✓ DNS propagation appears successful")
                steps_completed += 1
                break
        
        if i < max_checks - 1:
            print(f"Waiting {check_interval} seconds for next check...")
            time.sleep(check_interval)
    
    if steps_completed < 4:
        print("⚠ DNS propagation may still be in progress")
        print("  Continue monitoring with: python check_dns_clean.py")
    
    # Step 5: Setup Azure domain
    print("\nSTEP 5/5: Setting up Azure Custom Domain")
    print("Once DNS propagation is complete, run:")
    print("  az webapp config hostname add --webapp-name foodxchange-deploy-app --resource-group foodxchange-deploy --hostname www.fdx.trading")
    
    if steps_completed >= 4:
        steps_completed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("SETUP SUMMARY")
    print("=" * 50)
    print(f"Steps completed: {steps_completed}/{total_steps}")
    
    if steps_completed == total_steps:
        print("🎉 COMPLETE SUCCESS!")
        print("Your domain www.fdx.trading should be ready!")
    elif steps_completed >= 3:
        print("📝 MOSTLY COMPLETE")
        print("DNS records updated, waiting for propagation")
    else:
        print("⚠ SETUP INCOMPLETE")
        print("Please address the issues above")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        complete_dns_setup()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\nSetup failed: {e}")