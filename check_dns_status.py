#!/usr/bin/env python3
"""Check DNS propagation status for fdx.trading"""

import socket
import subprocess
import time
from datetime import datetime

def check_dns_resolution(hostname):
    """Check if hostname resolves"""
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return None

def check_nslookup(hostname):
    """Use nslookup to check DNS"""
    try:
        result = subprocess.run(['nslookup', hostname], capture_output=True, text=True)
        return result.stdout
    except:
        return None

def main():
    """Check DNS status"""
    print("DNS PROPAGATION STATUS CHECK")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    domains = ['fdx.trading', 'www.fdx.trading']
    expected_ips = {
        'fdx.trading': '20.51.249.227',
        'www.fdx.trading': 'foodxchange-deploy-app.azurewebsites.net'
    }
    
    all_good = True
    
    for domain in domains:
        print(f"Checking {domain}:")
        
        # Python socket resolution
        ip = check_dns_resolution(domain)
        if ip:
            print(f"  [OK] Resolves to: {ip}")
            if domain == 'fdx.trading' and ip != expected_ips[domain]:
                print(f"  ! Expected: {expected_ips[domain]}")
                all_good = False
        else:
            print(f"  [X] Not resolving yet")
            all_good = False
        
        # nslookup details
        nslookup = check_nslookup(domain)
        if nslookup and 'can\'t find' not in nslookup:
            lines = nslookup.split('\n')
            for line in lines:
                if 'Address:' in line and not 'Server:' in lines[lines.index(line)-1]:
                    print(f"  nslookup: {line.strip()}")
        
        print()
    
    if all_good:
        print("DNS PROPAGATION COMPLETE!")
        print("You can now add the custom domain in Azure App Service")
    else:
        print("DNS is still propagating...")
        print("Check again in a few minutes")
        print()
        print("You can also check online:")
        print("- https://dnschecker.org/#A/fdx.trading")
        print("- https://whatsmydns.net/#A/fdx.trading")

if __name__ == "__main__":
    main()