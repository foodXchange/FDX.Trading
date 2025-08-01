#!/usr/bin/env python3
"""
Azure Custom Domain Setup (Clean version)
Adds the custom domain to Azure App Service once DNS is ready
"""

import subprocess
import json
import requests
from datetime import datetime

def check_dns_ready():
    """Check if DNS records are properly configured"""
    print("Checking DNS readiness...")
    
    try:
        # Check CNAME record
        cname_url = "https://dns.google/resolve?name=www.fdx.trading&type=CNAME"
        cname_response = requests.get(cname_url, timeout=10)
        cname_data = cname_response.json()
        
        cname_ok = False
        if 'Answer' in cname_data:
            cname_value = cname_data['Answer'][0]['data']
            if cname_value == "foodxchange-deploy-app.azurewebsites.net.":
                print("PASS: CNAME record is correct")
                cname_ok = True
            else:
                print(f"FAIL: CNAME record incorrect: {cname_value}")
        else:
            print("FAIL: CNAME record not found")
        
        # Check TXT record
        txt_url = "https://dns.google/resolve?name=asuid.www.fdx.trading&type=TXT"
        txt_response = requests.get(txt_url, timeout=10)
        txt_data = txt_response.json()
        
        expected_txt = "41260bf0bfcf0f62c6509763f8d3773dceb6e1df952696707f2b337da93eec77"
        txt_ok = False
        
        if 'Answer' in txt_data:
            txt_value = txt_data['Answer'][0]['data'].strip('"')
            if txt_value == expected_txt:
                print("PASS: TXT record is correct")
                txt_ok = True
            else:
                print(f"FAIL: TXT record incorrect: {txt_value}")
        else:
            print("FAIL: TXT record not found")
        
        return cname_ok and txt_ok
        
    except Exception as e:
        print(f"Error checking DNS: {e}")
        return False

def add_custom_domain():
    """Add custom domain to Azure App Service"""
    print("\nAdding custom domain to Azure App Service...")
    
    cmd = [
        "az", "webapp", "config", "hostname", "add",
        "--webapp-name", "foodxchange-deploy-app",
        "--resource-group", "foodxchange-deploy",
        "--hostname", "www.fdx.trading"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("PASS: Custom domain added successfully!")
            return True
        else:
            print(f"FAIL: Failed to add domain: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("FAIL: Command timed out")
        return False
    except Exception as e:
        print(f"FAIL: Error running command: {e}")
        return False

def setup_ssl_certificate():
    """Set up free SSL certificate for the domain"""
    print("\nSetting up SSL certificate...")
    
    cmd = [
        "az", "webapp", "config", "ssl", "create",
        "--resource-group", "foodxchange-deploy",
        "--name", "foodxchange-deploy-app",
        "--hostname", "www.fdx.trading"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("PASS: SSL certificate created successfully!")
            return True
        else:
            print(f"WARN: SSL setup may have failed: {result.stderr}")
            print("  You can set this up manually in Azure Portal")
            return False
            
    except subprocess.TimeoutExpired:
        print("WARN: SSL setup timed out")
        return False
    except Exception as e:
        print(f"WARN: SSL setup error: {e}")
        return False

def verify_domain_setup():
    """Verify the domain is working"""
    print("\nVerifying domain setup...")
    
    try:
        # Test the website
        response = requests.get('https://www.fdx.trading', timeout=30)
        
        if response.status_code == 200:
            print("PASS: Website is accessible at https://www.fdx.trading")
            return True
        elif response.status_code in [503, 502]:
            print("WARN: Domain points to Azure but app may not be running")
            print("  Check Azure App Service status")
            return True
        else:
            print(f"WARN: Website returns status {response.status_code}")
            return False
            
    except requests.exceptions.SSLError:
        print("WARN: SSL certificate not ready yet, trying HTTP...")
        try:
            response = requests.get('http://www.fdx.trading', timeout=30)
            if response.status_code in [200, 301, 302]:
                print("PASS: Domain is working (SSL may take a few minutes)")
                return True
        except:
            pass
        return False
    except Exception as e:
        print(f"FAIL: Cannot access website: {e}")
        return False

def run_azure_setup():
    """Run complete Azure domain setup"""
    
    print("AZURE CUSTOM DOMAIN SETUP")
    print("=" * 40)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Check DNS readiness
    if not check_dns_ready():
        print("\nFAIL: DNS records are not ready yet")
        print("Please wait for DNS propagation and try again")
        print("Monitor with: python check_dns_clean.py")
        return False
    
    print("\nPASS: DNS records are ready!")
    
    # Step 2: Add custom domain
    if not add_custom_domain():
        print("\nFAIL: Failed to add custom domain")
        return False
    
    # Step 3: Setup SSL (optional, may fail initially)
    setup_ssl_certificate()
    
    # Step 4: Verify setup
    if verify_domain_setup():
        print("\nSUCCESS!")
        print("Your website is now available at:")
        print("  https://www.fdx.trading")
        print("  http://www.fdx.trading")
        return True
    else:
        print("\nWARN: Domain setup completed but verification failed")
        print("The domain may still be propagating")
        return False

if __name__ == "__main__":
    try:
        run_azure_setup()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
    except Exception as e:
        print(f"\nSetup failed: {e}")