"""
Check your public IP address
"""
import requests
import socket

def check_ip():
    """Check public IP from multiple sources"""
    
    print("Checking your public IP address...\n")
    
    # Method 1: Using ipify
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip1 = response.json()['ip']
        print(f"IP from ipify.org: {ip1}")
    except Exception as e:
        print(f"ipify.org failed: {e}")
        ip1 = None
    
    # Method 2: Using ipinfo
    try:
        response = requests.get('https://ipinfo.io/ip', timeout=5)
        ip2 = response.text.strip()
        print(f"IP from ipinfo.io: {ip2}")
    except Exception as e:
        print(f"ipinfo.io failed: {e}")
        ip2 = None
    
    # Method 3: Using ifconfig.me
    try:
        response = requests.get('https://ifconfig.me/ip', timeout=5)
        ip3 = response.text.strip()
        print(f"IP from ifconfig.me: {ip3}")
    except Exception as e:
        print(f"ifconfig.me failed: {e}")
        ip3 = None
    
    # Check if all match
    ips = [ip for ip in [ip1, ip2, ip3] if ip]
    if ips:
        if len(set(ips)) == 1:
            print(f"\nYour public IP address is: {ips[0]}")
            print("\nThis IP should be added to Azure PostgreSQL firewall rules.")
        else:
            print(f"\nDifferent IPs detected: {set(ips)}")
            print("You might be behind a proxy or load balancer.")
    
    # Check local hostname
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"\nLocal hostname: {hostname}")
        print(f"Local IP: {local_ip}")
    except Exception as e:
        print(f"Could not get local info: {e}")

if __name__ == "__main__":
    check_ip()