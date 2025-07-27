"""
Azure Monitor Service for Food Xchange
Handles Application Insights integration and monitoring
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.ext.azure.trace_exporter import AzureExporter
    from opencensus.ext.azure.metrics_exporter import AzureMetricsExporter
    from opencensus.trace.tracer import Tracer
    from opencensus.trace.samplers import ProbabilitySampler
    from opencensus.ext.fastapi import FastAPIMiddleware
    AZURE_MONITOR_AVAILABLE = True
except ImportError:
    AZURE_MONITOR_AVAILABLE = False
    print("⚠️ Azure Monitor dependencies not available. Install with: pip install opencensus-ext-azure")

class AzureMonitorService:
    """Service for Azure Application Insights monitoring"""
    
    def __init__(self):
        self.enabled = False
        self.instrumentation_key = None
        self.connection_string = None
        self.logger = None
        self.tracer = None
        self.metrics_exporter = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Azure Monitor if configuration is available"""
        if not AZURE_MONITOR_AVAILABLE:
            print("⚠️ Azure Monitor not available - missing dependencies")
            return
        
        # Get configuration from environment
        self.instrumentation_key = os.getenv('AZURE_APP_INSIGHTS_INSTRUMENTATION_KEY')
        self.connection_string = os.getenv('AZURE_APP_INSIGHTS_CONNECTION_STRING')
        enabled = os.getenv('AZURE_APP_INSIGHTS_ENABLED', 'false').lower() == 'true'
        
        if not enabled:
            print("ℹ️ Azure Monitor disabled via environment variable")
            return
        
        if not self.instrumentation_key and not self.connection_string:
            print("⚠️ Azure Monitor not configured - missing instrumentation key or connection string")
            return
        
        try:
            self._setup_logging()
            self._setup_tracing()
            self._setup_metrics()
            self.enabled = True
            print("✅ Azure Monitor initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize Azure Monitor: {e}")
    
    def _setup_logging(self):
        """Setup Azure log handler"""
        if self.connection_string:
            self.logger = logging.getLogger(__name__)
            handler = AzureLogHandler(connection_string=self.connection_string)
            handler.setLevel(logging.INFO)
            self.logger.addHandler(handler)
            print("✅ Azure logging configured")
    
    def _setup_tracing(self):
        """Setup Azure tracing"""
        if self.connection_string:
            self.tracer = Tracer(
                exporter=AzureExporter(connection_string=self.connection_string),
                sampler=ProbabilitySampler(1.0)
            )
            print("✅ Azure tracing configured")
    
    def _setup_metrics(self):
        """Setup Azure metrics exporter"""
        if self.connection_string:
            self.metrics_exporter = AzureMetricsExporter(
                connection_string=self.connection_string
            )
            print("✅ Azure metrics configured")
    
    def log_event(self, event_name: str, properties: Optional[Dict[str, Any]] = None):
        """Log a custom event to Application Insights"""
        if not self.enabled or not self.logger:
            return
        
        try:
            if properties is None:
                properties = {}
            
            properties['timestamp'] = datetime.utcnow().isoformat()
            properties['service'] = 'foodxchange'
            
            self.logger.info(f"Custom Event: {event_name}", extra={
                'custom_dimensions': properties
            })
        except Exception as e:
            print(f"⚠️ Failed to log event {event_name}: {e}")
    
    def log_exception(self, exception: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an exception to Application Insights"""
        if not self.enabled or not self.logger:
            return
        
        try:
            if context is None:
                context = {}
            
            context['exception_type'] = type(exception).__name__
            context['exception_message'] = str(exception)
            context['timestamp'] = datetime.utcnow().isoformat()
            context['service'] = 'foodxchange'
            
            self.logger.error(f"Exception: {exception}", extra={
                'custom_dimensions': context
            })
        except Exception as e:
            print(f"⚠️ Failed to log exception: {e}")
    
    def log_metric(self, metric_name: str, value: float, properties: Optional[Dict[str, Any]] = None):
        """Log a custom metric to Application Insights"""
        if not self.enabled or not self.metrics_exporter:
            return
        
        try:
            if properties is None:
                properties = {}
            
            properties['service'] = 'foodxchange'
            properties['timestamp'] = datetime.utcnow().isoformat()
            
            # Note: This is a simplified implementation
            # In production, you might want to use a more sophisticated metrics system
            self.logger.info(f"Metric: {metric_name} = {value}", extra={
                'custom_dimensions': properties
            })
        except Exception as e:
            print(f"⚠️ Failed to log metric {metric_name}: {e}")
    
    def start_span(self, span_name: str):
        """Start a tracing span"""
        if not self.enabled or not self.tracer:
            return None
        
        try:
            return self.tracer.span(name=span_name)
        except Exception as e:
            print(f"⚠️ Failed to start span {span_name}: {e}")
            return None
    
    def get_fastapi_middleware(self):
        """Get FastAPI middleware for Azure Monitor"""
        if not self.enabled or not AZURE_MONITOR_AVAILABLE:
            return None
        
        try:
            if self.connection_string:
                return FastAPIMiddleware(
                    exporter=AzureExporter(connection_string=self.connection_string),
                    sampler=ProbabilitySampler(1.0)
                )
        except Exception as e:
            print(f"⚠️ Failed to create FastAPI middleware: {e}")
        
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of Azure Monitor"""
        return {
            'enabled': self.enabled,
            'instrumentation_key_configured': bool(self.instrumentation_key),
            'connection_string_configured': bool(self.connection_string),
            'logging_configured': bool(self.logger),
            'tracing_configured': bool(self.tracer),
            'metrics_configured': bool(self.metrics_exporter),
            'dependencies_available': AZURE_MONITOR_AVAILABLE
        }

# Global instance
azure_monitor = AzureMonitorService() 