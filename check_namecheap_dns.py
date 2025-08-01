#!/usr/bin/env python3
"""
Check what DNS records are actually set in Namecheap
"""

import json
import os
import requests
import xml.etree.ElementTree as ET

def check_namecheap_dns():
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("CURRENT DNS RECORDS IN NAMECHEAP")
    print("=" * 40)
    
    base_url = "https://api.namecheap.com/xml.response"
    
    params = {
        'ApiUser': config['api_user'],
        'ApiKey': config['api_key'],
        'UserName': config['username'],
        'ClientIp': config['client_ip'],
        'Command': 'namecheap.domains.dns.getHosts',
        'SLD': 'fdx',
        'TLD': 'trading'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            api_response = root.find('.//ApiResponse')
            status = api_response.get('Status') if api_response is not None else 'Unknown'
            print(f"API Status: {status}")
            
            if api_response is not None and api_response.get('Status') == 'OK':
                
                hosts = root.findall('.//host')
                
                print(f"Found {len(hosts)} DNS records:")
                print()
                
                for host in hosts:
                    name = host.get('Name', '')
                    record_type = host.get('Type', '')
                    address = host.get('Address', '')
                    ttl = host.get('TTL', '')
                    
                    print(f"Name: {name}")
                    print(f"Type: {record_type}")
                    print(f"Value: {address}")
                    print(f"TTL: {ttl}")
                    print("-" * 20)
                
                # Check for our specific records
                print("CHECKING FOR REQUIRED RECORDS:")
                print()
                
                found_cname = False
                found_txt = False
                
                for host in hosts:
                    name = host.get('Name', '')
                    record_type = host.get('Type', '')
                    address = host.get('Address', '')
                    
                    if name == 'www' and record_type == 'CNAME':
                        if address == 'foodxchange-deploy-app.azurewebsites.net':
                            print("✓ CNAME record is correct")
                            found_cname = True
                        else:
                            print(f"✗ CNAME record is wrong: {address}")
                    
                    if name == 'asuid.www' and record_type == 'TXT':
                        expected = '41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77'
                        if address == expected:
                            print("✓ TXT record is correct")
                            found_txt = True
                        else:
                            print(f"✗ TXT record is wrong: {address}")
                
                if not found_cname:
                    print("✗ CNAME record not found")
                    
                if not found_txt:
                    print("✗ TXT record not found")
                    
            else:
                print("API Response Status: ERROR")
                print("Raw response:")
                print(response.text)
                errors = root.findall('.//Error')
                for error in errors:
                    error_num = error.get('Number', 'Unknown')
                    error_msg = error.text
                    print(f"API Error #{error_num}: {error_msg}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_namecheap_dns()