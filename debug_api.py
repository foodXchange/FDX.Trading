#!/usr/bin/env python3
"""
Debug Namecheap API Connection
Shows detailed error messages to help troubleshoot
"""

import json
import os
import requests
import xml.etree.ElementTree as ET

def debug_api():
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("DEBUG: Namecheap API Connection")
    print("=" * 40)
    print(f"Username: {config['username']}")
    print(f"API User: {config['api_user']}")
    print(f"Client IP: {config['client_ip']}")
    print(f"API Key: {config['api_key'][:8]}...{config['api_key'][-4:]}")
    print()
    
    base_url = "https://api.namecheap.com/xml.response"
    
    params = {
        'ApiUser': config['api_user'],
        'ApiKey': config['api_key'],
        'UserName': config['username'],
        'ClientIp': config['client_ip'],
        'Command': 'namecheap.users.getbalances'
    }
    
    print("Making API request...")
    print(f"URL: {base_url}")
    print("Parameters:")
    for key, value in params.items():
        if key == 'ApiKey':
            print(f"  {key}: {value[:8]}...{value[-4:]}")
        else:
            print(f"  {key}: {value}")
    print()
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        
        print(f"HTTP Status: {response.status_code}")
        print("Response content:")
        print("-" * 40)
        print(response.text)
        print("-" * 40)
        
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.text)
                
                # Check API response status
                api_response = root.find('.//ApiResponse')
                if api_response is not None:
                    status = api_response.get('Status')
                    print(f"\nAPI Response Status: {status}")
                    
                    if status != 'OK':
                        # Find all errors
                        errors = root.findall('.//Error')
                        print(f"Found {len(errors)} error(s):")
                        for i, error in enumerate(errors, 1):
                            error_num = error.get('Number', 'Unknown')
                            error_msg = error.text
                            print(f"  Error {i}: #{error_num} - {error_msg}")
                    else:
                        print("API call successful!")
                        
            except ET.ParseError as e:
                print(f"XML Parse Error: {e}")
                
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_api()