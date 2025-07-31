"""
Setup Application Insights for FoodXchange
Enables real-time monitoring and analytics
"""

import os
import json
from pathlib import Path

def create_app_insights_config():
    """Create Application Insights configuration"""
    
    # Application Insights configuration
    config = {
        "APPINSIGHTS_INSTRUMENTATIONKEY": "YOUR_KEY_HERE",
        "APPLICATIONINSIGHTS_CONNECTION_STRING": "InstrumentationKey=YOUR_KEY_HERE;IngestionEndpoint=https://westeurope-5.in.applicationinsights.azure.com/;LiveEndpoint=https://westeurope.livediagnostics.monitor.azure.com/",
        "ENABLE_TELEMETRY": True,
        "TELEMETRY_SETTINGS": {
            "enable_live_metrics": True,
            "enable_dependency_tracking": True,
            "enable_performance_counters": True,
            "enable_error_tracking": True,
            "sampling_percentage": 100.0
        }
    }
    
    print("📊 Application Insights Setup Guide")
    print("=" * 50)
    print("\n1. Create Application Insights in Azure Portal:")
    print("   - Go to: https://portal.azure.com")
    print("   - Create resource > Application Insights")
    print("   - Name: foodxchange-insights")
    print("   - Resource Group: foodxchange-rg")
    print("   - Region: West Europe")
    print("\n2. Get the Instrumentation Key from Overview page")
    print("\n3. Update the configuration above with your key")
    print("\n4. Add to your .env file:")
    print("   APPINSIGHTS_INSTRUMENTATIONKEY=your-key-here")
    
    # Create monitoring middleware
    middleware_code = '''
# Add this to foodxchange/main.py after imports

from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.fastapi.fastapi_middleware import FastAPIMiddleware
from opencensus.trace.samplers import ProbabilitySampler

# Configure Application Insights
if os.getenv("APPINSIGHTS_INSTRUMENTATIONKEY"):
    app.add_middleware(
        FastAPIMiddleware,
        tracer=None,
        exporter=AzureExporter(
            connection_string=f"InstrumentationKey={os.getenv('APPINSIGHTS_INSTRUMENTATIONKEY')}"
        ),
        sampler=ProbabilitySampler(rate=1.0),
    )
    logger.info("📊 Application Insights enabled")
'''
    
    print("\n5. Add monitoring middleware:")
    print(middleware_code)
    
    # Save configuration template
    config_path = Path("configs/app_insights_config.json")
    config_path.parent.mkdir(exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration template saved to: {config_path}")
    print("\n📈 Benefits of Application Insights:")
    print("   - Real-time performance metrics")
    print("   - Error tracking and alerts")
    print("   - User analytics")
    print("   - Dependency mapping")
    print("   - Custom event tracking")

if __name__ == "__main__":
    create_app_insights_config()