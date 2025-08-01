#!/usr/bin/env python3
"""Add ASUID TXT record for root domain"""

import json
import os
import requests
import xml.etree.ElementTree as ET

def load_config():
    """Load Namecheap API configuration"""
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    with open(config_file, 'r') as f:
        return json.load(f)

def get_current_records(config):
    """Get current DNS records"""
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
    
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        if root.get('Status') == 'OK':
            hosts = []
            for host in root.findall('.//host'):
                hosts.append({
                    'Name': host.get('Name', ''),
                    'Type': host.get('Type', ''),
                    'Address': host.get('Address', ''),
                    'TTL': host.get('TTL', '1800')
                })
            return hosts
    return None

def update_dns_records(config, records):
    """Update DNS records"""
    base_url = "https://api.namecheap.com/xml.response"
    
    params = {
        'ApiUser': config['api_user'],
        'ApiKey': config['api_key'],
        'UserName': config['username'],
        'ClientIp': config['client_ip'],
        'Command': 'namecheap.domains.dns.setHosts',
        'SLD': 'fdx',
        'TLD': 'trading'
    }
    
    # Add record parameters
    for i, record in enumerate(records, 1):
        params[f'HostName{i}'] = record['Name']
        params[f'RecordType{i}'] = record['Type']
        params[f'Address{i}'] = record['Address']
        params[f'TTL{i}'] = record['TTL']
    
    response = requests.get(base_url, params=params, timeout=30)
    
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        if root.get('Status') == 'OK':
            return True
        else:
            error = root.find('.//Error')
            if error is not None:
                print(f"Error: {error.text}")
    return False

def main():
    """Main function"""
    print("Adding ASUID TXT record for root domain")
    print("=" * 50)
    
    # Load config
    config = load_config()
    
    # Get current records
    print("Getting current DNS records...")
    current_records = get_current_records(config)
    
    if current_records is None:
        print("Failed to get current DNS records")
        return
    
    print(f"Found {len(current_records)} existing records")
    
    # Add ASUID TXT record for root
    asuid_value = "41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77"
    
    # Check if ASUID already exists
    asuid_exists = any(r['Name'] == 'asuid' and r['Type'] == 'TXT' for r in current_records)
    
    if not asuid_exists:
        print(f"Adding asuid TXT record")
        current_records.append({
            'Name': 'asuid',
            'Type': 'TXT',
            'Address': asuid_value,
            'TTL': '1800'
        })
    
    # Update DNS records
    print("\nUpdating DNS records...")
    if update_dns_records(config, current_records):
        print("DNS records updated successfully!")
        
        # Show all records
        print("\nCurrent DNS records:")
        for record in current_records:
            print(f"  {record['Name']}: {record['Type']} -> {record['Address']}")
    else:
        print("Failed to update DNS records")

if __name__ == "__main__":
    main()