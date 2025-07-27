#!/usr/bin/env python3
"""
Azure Deployment Monitor
Specialized monitoring for Azure Web App deployment issues and conflicts
"""

import os
import sys
import time
import json
import logging
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import azure.mgmt.web
import azure.mgmt.resource
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('azure_deployment_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AzureDeploymentMonitor:
    def __init__(self):
        self.subscription_id = os.getenv('AZURE_SUBSCRIPTION_ID')
        self.resource_group = os.getenv('AZURE_RESOURCE_GROUP', 'foodxchange-rg')
        self.web_app_name = os.getenv('AZURE_WEB_APP_NAME', 'foodxchange-app')
        self.credential = DefaultAzureCredential()
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'deployment_status': {},
            'app_service_health': {},
            'deployment_conflicts': [],
            'recommendations': [],
            'errors': []
        }
        
    def check_azure_credentials(self) -> bool:
        """Verify Azure credentials are properly configured"""
        try:
            # Test credential access
            web_client = azure.mgmt.web.WebSiteManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
            
            # Try to list web apps to verify access
            web_apps = list(web_client.web_apps.list_by_resource_group(self.resource_group))
            logger.info(f"Successfully authenticated with Azure. Found {len(web_apps)} web apps.")
            return True
            
        except Exception as e:
            logger.error(f"Azure authentication failed: {e}")
            self.results['errors'].append(f"Authentication failed: {str(e)}")
            return False
    
    def check_deployment_status(self) -> Dict[str, Any]:
        """Check current deployment status and identify conflicts"""
        deployment_info = {
            'status': 'unknown',
            'last_deployment': None,
            'active_deployments': [],
            'conflicts': [],
            'recommendations': []
        }
        
        try:
            web_client = azure.mgmt.web.WebSiteManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
            
            # Get deployment history
            deployments = list(web_client.web_apps.list_deployments(
                resource_group_name=self.resource_group,
                name=self.web_app_name
            ))
            
            if deployments:
                latest_deployment = deployments[0]
                deployment_info['last_deployment'] = {
                    'id': latest_deployment.id,
                    'status': latest_deployment.status,
                    'message': latest_deployment.message,
                    'created_time': latest_deployment.created_time.isoformat() if latest_deployment.created_time else None
                }
                
                # Check for deployment conflicts
                if latest_deployment.status == 4:  # Failed
                    deployment_info['status'] = 'failed'
                    deployment_info['conflicts'].append({
                        'type': 'deployment_failed',
                        'message': latest_deployment.message,
                        'recommendation': 'Check deployment logs and resolve conflicts'
                    })
                    
                    # Check for specific error codes
                    if '409' in str(latest_deployment.message):
                        deployment_info['conflicts'].append({
                            'type': 'conflict_409',
                            'message': 'Deployment conflict detected (409 error)',
                            'recommendation': 'Stop any running deployments and retry'
                        })
                        
                elif latest_deployment.status == 3:  # In Progress
                    deployment_info['status'] = 'in_progress'
                    deployment_info['recommendations'].append('Wait for current deployment to complete')
                    
                elif latest_deployment.status == 2:  # Successful
                    deployment_info['status'] = 'successful'
                    
            else:
                deployment_info['status'] = 'no_deployments'
                deployment_info['recommendations'].append('No deployment history found')
                
        except Exception as e:
            logger.error(f"Error checking deployment status: {e}")
            deployment_info['status'] = 'error'
            deployment_info['conflicts'].append({
                'type': 'check_error',
                'message': str(e),
                'recommendation': 'Verify Azure credentials and permissions'
            })
            
        self.results['deployment_status'] = deployment_info
        return deployment_info
    
    def check_app_service_health(self) -> Dict[str, Any]:
        """Check App Service health and configuration"""
        health_info = {
            'status': 'unknown',
            'state': None,
            'host_names': [],
            'ssl_state': None,
            'https_only': None,
            'client_affinity_enabled': None,
            'issues': []
        }
        
        try:
            web_client = azure.mgmt.web.WebSiteManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
            
            # Get web app details
            web_app = web_client.web_apps.get(
                resource_group_name=self.resource_group,
                name=self.web_app_name
            )
            
            health_info['state'] = web_app.state
            health_info['host_names'] = web_app.host_names
            health_info['ssl_state'] = web_app.https_only
            health_info['https_only'] = web_app.https_only
            health_info['client_affinity_enabled'] = web_app.client_affinity_enabled
            
            if web_app.state == 'Running':
                health_info['status'] = 'healthy'
            elif web_app.state == 'Stopped':
                health_info['status'] = 'stopped'
                health_info['issues'].append('App Service is stopped')
            else:
                health_info['status'] = 'unknown'
                health_info['issues'].append(f'App Service state: {web_app.state}')
                
        except Exception as e:
            logger.error(f"Error checking App Service health: {e}")
            health_info['status'] = 'error'
            health_info['issues'].append(f'Health check failed: {str(e)}')
            
        self.results['app_service_health'] = health_info
        return health_info
    
    def check_deployment_conflicts(self) -> List[Dict[str, Any]]:
        """Check for specific deployment conflicts"""
        conflicts = []
        
        try:
            # Check for running deployments
            web_client = azure.mgmt.web.WebSiteManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )
            
            # Get recent deployments
            deployments = list(web_client.web_apps.list_deployments(
                resource_group_name=self.resource_group,
                name=self.web_app_name
            ))
            
            # Check for multiple active deployments
            active_deployments = [d for d in deployments if d.status == 3]  # In Progress
            if len(active_deployments) > 1:
                conflicts.append({
                    'type': 'multiple_active_deployments',
                    'severity': 'high',
                    'message': f'Found {len(active_deployments)} active deployments',
                    'recommendation': 'Stop conflicting deployments before retrying'
                })
            
            # Check for failed deployments with 409 errors
            failed_deployments = [d for d in deployments if d.status == 4 and '409' in str(d.message)]
            if failed_deployments:
                conflicts.append({
                    'type': 'conflict_409_errors',
                    'severity': 'high',
                    'message': f'Found {len(failed_deployments)} deployments with 409 conflicts',
                    'recommendation': 'Clear deployment locks and retry deployment'
                })
                
        except Exception as e:
            logger.error(f"Error checking deployment conflicts: {e}")
            conflicts.append({
                'type': 'conflict_check_error',
                'severity': 'medium',
                'message': f'Failed to check conflicts: {str(e)}',
                'recommendation': 'Verify Azure permissions'
            })
            
        self.results['deployment_conflicts'] = conflicts
        return conflicts
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on current status"""
        recommendations = []
        
        # Check deployment status
        deployment_status = self.results['deployment_status']
        if deployment_status.get('status') == 'failed':
            recommendations.append("Deployment failed - check logs for specific errors")
            
        # Check for conflicts
        conflicts = self.results['deployment_conflicts']
        for conflict in conflicts:
            if conflict['type'] == 'conflict_409_errors':
                recommendations.append("Stop all running deployments and clear deployment locks")
                recommendations.append("Wait 5-10 minutes before retrying deployment")
            elif conflict['type'] == 'multiple_active_deployments':
                recommendations.append("Cancel conflicting deployments in Azure portal")
                
        # Check App Service health
        health = self.results['app_service_health']
        if health.get('status') == 'stopped':
            recommendations.append("Start the App Service before deploying")
            
        # General recommendations
        if not recommendations:
            recommendations.append("System appears healthy - proceed with deployment")
            
        self.results['recommendations'] = recommendations
        return recommendations
    
    def run_full_check(self) -> Dict[str, Any]:
        """Run complete deployment health check"""
        logger.info("Starting Azure deployment health check...")
        
        # Check credentials
        if not self.check_azure_credentials():
            return self.results
            
        # Run all checks
        self.check_deployment_status()
        self.check_app_service_health()
        self.check_deployment_conflicts()
        self.generate_recommendations()
        
        logger.info("Azure deployment health check completed")
        return self.results
    
    def save_report(self, filename: str = None):
        """Save monitoring report to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"azure_deployment_report_{timestamp}.json"
            
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            logger.info(f"Report saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
    
    def print_summary(self):
        """Print human-readable summary"""
        print("\n" + "="*60)
        print("AZURE DEPLOYMENT MONITOR SUMMARY")
        print("="*60)
        
        # Deployment Status
        deployment = self.results['deployment_status']
        print(f"\n📦 Deployment Status: {deployment.get('status', 'unknown').upper()}")
        if deployment.get('last_deployment'):
            last_deploy = deployment['last_deployment']
            print(f"   Last Deployment: {last_deploy.get('created_time', 'Unknown')}")
            print(f"   Status: {last_deploy.get('status', 'Unknown')}")
            if last_deploy.get('message'):
                print(f"   Message: {last_deploy['message']}")
        
        # App Service Health
        health = self.results['app_service_health']
        print(f"\n🏥 App Service Health: {health.get('status', 'unknown').upper()}")
        print(f"   State: {health.get('state', 'Unknown')}")
        print(f"   HTTPS Only: {health.get('https_only', 'Unknown')}")
        
        # Conflicts
        conflicts = self.results['deployment_conflicts']
        if conflicts:
            print(f"\n⚠️  Conflicts Found: {len(conflicts)}")
            for conflict in conflicts:
                print(f"   • {conflict['type']}: {conflict['message']}")
        else:
            print(f"\n✅ No conflicts detected")
        
        # Recommendations
        recommendations = self.results['recommendations']
        if recommendations:
            print(f"\n💡 Recommendations:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        # Errors
        errors = self.results['errors']
        if errors:
            print(f"\n❌ Errors:")
            for error in errors:
                print(f"   • {error}")
        
        print("\n" + "="*60)

def main():
    """Main function"""
    monitor = AzureDeploymentMonitor()
    
    try:
        # Run full check
        results = monitor.run_full_check()
        
        # Print summary
        monitor.print_summary()
        
        # Save report
        monitor.save_report()
        
        # Exit with appropriate code
        if results['deployment_conflicts'] or results['errors']:
            sys.exit(1)  # Issues found
        else:
            sys.exit(0)  # All good
            
    except KeyboardInterrupt:
        print("\nMonitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 