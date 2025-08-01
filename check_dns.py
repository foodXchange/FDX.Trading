#!/usr/bin/env python3
"""
DNS Checker for fdx.trading Domain
Monitors DNS propagation and Azure domain setup
"""

import requests
import time
import json
from datetime import datetime

def check_dns_record(domain, record_type='A'):
    """Check DNS record using Google DNS API"""
    try:
        url = f"https://dns.google/resolve?name={domain}&type={record_type}"
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        return {"error": str(e)}

def check_domain_status():
    """Check current DNS status for fdx.trading"""
    print(f"DNS Status Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check CNAME record
    print("1. Checking CNAME record for www.fdx.trading...")
    cname_result = check_dns_record('www.fdx.trading', 'CNAME')
    
    if 'Answer' in cname_result:
        cname_value = cname_result['Answer'][0]['data']
        print(f"   [OK] CNAME found: {cname_value}")
        
        if cname_value == "foodxchange-deploy-app.azurewebsites.net.":
            print("   [OK] CNAME is correct!")
        else:
            print(f"   [NEEDS UPDATE] CNAME should be 'foodxchange-deploy-app.azurewebsites.net'")
    else:
        print("   [MISSING] CNAME record not found")
    
    # Check TXT record
    print("\n2. Checking TXT record for domain verification...")
    txt_result = check_dns_record('asuid.www.fdx.trading', 'TXT')
    
    expected_txt = "41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77"
    
    if 'Answer' in txt_result:
        txt_value = txt_result['Answer'][0]['data'].strip('"')
        print(f"   [OK] TXT record found: {txt_value}")
        
        if txt_value == expected_txt:
            print("   [OK] TXT record is correct!")
        else:
            print(f"   [OK] TXT record incorrect. Should be: {expected_txt}")
    else:
        print("   [OK] TXT record not found")
        print(f"   [OK]ù Need to add: asuid.www = {expected_txt}")
    
    # Test website accessibility
    print("\n3. Testing website accessibility...")
    try:
        response = requests.get('https://www.fdx.trading', timeout=10)
        print(f"   [OK] Website responds with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   [OK] Website not accessible: {e}")
    
    print("\n" + "=" * 60)
    return cname_result, txt_result

def monitor_dns(interval=30, max_checks=20):
    """Monitor DNS propagation"""
    print("[OK]Ä Starting DNS monitoring...")
    print("Press Ctrl+C to stop\n")
    
    for i in range(max_checks):
        try:
            cname_result, txt_result = check_domain_status()
            
            # Check if both records are correct
            cname_ok = ('Answer' in cname_result and 
                       cname_result['Answer'][0]['data'] == "foodxchange-deploy-app.azurewebsites.net.")
            
            txt_ok = ('Answer' in txt_result and 
                     txt_result['Answer'][0]['data'].strip('"') == "41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77")
            
            if cname_ok and txt_ok:
                print("[OK]â All DNS records are correctly configured!")
                print("[OK] Ready to add custom domain to Azure!")
                break
            
            if i < max_checks - 1:
                print(f"[OK] Waiting {interval} seconds for next check... ({i+1}/{max_checks})")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n[OK]ã Monitoring stopped by user")
            break
        except Exception as e:
            print(f"[OK] Error during check: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_dns()
    else:
        check_domain_status()
        print("\n[OK]° To monitor continuously, run: python check_dns.py monitor")