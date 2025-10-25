"""
Logging configuration for the Farmer Budget Optimizer.
Provides structured logging with different levels and outputs.
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Dict, Any

class ContextFilter(logging.Filter):
    """Add context information to log records."""
    
    def filter(self, record):
        # Add timestamp in ISO format
        record.iso_timestamp = datetime.now().isoformat()
        
        # Add process and thread info
        record.process_name = "farmer-budget-optimizer"
        
        # Add request context if available
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        if not hasattr(record, 'user_id'):
            record.user_id = 'N/A'
        
        return True

class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': record.iso_timestamp,
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_name': record.process_name,
            'request_id': getattr(record, 'request_id', 'N/A'),
            'user_id': getattr(record, 'user_id', 'N/A')
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                          'filename', 'module', 'lineno', 'funcName', 'created', 
                          'msecs', 'relativeCreated', 'thread', 'threadName', 
                          'processName', 'process', 'getMessage', 'exc_info', 
                          'exc_text', 'stack_info', 'iso_timestamp', 'process_name']:
                log_entry[key] = value
        
        return self.to_json(log_entry)
    
    def to_json(self, log_entry: Dict[str, Any]) -> str:
        """Convert log entry to JSON string."""
        import json
        try:
            return json.dumps(log_entry, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            # Fallback to string representation
            return str(log_entry)

def setup_logging(
    log_level: str = "INFO",
    log_format: str = "standard",
    log_file: str = None,
    enable_json: bool = False
):
    """
    Set up comprehensive logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ('standard', 'detailed', 'json')
        log_file: Optional log file path
        enable_json: Whether to use JSON formatting
    """
    
    # Create logs directory if it doesn't exist
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # Define formatters
    formatters = {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d [%(funcName)s]'
        },
        'json': {
            '()': JSONFormatter
        }
    }
    
    # Define handlers
    handlers = {
        'console': {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'json' if enable_json else log_format,
            'stream': sys.stdout,
            'filters': ['context']
        }
    }
    
    # Add file handler if log_file is specified
    if log_file:
        handlers['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'json' if enable_json else 'detailed',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'filters': ['context']
        }
    
    # Define filters
    filters = {
        'context': {
            '()': ContextFilter
        }
    }
    
    # Define loggers
    loggers = {
        '': {  # Root logger
            'level': log_level,
            'handlers': list(handlers.keys()),
            'propagate': False
        },
        'uvicorn': {
            'level': 'INFO',
            'handlers': list(handlers.keys()),
            'propagate': False
        },
        'uvicorn.access': {
            'level': 'INFO',
            'handlers': list(handlers.keys()),
            'propagate': False
        },
        'boto3': {
            'level': 'WARNING',
            'handlers': list(handlers.keys()),
            'propagate': False
        },
        'botocore': {
            'level': 'WARNING',
            'handlers': list(handlers.keys()),
            'propagate': False
        },
        'urllib3': {
            'level': 'WARNING',
            'handlers': list(handlers.keys()),
            'propagate': False
        }
    }
    
    # Configure logging
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'filters': filters,
        'handlers': handlers,
        'loggers': loggers
    }
    
    logging.config.dictConfig(config)
    
    # Log configuration info
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, Format: {log_format}, JSON: {enable_json}")
    if log_file:
        logger.info(f"Log file: {log_file}")

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(name)

def log_request_start(request_id: str, method: str, url: str, user_id: str = None):
    """Log the start of a request."""
    logger = get_logger("request")
    logger.info(
        f"Request started: {method} {url}",
        extra={
            'request_id': request_id,
            'user_id': user_id,
            'event_type': 'request_start',
            'method': method,
            'url': url
        }
    )

def log_request_end(request_id: str, status_code: int, duration_ms: float, user_id: str = None):
    """Log the end of a request."""
    logger = get_logger("request")
    logger.info(
        f"Request completed: {status_code} ({duration_ms:.2f}ms)",
        extra={
            'request_id': request_id,
            'user_id': user_id,
            'event_type': 'request_end',
            'status_code': status_code,
            'duration_ms': duration_ms
        }
    )

def log_service_call(service_name: str, operation: str, request_id: str = None, **kwargs):
    """Log external service calls."""
    logger = get_logger("service")
    logger.info(
        f"Service call: {service_name}.{operation}",
        extra={
            'request_id': request_id,
            'event_type': 'service_call',
            'service_name': service_name,
            'operation': operation,
            **kwargs
        }
    )

def log_performance_metric(metric_name: str, value: float, unit: str = "ms", **kwargs):
    """Log performance metrics."""
    logger = get_logger("performance")
    logger.info(
        f"Performance metric: {metric_name} = {value}{unit}",
        extra={
            'event_type': 'performance_metric',
            'metric_name': metric_name,
            'value': value,
            'unit': unit,
            **kwargs
        }
    )