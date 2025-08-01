#!/usr/bin/env python3
"""Set all required DNS records for fdx.trading"""

import json
import os
import requests
import xml.etree.ElementTree as ET

def load_config():
    """Load Namecheap API configuration"""
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    with open(config_file, 'r') as f:
        return json.load(f)

def update_dns_records(config):
    """Update all DNS records"""
    base_url = "https://api.namecheap.com/xml.response"
    
    # Define all required records
    params = {
        'ApiUser': config['api_user'],
        'ApiKey': config['api_key'],
        'UserName': config['username'],
        'ClientIp': config['client_ip'],
        'Command': 'namecheap.domains.dns.setHosts',
        'SLD': 'fdx',
        'TLD': 'trading',
        # Root domain A record
        'HostName1': '@',
        'RecordType1': 'A',
        'Address1': '20.51.249.227',
        'TTL1': '1800',
        # WWW CNAME record
        'HostName2': 'www',
        'RecordType2': 'CNAME',
        'Address2': 'foodxchange-deploy-app.azurewebsites.net.',
        'TTL2': '1800',
        # ASUID TXT record for www
        'HostName3': 'asuid.www',
        'RecordType3': 'TXT',
        'Address3': '41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77',
        'TTL3': '1800'
    }
    
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

def main():
    """Main function"""
    print("FDX.TRADING DNS UPDATE - Set All Records")
    print("=" * 50)
    
    # Load config
    config = load_config()
    print("Config loaded successfully")
    
    # Update DNS records
    print("\nSetting all DNS records...")
    print("  - @ -> A -> 20.51.249.227")
    print("  - www -> CNAME -> foodxchange-deploy-app.azurewebsites.net.")
    print("  - asuid.www -> TXT -> 41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77")
    
    if update_dns_records(config):
        print("\nDNS records updated successfully!")
        
        # Verify the update
        print("\nVerifying update...")
        records = get_current_records(config)
        if records:
            print(f"Current DNS records ({len(records)} total):")
            for record in records:
                print(f"  {record['Name']}: {record['Type']} -> {record['Address']}")
    else:
        print("\nFailed to update DNS records")

if __name__ == "__main__":
    main()