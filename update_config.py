#!/usr/bin/env python3
"""
Quick Config Updater for Namecheap API
Safely updates the configuration file
"""

import json
import os

def update_config():
    """Update the Namecheap API configuration"""
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    
    if not os.path.exists(config_file):
        print("❌ Config file not found!")
        print("Run: python setup_namecheap_api.py first")
        return
    
    try:
        # Load existing config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("Namecheap API Configuration Update")
        print("=" * 40)
        print(f"Current username: {config.get('username', 'Not set')}")
        print(f"Current IP: {config.get('client_ip', 'Not set')}")
        print()
        
        # Update username (we know it's 'Foodz')
        config['username'] = 'Foodz'
        config['api_user'] = 'Foodz'
        
        print("✅ Username set to: Foodz")
        print("✅ IP address already set to: 95.35.178.122")
        print()
        print("📋 Next steps:")
        print("1. Go to Namecheap → Profile → Tools → Namecheap API access")
        print("2. Enable API access and whitelist IP: 95.35.178.122") 
        print("3. Get your API key")
        print("4. Edit this file and replace YOUR_NAMECHEAP_API_KEY:")
        print(f"   {config_file}")
        print("5. Then run: python test_namecheap_api.py")
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        print(f"\n✅ Config updated at: {config_file}")
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")

if __name__ == "__main__":
    update_config()