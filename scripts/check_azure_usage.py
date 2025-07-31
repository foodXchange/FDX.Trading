#!/usr/bin/env python3
"""
Azure Resource Monitor for FoodXchange
Monitors usage, costs, and health of Azure resources
"""

import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any

# Fix Unicode output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def run_az_command(command: str) -> Dict[str, Any]:
    """Run Azure CLI command and return JSON output"""
    try:
        result = subprocess.run(
            f"az {command} --output json",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return json.loads(result.stdout) if result.stdout else {}
        else:
            print(f"Error: {result.stderr}")
            return {}
    except Exception as e:
        print(f"Command failed: {e}")
        return {}

def check_openai_usage():
    """Check OpenAI service usage and limits"""
    print("\n🤖 OpenAI Service Status")
    print("=" * 50)
    
    # Get OpenAI account details
    account = run_az_command(
        'cognitiveservices account show --name "foodxchangeopenai" '
        '--resource-group "foodxchange-rg"'
    )
    
    if account:
        print(f"✅ Service: {account.get('name')}")
        print(f"✅ Status: {account.get('properties', {}).get('provisioningState', 'Unknown')}")
        print(f"✅ Endpoint: {account.get('properties', {}).get('endpoint', 'Not set')}")
        print(f"✅ SKU: {account.get('sku', {}).get('name', 'Unknown')}")
        
        # Show limits for free tier
        if account.get('sku', {}).get('name') == 'S0':
            print("\n📊 Free Tier Limits:")
            print("  - Tokens: 240,000 per minute")
            print("  - Requests: 3 per minute")
            print("  - Total: 1M tokens per month")

def check_storage_usage():
    """Check storage account usage"""
    print("\n💾 Storage Accounts")
    print("=" * 50)
    
    storage_accounts = run_az_command(
        'storage account list --resource-group "foodxchange-rg"'
    )
    
    for account in storage_accounts:
        print(f"\n📦 {account.get('name')}")
        print(f"  - Location: {account.get('location')}")
        print(f"  - SKU: {account.get('sku', {}).get('name')}")
        print(f"  - Kind: {account.get('kind')}")

def check_cognitive_services():
    """Check all cognitive services"""
    print("\n🧠 Cognitive Services")
    print("=" * 50)
    
    services = run_az_command(
        'cognitiveservices account list --resource-group "foodxchange-rg"'
    )
    
    for service in services:
        print(f"\n🔹 {service.get('name')}")
        print(f"  - Type: {service.get('kind')}")
        print(f"  - Location: {service.get('location')}")
        print(f"  - SKU: {service.get('sku', {}).get('name')}")

def check_costs():
    """Check estimated costs for current month"""
    print("\n💰 Cost Analysis (Current Month)")
    print("=" * 50)
    
    # Note: Cost data may have 24-48 hour delay
    print("⏳ Note: Cost data typically has a 24-48 hour delay")
    print("\nFor real-time cost monitoring:")
    print("1. Visit: https://portal.azure.com/#blade/Microsoft_Azure_CostManagement/Menu/overview")
    print("2. Select your subscription")
    print("3. Filter by resource group: foodxchange-rg")

def check_alerts():
    """Check configured alerts"""
    print("\n🚨 Configured Alerts")
    print("=" * 50)
    
    alerts = run_az_command(
        'monitor metrics alert list --resource-group "foodxchange-rg"'
    )
    
    if alerts:
        for alert in alerts:
            print(f"\n📢 {alert.get('name')}")
            print(f"  - Enabled: {alert.get('enabled')}")
            print(f"  - Severity: {alert.get('severity')}")
    else:
        print("No alerts configured")

def show_monitoring_tips():
    """Show monitoring best practices"""
    print("\n💡 Monitoring Best Practices")
    print("=" * 50)
    print("\n1. **Cost Monitoring:**")
    print("   - Set up budget alerts in Azure Portal")
    print("   - Monitor daily to avoid surprises")
    print("   - Free tier limits: Stay within to avoid charges")
    
    print("\n2. **Performance Monitoring:**")
    print("   - Check API response times")
    print("   - Monitor error rates")
    print("   - Set up Application Insights")
    
    print("\n3. **Security Monitoring:**")
    print("   - Enable Azure Security Center")
    print("   - Monitor access logs")
    print("   - Rotate API keys regularly")
    
    print("\n4. **Useful Azure Portal Links:**")
    print("   - Cost Management: https://portal.azure.com/#blade/Microsoft_Azure_CostManagement/Menu/overview")
    print("   - Monitor Dashboard: https://portal.azure.com/#blade/Microsoft_Azure_Monitoring/AzureMonitoringBrowseBlade/overview")
    print("   - Resource Group: https://portal.azure.com/#@/resource/subscriptions/88931ed0-52df-42fb-a09c-e024c9586f8a/resourceGroups/foodxchange-rg/overview")

def main():
    print("🔍 FoodXchange Azure Resource Monitor")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if logged in
    account = run_az_command("account show")
    if not account:
        print("❌ Not logged in to Azure CLI. Run: az login")
        return
    
    print(f"✅ Subscription: {account.get('name')}")
    print(f"✅ Tenant: {account.get('tenantDisplayName')}")
    
    # Run all checks
    check_openai_usage()
    check_cognitive_services()
    check_storage_usage()
    check_costs()
    check_alerts()
    show_monitoring_tips()
    
    print("\n✅ Monitoring check complete!")

if __name__ == "__main__":
    main()