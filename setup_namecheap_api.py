#!/usr/bin/env python3
"""
Namecheap API Setup Helper
Creates configuration file for API access
"""

import json
import os
import requests

def get_public_ip():
    """Get current public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        return '95.35.178.122'  # Fallback to detected IP

def create_config_template():
    """Create configuration template"""
    config_dir = os.path.expanduser('~/.namecheap-api')
    config_file = os.path.join(config_dir, 'config.json')
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    public_ip = get_public_ip()
    
    config_template = {
        "username": "YOUR_NAMECHEAP_USERNAME",
        "api_key": "YOUR_NAMECHEAP_API_KEY",
        "api_user": "YOUR_NAMECHEAP_USERNAME",
        "client_ip": public_ip
    }
    
    with open(config_file, 'w') as f:
        json.dump(config_template, f, indent=2)
    
    print("Namecheap API Configuration Setup")
    print("=" * 50)
    print(f"Public IP detected: {public_ip}")
    print(f"Config file created: {config_file}")
    print()
    print("STEPS TO COMPLETE SETUP:")
    print()
    print("1. Get your Namecheap API credentials:")
    print("   - Login to your Namecheap account")
    print("   - Go to Profile > Tools > Namecheap API access")
    print("   - Enable API access")
    print("   - Generate/copy your API key")
    print()
    print("2. Edit the config file and replace:")
    print("   - YOUR_NAMECHEAP_USERNAME: Your actual Namecheap username")
    print("   - YOUR_NAMECHEAP_API_KEY: Your actual API key")
    print()
    print("3. Then run: python update_dns.py")
    print()
    
    return config_file

if __name__ == "__main__":
    create_config_template()