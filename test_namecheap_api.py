#!/usr/bin/env python3
"""
Namecheap API Connection Tester
Tests API credentials and connectivity before making DNS changes
"""

import json
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

def load_config():
    """Load Namecheap API configuration"""
    config_file = os.path.expanduser('~/.namecheap-api/config.json')
    
    if not os.path.exists(config_file):
        print("X Config file not found!")
        print(f"   Expected: {config_file}")
        print("   Run: python setup_namecheap_api.py first")
        return None
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        # Check if template values are still there
        if config.get('username') == 'YOUR_NAMECHEAP_USERNAME':
            print("X Config file not updated!")
            print("   Please edit the config file with your actual credentials")
            print(f"   File: {config_file}")
            return None
            
        if config.get('api_key') == 'YOUR_NAMECHEAP_API_KEY':
            print("X API key not set!")
            print("   Please add your actual API key to the config file")
            return None
            
        return config
        
    except Exception as e:
        print(f"X Error reading config: {e}")
        return None

def test_api_connection(config):
    """Test basic API connectivity"""
    print("Testing API Connection...")
    
    base_url = "https://api.namecheap.com/xml.response"
    
    params = {
        'ApiUser': config['api_user'],
        'ApiKey': config['api_key'],
        'UserName': config['username'],
        'ClientIp': config['client_ip'],
        'Command': 'namecheap.users.getbalances'  # Simple test command
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            # Parse XML response
            root = ET.fromstring(response.text)
            
            # Check for API errors
            if root.get('Status') == 'OK':
                print("OK API Connection: SUCCESS")
                
                # Try to get account balance as additional verification
                try:
                    balance = root.find('.//AccountBalance').text
                    print(f"   Account Balance: ${balance}")
                except:
                    print("   (Could not retrieve balance, but connection works)")
                
                return True
            else:
                # Find error details
                error_elem = root.find('.//Error')
                if error_elem is not None:
                    error_msg = error_elem.text
                    error_num = error_elem.get('Number', 'Unknown')
                    print(f"X API Error #{error_num}: {error_msg}")
                else:
                    print("X API returned error status")
                    print(f"   Raw response: {response.text[:500]}")
                return False
        else:
            print(f"X HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"X Connection Error: {e}")
        return False
    except ET.ParseError as e:
        print(f"X XML Parse Error: {e}")
        return False

def test_domain_access(config):
    """Test if we can access the domain"""
    print("\nTesting Domain Access...")
    
    base_url = "https://api.namecheap.com/xml.response"
    
    params = {
        'ApiUser': config['api_user'],
        'ApiKey': config['api_key'],
        'UserName': config['username'],
        'ClientIp': config['client_ip'],
        'Command': 'namecheap.domains.getList'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            if root.get('Status') == 'OK':
                
                # Find all domains
                domains = root.findall('.//Domain')
                domain_names = [d.get('Name') for d in domains]
                
                print(f"OK Found {len(domain_names)} domain(s) in account:")
                for domain in domain_names:
                    print(f"   - {domain}")
                
                if 'fdx.trading' in domain_names:
                    print("OK fdx.trading: FOUND in account!")
                    return True
                else:
                    print("X fdx.trading: NOT FOUND in account")
                    print("   Make sure the domain is in the same account as your API key")
                    return False
            else:
                print("X Could not retrieve domain list")
                return False
        else:
            print(f"X HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"X Error checking domains: {e}")
        return False

def test_dns_permissions(config):
    """Test if we can read current DNS records"""
    print("\nTesting DNS Read Permissions...")
    
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
            
            if root.get('Status') == 'OK':
                
                # Find DNS hosts
                hosts = root.findall('.//host')
                
                print(f"OK DNS Read Access: SUCCESS")
                print(f"   Found {len(hosts)} DNS record(s):")
                
                for host in hosts:
                    name = host.get('Name', '')
                    record_type = host.get('Type', '')
                    address = host.get('Address', '')
                    print(f"   - {name}: {record_type} → {address}")
                
                return True
            else:
                error_elem = root.find('.//Error')
                if error_elem is not None:
                    error_msg = error_elem.text
                    print(f"X DNS Access Error: {error_msg}")
                else:
                    print("X Could not read DNS records")
                return False
        else:
            print(f"X HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"X Error reading DNS: {e}")
        return False

def run_full_test():
    """Run complete API test suite"""
    print("NAMECHEAP API CONNECTION TEST")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Load configuration
    config = load_config()
    if not config:
        return False
    
    print(f"OK Config Loaded:")
    print(f"   Username: {config['username']}")
    print(f"   Client IP: {config['client_ip']}")
    print(f"   API Key: {'*' * (len(config['api_key']) - 4)}{config['api_key'][-4:]}")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_api_connection(config):
        tests_passed += 1
    
    if test_domain_access(config):
        tests_passed += 1
        
    if test_dns_permissions(config):
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("ALL TESTS PASSED!")
        print("OK Ready to update DNS records")
        print("\nNext step: python update_dns.py")
        return True
    else:
        print("X Some tests failed")
        print("! Please fix the issues above before updating DNS")
        return False

if __name__ == "__main__":
    try:
        run_full_test()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\nX Test failed with error: {e}")