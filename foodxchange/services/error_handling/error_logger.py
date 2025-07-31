"""
Error Logger Module
Handles error logging, tracking, and reporting
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque

from .models import (
    ErrorDetails,
    ErrorType,
    ErrorSeverity,
    ErrorMetrics
)

logger = logging.getLogger(__name__)


class ErrorLogger:
    """
    Handles error logging and metrics collection
    """
    
    def __init__(self, max_history: int = 1000):
        self.error_history: deque = deque(maxlen=max_history)
        self.error_metrics: Dict[str, ErrorMetrics] = {}
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.recent_errors: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
    
    def log_error(
        self,
        error_details: ErrorDetails,
        context: Optional[Dict[str, Any]] = None,
        recovered: bool = False,
        resolution_time: Optional[float] = None
    ):
        """Log an error with details"""
        try:
            # Create log entry
            log_entry = {
                "timestamp": datetime.now(),
                "error_details": error_details.to_dict(),
                "context": context or {},
                "recovered": recovered,
                "resolution_time": resolution_time
            }
            
            # Add to history
            self.error_history.append(log_entry)
            
            # Update metrics
            self._update_metrics(error_details, recovered, resolution_time)
            
            # Track patterns
            self._track_error_patterns(error_details)
            
            # Add to recent errors by type
            self.recent_errors[error_details.type.value].append(log_entry)
            
            # Log based on severity
            self._log_by_severity(error_details, context)
            
        except Exception as e:
            logger.error(f"Error logging error details: {e}")
    
    def _update_metrics(
        self,
        error_details: ErrorDetails,
        recovered: bool,
        resolution_time: Optional[float]
    ):
        """Update error metrics"""
        error_type = error_details.type
        
        if error_type not in self.error_metrics:
            self.error_metrics[error_type] = ErrorMetrics(error_type=error_type)
        
        self.error_metrics[error_type].update(error_details, recovered, resolution_time)
    
    def _track_error_patterns(self, error_details: ErrorDetails):
        """Track error patterns for analysis"""
        # Track by error message pattern
        message_key = self._normalize_error_message(error_details.technical_message)
        self.error_patterns[message_key] += 1
        
        # Track by source location
        if error_details.source_file and error_details.source_line:
            location_key = f"{error_details.source_file}:{error_details.source_line}"
            self.error_patterns[f"location:{location_key}"] += 1
    
    def _log_by_severity(self, error_details: ErrorDetails, context: Optional[Dict[str, Any]]):
        """Log error based on severity level"""
        log_data = {
            "error_id": error_details.error_id,
            "type": error_details.type.value,
            "message": error_details.technical_message,
            "user_message": error_details.message,
            "source": f"{error_details.source_file}:{error_details.source_line}" if error_details.source_file else "unknown",
            "context": context
        }
        
        if error_details.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"CRITICAL ERROR: {error_details.error_id}", extra=log_data)
        elif error_details.severity == ErrorSeverity.HIGH:
            logger.error(f"HIGH SEVERITY ERROR: {error_details.error_id}", extra=log_data)
        elif error_details.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"MEDIUM SEVERITY ERROR: {error_details.error_id}", extra=log_data)
        else:
            logger.info(f"LOW SEVERITY ERROR: {error_details.error_id}", extra=log_data)
    
    def _normalize_error_message(self, message: str) -> str:
        """Normalize error message for pattern matching"""
        # Remove numbers, IDs, and specific values
        import re
        
        # Remove UUIDs
        message = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID', message, flags=re.IGNORECASE)
        
        # Remove numbers
        message = re.sub(r'\d+', 'N', message)
        
        # Remove file paths
        message = re.sub(r'[/\\][\w\\/.-]+', '/PATH/', message)
        
        # Truncate to reasonable length
        return message[:200]
    
    def get_error_summary(self, time_window: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get error summary statistics"""
        cutoff_time = datetime.now() - time_window if time_window else None
        
        # Filter errors by time window
        relevant_errors = []
        for entry in self.error_history:
            if not cutoff_time or entry["timestamp"] > cutoff_time:
                relevant_errors.append(entry)
        
        # Calculate summary
        summary = {
            "total_errors": len(relevant_errors),
            "by_type": defaultdict(int),
            "by_severity": defaultdict(int),
            "recovery_rate": 0.0,
            "average_resolution_time": 0.0,
            "top_errors": [],
            "error_trend": []
        }
        
        if not relevant_errors:
            return summary
        
        # Count by type and severity
        recovered_count = 0
        total_resolution_time = 0.0
        resolution_count = 0
        
        for entry in relevant_errors:
            error_details = entry["error_details"]
            summary["by_type"][error_details["type"]] += 1
            summary["by_severity"][error_details["severity"]] += 1
            
            if entry["recovered"]:
                recovered_count += 1
            
            if entry["resolution_time"]:
                total_resolution_time += entry["resolution_time"]
                resolution_count += 1
        
        # Calculate rates
        summary["recovery_rate"] = recovered_count / len(relevant_errors) if relevant_errors else 0
        summary["average_resolution_time"] = total_resolution_time / resolution_count if resolution_count > 0 else 0
        
        # Get top error patterns
        top_patterns = sorted(
            self.error_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        summary["top_errors"] = [
            {"pattern": pattern, "count": count}
            for pattern, count in top_patterns
        ]
        
        # Calculate trend (hourly for last 24 hours)
        if time_window and time_window <= timedelta(days=1):
            summary["error_trend"] = self._calculate_hourly_trend(relevant_errors)
        
        return summary
    
    def _calculate_hourly_trend(self, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate hourly error trend"""
        hourly_counts = defaultdict(int)
        
        for entry in errors:
            hour_key = entry["timestamp"].strftime("%Y-%m-%d %H:00")
            hourly_counts[hour_key] += 1
        
        # Create trend data
        trend = []
        current_time = datetime.now()
        for i in range(24):
            hour_time = current_time - timedelta(hours=i)
            hour_key = hour_time.strftime("%Y-%m-%d %H:00")
            trend.append({
                "hour": hour_key,
                "count": hourly_counts.get(hour_key, 0)
            })
        
        return list(reversed(trend))
    
    def get_recent_errors(
        self,
        error_type: Optional[ErrorType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent errors"""
        if error_type:
            return list(self.recent_errors[error_type.value])[:limit]
        
        # Get all recent errors
        all_recent = []
        for error_list in self.recent_errors.values():
            all_recent.extend(list(error_list))
        
        # Sort by timestamp
        all_recent.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return all_recent[:limit]
    
    def get_error_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get error metrics by type"""
        metrics = {}
        
        for error_type, metric in self.error_metrics.items():
            metrics[error_type.value] = {
                "count": metric.count,
                "first_seen": metric.first_seen.isoformat() if metric.first_seen else None,
                "last_seen": metric.last_seen.isoformat() if metric.last_seen else None,
                "severity_breakdown": metric.severity_breakdown,
                "recovery_success_rate": metric.recovery_success_rate,
                "average_resolution_time": metric.average_resolution_time
            }
        
        return metrics
    
    def export_error_report(self, format: str = "json") -> str:
        """Export error report"""
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_error_summary(),
            "metrics": self.get_error_metrics(),
            "recent_errors": self.get_recent_errors(limit=20)
        }
        
        if format == "json":
            return json.dumps(report_data, indent=2, default=str)
        else:
            # Could implement other formats (CSV, HTML, etc.)
            return json.dumps(report_data, indent=2, default=str)
    
    def clear_old_errors(self, days: int = 30):
        """Clear errors older than specified days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # Filter error history
        self.error_history = deque(
            (entry for entry in self.error_history if entry["timestamp"] > cutoff_time),
            maxlen=self.error_history.maxlen
        )
        
        logger.info(f"Cleared errors older than {days} days")