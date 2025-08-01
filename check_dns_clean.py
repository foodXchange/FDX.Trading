#!/usr/bin/env python3
"""
DNS Checker for fdx.trading Domain - Clean Version
"""

import requests
import time
from datetime import datetime

def check_dns_record(domain, record_type='A'):
    try:
        url = f"https://dns.google/resolve?name={domain}&type={record_type}"
        response = requests.get(url)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_domain_status():
    print(f"DNS Status Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check CNAME record
    print("1. Checking CNAME record for www.fdx.trading...")
    cname_result = check_dns_record('www.fdx.trading', 'CNAME')
    
    if 'Answer' in cname_result:
        cname_value = cname_result['Answer'][0]['data']
        print(f"   FOUND: {cname_value}")
        
        if cname_value == "foodxchange-deploy-app.azurewebsites.net.":
            print("   STATUS: CORRECT!")
        else:
            print("   STATUS: NEEDS UPDATE - should be 'foodxchange-deploy-app.azurewebsites.net'")
    else:
        print("   STATUS: MISSING - CNAME record not found")
    
    # Check TXT record
    print("\n2. Checking TXT record for domain verification...")
    txt_result = check_dns_record('asuid.www.fdx.trading', 'TXT')
    
    expected_txt = "41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77"
    
    if 'Answer' in txt_result:
        txt_value = txt_result['Answer'][0]['data'].strip('"')
        print(f"   FOUND: {txt_value}")
        
        if txt_value == expected_txt:
            print("   STATUS: CORRECT!")
        else:
            print(f"   STATUS: INCORRECT - Should be: {expected_txt}")
    else:
        print("   STATUS: MISSING - TXT record not found")
        print(f"   NEEDED: asuid.www = {expected_txt}")
    
    # Test website
    print("\n3. Testing website accessibility...")
    try:
        response = requests.get('https://www.fdx.trading', timeout=10)
        print(f"   RESULT: Website responds with status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   RESULT: Website not accessible - {e}")
    
    print("\n" + "=" * 60)
    return cname_result, txt_result

if __name__ == "__main__":
    check_domain_status()
    print("\nTo monitor continuously: python check_dns_clean.py")