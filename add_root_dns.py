#!/usr/bin/env python3
"""Add root domain A record to fdx.trading"""

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
    print("FDX.TRADING DNS UPDATE - Add Root A Record")
    print("=" * 50)
    
    # Load config
    config = load_config()
    print("Config loaded successfully")
    
    # Get current records
    print("\nGetting current DNS records...")
    current_records = get_current_records(config)
    
    if current_records is None:
        print("Failed to get current DNS records")
        return
    
    print(f"Found {len(current_records)} existing records:")
    for record in current_records:
        print(f"  {record['Name']}: {record['Type']} -> {record['Address']}")
    
    # Add root domain A record
    azure_ip = "20.51.249.227"
    
    # Check if root A record already exists
    root_exists = any(r['Name'] == '@' and r['Type'] == 'A' for r in current_records)
    
    if not root_exists:
        print(f"\nAdding root domain A record -> {azure_ip}")
        current_records.append({
            'Name': '@',
            'Type': 'A',
            'Address': azure_ip,
            'TTL': '1800'
        })
    else:
        print(f"\nRoot A record already exists")
        # Update existing record
        for record in current_records:
            if record['Name'] == '@' and record['Type'] == 'A':
                print(f"Updating existing A record from {record['Address']} to {azure_ip}")
                record['Address'] = azure_ip
    
    # Update DNS records
    print("\nUpdating DNS records...")
    if update_dns_records(config, current_records):
        print("DNS records updated successfully!")
        
        # Verify the update
        print("\nVerifying update...")
        new_records = get_current_records(config)
        if new_records:
            print(f"Current DNS records ({len(new_records)} total):")
            for record in new_records:
                print(f"  {record['Name']}: {record['Type']} -> {record['Address']}")
    else:
        print("Failed to update DNS records")

if __name__ == "__main__":
    main()