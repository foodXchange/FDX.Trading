#!/usr/bin/env python3
"""
Deploy Optimized Search System to Production VM
Handles complex 1-to-many product relationships
"""

import subprocess
import os

def deploy_to_vm():
    """Deploy all search optimization files to production"""
    
    vm_host = "azureuser@4.206.1.15"
    app_dir = "/home/fdxfounder/fdx/app"
    
    # Files to deploy
    files_to_deploy = [
        "optimize_product_search.py",
        "enhance_supplier_data.py", 
        "openai_search.py",
        "advanced_search_system.py",
        "app_with_optimizer.py"
    ]
    
    print("Deploying Optimized Search System to Production")
    print("=" * 60)
    
    # Copy each file
    for file in files_to_deploy:
        if os.path.exists(file):
            print(f"Deploying {file}...")
            cmd = f'scp {file} {vm_host}:{app_dir}/'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"SUCCESS: {file} deployed successfully")
            else:
                print(f"ERROR: Failed to deploy {file}: {result.stderr}")
        else:
            print(f"WARNING: {file} not found locally")
    
    print("\nSetting up database optimizations on VM...")
    
    # Run database setup commands
    setup_commands = [
        # Add product classification column
        """python3 -c "
from optimize_product_search import ProductSearchOptimizer
optimizer = ProductSearchOptimizer()
optimizer.add_product_classification_column()
print('Added product classification column')
"
        """,
        
        # Add enhanced data columns
        """python3 -c "
from enhance_supplier_data import SupplierDataEnhancer
enhancer = SupplierDataEnhancer()
enhancer.setup_enhanced_columns()
print('Added enhanced data columns')
"
        """
    ]
    
    for cmd in setup_commands:
        ssh_cmd = f'ssh {vm_host} "cd {app_dir} && {cmd}"'
        result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
    
    print("\nBacking up current app.py...")
    backup_cmd = f'ssh {vm_host} "cd {app_dir} && cp app.py app_backup_$(date +%Y%m%d_%H%M%S).py"'
    subprocess.run(backup_cmd, shell=True)
    
    print("\nActivating optimized search...")
    activate_cmd = f'ssh {vm_host} "cd {app_dir} && cp app_with_optimizer.py app.py"'
    result = subprocess.run(activate_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("SUCCESS: Optimized search activated")
    else:
        print(f"ERROR: Failed to activate: {result.stderr}")
    
    print("\nRestarting application...")
    restart_cmd = f'ssh {vm_host} "sudo systemctl restart fdx-app"'
    result = subprocess.run(restart_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("SUCCESS: Application restarted successfully")
    else:
        print(f"WARNING: Restart warning: {result.stderr}")
    
    print("\nDeployment Complete!")
    print("=" * 60)
    print("\nNew Search Capabilities:")
    print("1. Excludes suppliers who USE products as ingredients")
    print("2. Prioritizes suppliers who SELL products")
    print("3. Handles 1-to-many product relationships")
    print("4. AI-powered product classification")
    print("5. Website scraping for enhanced data (when configured)")
    
    print("\nTest the optimized search at:")
    print("https://www.fdx.trading")
    print("\nTry searching for:")
    print("- 'sunflower oil' (will exclude bakeries)")
    print("- 'wafer biscuits' (will find manufacturers with variations)")
    print("- 'chocolate coating' (will find coating suppliers, not candy makers)")

if __name__ == "__main__":
    deploy_to_vm()