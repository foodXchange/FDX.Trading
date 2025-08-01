#!/usr/bin/env python3
"""
Namecheap API Connection Tester (Clean version without unicode)
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
        print("ERROR: Config file not found!")
        print(f"   Expected: {config_file}")
        print("   Run: python setup_namecheap_api.py first")
        return None
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
            
        # Check if template values are still there
        if config.get('username') == 'YOUR_NAMECHEAP_USERNAME':
            print("ERROR: Config file not updated!")
            print("   Please edit the config file with your actual credentials")
            print(f"   File: {config_file}")
            return None
            
        if config.get('api_key') == 'YOUR_NAMECHEAP_API_KEY':
            print("ERROR: API key not set!")
            print("   Please add your actual API key to the config file")
            return None
            
        return config
        
    except Exception as e:
        print(f"ERROR reading config: {e}")
        return None

def test_api_connection(config):
    """Test basic API connectivity"""
    
    base_url = "https://api.namecheap.com/xml.response"
    
    params = {
        'ApiUser': config['api_user'],
        'ApiKey': config['api_key'],
        'UserName': config['username'],
        'ClientIp': config['client_ip'],
        'Command': 'namecheap.users.getbalances'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=30)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            
            api_response = root.find('.//ApiResponse')
            if api_response is not None and api_response.get('Status') == 'OK':
                return {'success': True, 'message': 'API Connection successful'}
            else:
                error_elem = root.find('.//Error')
                if error_elem is not None:
                    error_msg = error_elem.text
                    error_num = error_elem.get('Number', 'Unknown')
                    return {'success': False, 'message': f'API Error #{error_num}: {error_msg}'}
                else:
                    return {'success': False, 'message': 'API returned error status'}
        else:
            return {'success': False, 'message': f'HTTP Error: {response.status_code}'}
            
    except requests.exceptions.RequestException as e:
        return {'success': False, 'message': f'Connection Error: {e}'}
    except ET.ParseError as e:
        return {'success': False, 'message': f'XML Parse Error: {e}'}

def test_domain_access(config):
    """Test if we can access the domain"""
    
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
            
            api_response = root.find('.//ApiResponse')
            if api_response is not None and api_response.get('Status') == 'OK':
                
                domains = root.findall('.//Domain')
                domain_names = [d.get('Name') for d in domains]
                
                if 'fdx.trading' in domain_names:
                    return {'success': True, 'message': f'Found {len(domain_names)} domains, fdx.trading is accessible'}
                else:
                    return {'success': False, 'message': f'Found {len(domain_names)} domains, but fdx.trading not found in account'}
            else:
                return {'success': False, 'message': 'Could not retrieve domain list'}
        else:
            return {'success': False, 'message': f'HTTP Error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error checking domains: {e}'}

def test_dns_access(config):
    """Test if we can read current DNS records"""
    
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
            if api_response is not None and api_response.get('Status') == 'OK':
                
                hosts = root.findall('.//host')
                return {'success': True, 'message': f'DNS access successful, found {len(hosts)} DNS records'}
            else:
                error_elem = root.find('.//Error')
                if error_elem is not None:
                    error_msg = error_elem.text
                    return {'success': False, 'message': f'DNS Access Error: {error_msg}'}
                else:
                    return {'success': False, 'message': 'Could not read DNS records'}
        else:
            return {'success': False, 'message': f'HTTP Error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error reading DNS: {e}'}

def check_current_dns(config):
    """Check current DNS records in detail"""
    
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
            if api_response is not None and api_response.get('Status') == 'OK':
                
                hosts = root.findall('.//host')
                records_info = []
                
                for host in hosts:
                    name = host.get('Name', '')
                    record_type = host.get('Type', '')
                    address = host.get('Address', '')
                    records_info.append(f"{name}: {record_type} -> {address}")
                
                return {'success': True, 'message': f'Current DNS: {"; ".join(records_info)}'}
            else:
                return {'success': False, 'message': 'Could not read current DNS records'}
        else:
            return {'success': False, 'message': f'HTTP Error: {response.status_code}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error reading current DNS: {e}'}

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
    
    print(f"Config Loaded:")
    print(f"  Username: {config['username']}")
    print(f"  API User: {config['api_user']}")
    print(f"  Client IP: {config['client_ip']}")
    print(f"  API Key: ...{config['api_key'][-4:]}")
    print()
    
    # Run tests
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Basic API connection
    print("TEST 1: Basic API Connection")
    result = test_api_connection(config)
    if result['success']:
        print(f"PASS: {result['message']}")
        tests_passed += 1
    else:
        print(f"FAIL: {result['message']}")
        tests_failed += 1
    print()
    
    # Test 2: Domain list access
    print("TEST 2: Domain List Access")
    result = test_domain_access(config)
    if result['success']:
        print(f"PASS: {result['message']}")
        tests_passed += 1
    else:
        print(f"FAIL: {result['message']}")
        tests_failed += 1
    print()
    
    # Test 3: DNS records access
    print("TEST 3: DNS Records Access")
    result = test_dns_access(config)
    if result['success']:
        print(f"PASS: {result['message']}")
        tests_passed += 1
    else:
        print(f"FAIL: {result['message']}")
        tests_failed += 1
    print()
    
    # Test 4: Current DNS status
    print("TEST 4: Current DNS Status")
    result = check_current_dns(config)
    if result['success']:
        print(f"PASS: {result['message']}")
        tests_passed += 1
    else:
        print(f"FAIL: {result['message']}")
        tests_failed += 1
    
    # Results
    total_tests = tests_passed + tests_failed
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Tests Passed: {tests_passed}/{total_tests}")
    print(f"Tests Failed: {tests_failed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\nSUCCESS: ALL TESTS PASSED!")
        print("Ready to update DNS records")
        print("\nNext step: python update_dns.py")
        return True
    else:
        print("\nFAIL: Some tests failed")
        print("Please fix the issues above before updating DNS")
        return False

if __name__ == "__main__":
    try:
        run_full_test()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")