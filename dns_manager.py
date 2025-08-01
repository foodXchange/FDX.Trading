#!/usr/bin/env python3
"""
DNS Manager for fdx.trading
Simple menu-driven DNS management
"""

import subprocess
import sys
import os

def show_menu():
    """Display the main menu"""
    print("\n" + "=" * 60)
    print("DNS MANAGER FOR fdx.trading")
    print("=" * 60)
    print("1. Check current DNS status")
    print("2. Show manual DNS setup instructions")
    print("3. Setup Namecheap API (automated)")
    print("4. Update DNS records via API (automated)")
    print("5. Monitor DNS propagation")
    print("6. Exit")
    print("=" * 60)

def run_script(script_name, args=""):
    """Run a Python script"""
    try:
        cmd = f"python {script_name} {args}"
        result = subprocess.run(cmd, shell=True, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def check_dns_status():
    """Check current DNS status"""
    print("\nChecking DNS status...")
    return run_script("check_dns_clean.py")

def show_manual_setup():
    """Show manual setup instructions"""
    print("\nManual DNS Setup Instructions:")
    return run_script("update_dns.py", "--manual")

def setup_api():
    """Setup Namecheap API"""
    print("\nSetting up Namecheap API...")
    return run_script("update_dns.py", "--setup")

def update_via_api():
    """Update DNS via API"""
    print("\nUpdating DNS records via API...")
    return run_script("update_dns.py")

def monitor_dns():
    """Monitor DNS propagation"""
    print("\nStarting DNS monitoring...")
    print("Press Ctrl+C to stop monitoring")
    try:
        while True:
            if not run_script("check_dns_clean.py"):
                break
            import time
            print("\nWaiting 30 seconds for next check...")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

def main():
    """Main menu loop"""
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect an option (1-6): ").strip()
            
            if choice == '1':
                check_dns_status()
            elif choice == '2':
                show_manual_setup()
            elif choice == '3':
                setup_api()
            elif choice == '4':
                update_via_api()
            elif choice == '5':
                monitor_dns()
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()