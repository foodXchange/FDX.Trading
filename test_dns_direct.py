#!/usr/bin/env python3
"""Test direct DNS access for fdx.trading"""

import json
import os
import requests
import xml.etree.ElementTree as ET

def load_config():
    """Load Namecheap API configuration"""
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    with open(config_file, 'r') as f:
        return json.load(f)

def test_direct_dns():
    """Test direct DNS access for fdx.trading"""
    config = load_config()
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
    
    print("Testing direct DNS access for fdx.trading...")
    response = requests.get(base_url, params=params, timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response:\n{response.text}")
    
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        if root.get('Status') == 'OK':
            hosts = root.findall('.//host')
            print(f"\nFound {len(hosts)} DNS records")
            for host in hosts:
                name = host.get('Name', '')
                record_type = host.get('Type', '')
                address = host.get('Address', '')
                print(f"  {name}: {record_type} -> {address}")

if __name__ == "__main__":
    test_direct_dns()