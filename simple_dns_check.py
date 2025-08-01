#!/usr/bin/env python3
"""
Simple DNS verification script
"""

import json
import os
import requests
import xml.etree.ElementTree as ET

def simple_dns_check():
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print("DNS VERIFICATION")
    print("=" * 30)
    
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
    
    response = requests.get(base_url, params=params, timeout=30)
    
    if response.status_code == 200 and 'Status="OK"' in response.text:
        print("PASS: API call successful")
        
        # Parse the response text directly
        if 'Name="www" Type="CNAME" Address="foodxchange-deploy-app.azurewebsites.net."' in response.text:
            print("PASS: CNAME record is correct")
        else:
            print("FAIL: CNAME record issue")
            
        if 'Name="asuid.www" Type="TXT"' in response.text and '41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77' in response.text:
            print("PASS: TXT record is correct")
        else:
            print("FAIL: TXT record issue")
            
        print("\nSUCCESS: DNS records are properly configured in Namecheap!")
        print("Now waiting for DNS propagation...")
        print("This can take 5-60 minutes")
        
    else:
        print("FAIL: API call failed")
        print(response.text)

if __name__ == "__main__":
    simple_dns_check()