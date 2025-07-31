"""
Structured Logging Configuration for FoodXchange Platform
Provides consistent logging format and levels across all services
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import traceback

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'endpoint'):
            log_entry["endpoint"] = record.endpoint
        
        return json.dumps(log_entry, ensure_ascii=False)

class ColoredFormatter(logging.Formatter):
    """Colored formatter for development console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for development"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        formatted = (
            f"{color}[{record.levelname:8}]{reset} "
            f"{timestamp} "
            f"{record.name}:{record.lineno} - "
            f"{record.getMessage()}"
        )
        
        if record.exc_info:
            formatted += f"\n{color}Exception:{reset}\n"
            formatted += self.formatException(record.exc_info)
        
        return formatted

def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    structured: bool = True,
    development: bool = False
) -> None:
    """
    Setup application logging configuration
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        structured: Use structured JSON logging
        development: Use colored console output for development
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if development:
        console_formatter = ColoredFormatter()
    elif structured:
        console_formatter = StructuredFormatter()
    else:
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        if structured:
            file_formatter = StructuredFormatter()
        else:
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    
    # Log configuration
    logger = logging.getLogger(__name__)
    logger.info("Logging configured", extra={
        "extra_fields": {
            "level": level,
            "structured": structured,
            "development": development,
            "log_file": log_file
        }
    })

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

def log_with_context(
    logger: logging.Logger,
    level: str,
    message: str,
    **context: Any
) -> None:
    """
    Log a message with additional context
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **context: Additional context fields
    """
    record = logger.makeRecord(
        logger.name,
        getattr(logging, level.upper()),
        "",
        0,
        message,
        (),
        None
    )
    record.extra_fields = context
    logger.handle(record)

def log_request(
    logger: logging.Logger,
    request_id: str,
    method: str,
    url: str,
    user_id: Optional[str] = None,
    duration: Optional[float] = None,
    status_code: Optional[int] = None,
    **extra: Any
) -> None:
    """
    Log HTTP request information
    
    Args:
        logger: Logger instance
        request_id: Unique request identifier
        method: HTTP method
        url: Request URL
        user_id: User identifier (optional)
        duration: Request duration in seconds (optional)
        status_code: HTTP status code (optional)
        **extra: Additional context
    """
    context = {
        "request_id": request_id,
        "method": method,
        "url": url,
        "endpoint": url.split('?')[0],  # Remove query parameters
        **extra
    }
    
    if user_id:
        context["user_id"] = user_id
    
    if duration is not None:
        context["duration_ms"] = round(duration * 1000, 2)
    
    if status_code is not None:
        context["status_code"] = status_code
        level = "INFO" if status_code < 400 else "WARNING"
    else:
        level = "INFO"
    
    log_with_context(logger, level, f"{method} {url}", **context)

def log_error(
    logger: logging.Logger,
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> None:
    """
    Log error with full context
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context
        request_id: Request identifier (optional)
        user_id: User identifier (optional)
    """
    extra_fields = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    
    if context:
        extra_fields.update(context)
    
    if request_id:
        extra_fields["request_id"] = request_id
    
    if user_id:
        extra_fields["user_id"] = user_id
    
    log_with_context(
        logger,
        "ERROR",
        f"Exception occurred: {type(error).__name__}: {error}",
        **extra_fields
    )

def log_performance(
    logger: logging.Logger,
    operation: str,
    duration: float,
    **context: Any
) -> None:
    """
    Log performance metrics
    
    Args:
        logger: Logger instance
        operation: Operation name
        duration: Duration in seconds
        **context: Additional context
    """
    level = "INFO" if duration < 1.0 else "WARNING"
    
    log_with_context(
        logger,
        level,
        f"Performance: {operation} completed in {duration:.3f}s",
        operation=operation,
        duration_ms=round(duration * 1000, 2),
        **context
    )

def log_security_event(
    logger: logging.Logger,
    event_type: str,
    description: str,
    severity: str = "INFO",
    **context: Any
) -> None:
    """
    Log security-related events
    
    Args:
        logger: Logger instance
        event_type: Type of security event
        description: Event description
        severity: Event severity
        **context: Additional context
    """
    log_with_context(
        logger,
        severity,
        f"Security Event [{event_type}]: {description}",
        security_event_type=event_type,
        **context
    )

# Initialize logging with default configuration
def init_logging() -> None:
    """Initialize logging with default configuration"""
    import os
    
    # Determine environment
    environment = os.getenv("ENVIRONMENT", "development")
    development = environment == "development"
    
    # Determine log level
    log_level = os.getenv("LOG_LEVEL", "INFO" if not development else "DEBUG")
    
    # Determine log file
    log_file = os.getenv("LOG_FILE", "logs/foodxchange.log" if not development else None)
    
    # Determine structured logging
    structured = os.getenv("STRUCTURED_LOGGING", "true").lower() == "true"
    
    setup_logging(
        level=log_level,
        log_file=log_file,
        structured=structured,
        development=development
    )

# Auto-initialize logging when module is imported
init_logging() 