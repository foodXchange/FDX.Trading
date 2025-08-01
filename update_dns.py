#!/usr/bin/env python3
"""
DNS Update Script for fdx.trading using Namecheap API
Python-based solution for updating DNS records
"""

import requests
import json
import os
from datetime import datetime

# DNS records that need to be set
REQUIRED_RECORDS = [
    {
        'type': 'CNAME',
        'name': 'www',
        'value': 'foodxchange-deploy-app.azurewebsites.net',
        'ttl': 1800
    },
    {
        'type': 'TXT', 
        'name': 'asuid.www',
        'value': '41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77',
        'ttl': 1800
    }
]

def get_public_ip():
    """Get current public IP address"""
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text.strip()
    except:
        print("Could not get public IP automatically")
        return input("Enter your public IP address: ")

def setup_config():
    """Setup Namecheap API configuration"""
    config_dir = os.path.expanduser('~/.namecheap-api')
    config_file = os.path.join(config_dir, 'config.json')
    
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    print("Setting up Namecheap API Configuration")
    print("=" * 50)
    
    # Get public IP
    public_ip = get_public_ip()
    print(f"Your public IP: {public_ip}")
    
    # Get credentials
    print("\nNamecheap API Setup:")
    print("1. Login to your Namecheap account")
    print("2. Go to Profile > Tools > Namecheap API access")
    print("3. Enable API access and get your API key")
    print()
    
    username = input("Enter your Namecheap username: ")
    api_key = input("Enter your Namecheap API key: ")
    
    config = {
        'username': username,
        'api_key': api_key,
        'api_user': username,
        'client_ip': public_ip
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\nConfiguration saved to: {config_file}")
    return config

def load_config():
    """Load Namecheap API configuration"""
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    
    if not os.path.exists(config_file):
        print("Configuration not found. Setting up...")
        return setup_config()
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except:
        print("Error reading config. Setting up again...")
        return setup_config()

def namecheap_api_call(command, params, config):
    """Make API call to Namecheap"""
    base_url = "https://api.namecheap.com/xml.response"
    
    # Base parameters
    api_params = {
        'ApiUser': config['api_user'],
        'ApiKey': config['api_key'],
        'UserName': config['username'],
        'ClientIp': config['client_ip'],
        'Command': command
    }
    
    # Add specific parameters
    api_params.update(params)
    
    try:
        response = requests.get(base_url, params=api_params, timeout=30)
        return response.text
    except Exception as e:
        print(f"API call failed: {e}")
        return None

def update_dns_records():
    """Update DNS records using Namecheap API"""
    print("Starting DNS update for fdx.trading...")
    print("=" * 50)
    
    config = load_config()
    domain = 'fdx.trading'
    
    print(f"Using account: {config['username']}")
    print(f"From IP: {config['client_ip']}")
    print()
    
    # Get current DNS records first
    print("1. Getting current DNS records...")
    get_params = {
        'SLD': 'fdx',
        'TLD': 'trading'
    }
    
    response = namecheap_api_call('namecheap.domains.dns.getHosts', get_params, config)
    if response:
        print("   Current records retrieved")
    else:
        print("   Failed to get current records")
        show_manual_instructions()
        return
    
    # Set DNS records
    print("\n2. Setting new DNS records...")
    
    # Prepare host records (you'll need to keep existing records too)
    set_params = {
        'SLD': 'fdx',
        'TLD': 'trading',
        'HostName1': 'www',
        'RecordType1': 'CNAME',
        'Address1': 'foodxchange-deploy-app.azurewebsites.net',
        'TTL1': '1800',
        'HostName2': 'asuid.www',
        'RecordType2': 'TXT',
        'Address2': '41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77',
        'TTL2': '1800'
    }
    
    response = namecheap_api_call('namecheap.domains.dns.setHosts', set_params, config)
    if response and 'CommandResponse' in response and 'IsSuccess="true"' in response:
        print("   SUCCESS: DNS records updated!")
        print("\n3. DNS propagation will take 5-60 minutes")
        print("   Monitor with: python check_dns_clean.py")
    else:
        print("   FAILED: Could not update DNS records")
        print("   Response:", response)
        show_manual_instructions()

def show_manual_instructions():
    """Show manual DNS setup instructions"""
    print("\n" + "=" * 50)
    print("MANUAL DNS SETUP REQUIRED")
    print("=" * 50)
    print("Login to your Namecheap account and add these records:")
    print()
    
    for i, record in enumerate(REQUIRED_RECORDS, 1):
        print(f"{i}. {record['type']} Record:")
        if record['type'] == 'CNAME':
            print(f"   Type: {record['type']}")
            print(f"   Host: {record['name']}")
            print(f"   Target: {record['value']}")
            print(f"   TTL: {record['ttl']}")
        else:
            print(f"   Type: {record['type']}")
            print(f"   Host: {record['name']}")
            print(f"   Value: {record['value']}")
            print(f"   TTL: {record['ttl']}")
        print()
    
    print("After updating:")
    print("• Wait 5-60 minutes for DNS propagation")  
    print("• Run: python check_dns_clean.py")
    print("• When both records show as correct, run the Azure domain setup")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--manual':
        show_manual_instructions()
    elif len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_config()
    else:
        try:
            update_dns_records()
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
        except Exception as e:
            print(f"Error: {e}")
            show_manual_instructions()