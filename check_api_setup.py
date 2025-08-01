#!/usr/bin/env python3
"""
Simple API Setup Checker
"""

import json
import os

def check_setup():
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    
    print("NAMECHEAP API SETUP STATUS")
    print("=" * 40)
    
    if not os.path.exists(config_file):
        print("ERROR: Config file not found")
        return
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("Configuration Status:")
        print(f"  Username: {config.get('username', 'NOT SET')}")
        print(f"  Client IP: {config.get('client_ip', 'NOT SET')}")
        
        api_key = config.get('api_key', '')
        if api_key == 'YOUR_NAMECHEAP_API_KEY':
            print("  API Key: NOT SET (placeholder)")
            print()
            print("NEXT STEPS:")
            print("1. Login to Namecheap account (username: Foodz)")
            print("2. Go to: Profile > Tools > Namecheap API access") 
            print("3. Enable API access")
            print("4. Whitelist IP: 95.35.178.122")
            print("5. Get/generate your API key")
            print("6. Edit this file:")
            print(f"   {config_file}")
            print("7. Replace 'YOUR_NAMECHEAP_API_KEY' with actual key")
            print("8. Run: python test_namecheap_api.py")
        else:
            print(f"  API Key: SET (ending in ...{api_key[-4:]})")
            print()
            print("READY TO TEST!")
            print("Run: python test_namecheap_api.py")
            
    except Exception as e:
        print(f"ERROR reading config: {e}")

if __name__ == "__main__":
    check_setup()