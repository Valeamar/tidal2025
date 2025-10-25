"""
Comprehensive error handling utilities for the Farmer Budget Optimizer.
Provides retry logic, graceful degradation, and user-friendly error messages.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union
from enum import Enum
import boto3
from botocore.exceptions import ClientError, BotoCoreError
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)

class ErrorCategory(str, Enum):
    """Categories of errors for different handling strategies."""
    VALIDATION = "VALIDATION"
    EXTERNAL_API = "EXTERNAL_API"
    AWS_SERVICE = "AWS_SERVICE"
    NETWORK = "NETWORK"
    PROCESSING = "PROCESSING"
    RATE_LIMIT = "RATE_LIMIT"
    AUTHENTICATION = "AUTHENTICATION"
    CONFIGURATION = "CONFIGURATION"

class ServiceStatus(str, Enum):
    """Status of external services."""
    AVAILABLE = "AVAILABLE"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"

class RetryConfig:
    """Configuration for retry logic."""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

class ServiceError(Exception):
    """Base exception for service errors with categorization."""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        retryable: bool = False,
        user_message: Optional[str] = None,
        recovery_suggestions: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.category = category
        self.retryable = retryable
        self.user_message = user_message or self._generate_user_message()
        self.recovery_suggestions = recovery_suggestions or []
        self.details = details or {}
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message based on category."""
        messages = {
            ErrorCategory.VALIDATION: "Please check your input and try again.",
            ErrorCategory.EXTERNAL_API: "We're having trouble accessing market data. Please try again in a few minutes.",
            ErrorCategory.AWS_SERVICE: "Our analysis service is temporarily unavailable. Please try again later.",
            ErrorCategory.NETWORK: "Network connection issue. Please check your internet connection and try again.",
            ErrorCategory.PROCESSING: "We encountered an issue processing your request. Please try again.",
            ErrorCategory.RATE_LIMIT: "Too many requests. Please wait a moment and try again.",
            ErrorCategory.AUTHENTICATION: "Authentication issue with external services. Please contact support.",
            ErrorCategory.CONFIGURATION: "Service configuration issue. Please contact support."
        }
        return messages.get(self.category, "An unexpected error occurred. Please try again.")

class ServiceHealthMonitor:
    """Monitor health status of external services."""
    
    def __init__(self):
        self._service_status: Dict[str, ServiceStatus] = {}
        self._last_check: Dict[str, float] = {}
        self._check_interval = 300  # 5 minutes
    
    def get_service_status(self, service_name: str) -> ServiceStatus:
        """Get current status of a service."""
        current_time = time.time()
        last_check = self._last_check.get(service_name, 0)
        
        if current_time - last_check > self._check_interval:
            self._check_service_health(service_name)
            self._last_check[service_name] = current_time
        
        return self._service_status.get(service_name, ServiceStatus.AVAILABLE)
    
    def _check_service_health(self, service_name: str):
        """Check health of a specific service."""
        try:
            if service_name.startswith("aws_"):
                self._check_aws_service_health(service_name)
            else:
                self._check_external_api_health(service_name)
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {e}")
            self._service_status[service_name] = ServiceStatus.UNAVAILABLE
    
    def _check_aws_service_health(self, service_name: str):
        """Check AWS service health."""
        try:
            service_map = {
                "aws_forecast": "forecast",
                "aws_quicksight": "quicksight",
                "aws_comprehend": "comprehend"
            }
            
            if service_name in service_map:
                client = boto3.client(service_map[service_name])
                # Simple health check - list operations usually work if service is available
                if service_name == "aws_forecast":
                    client.list_datasets(MaxResults=1)
                elif service_name == "aws_quicksight":
                    # QuickSight requires account ID, so we'll assume it's available
                    pass
                elif service_name == "aws_comprehend":
                    client.detect_sentiment(Text="test", LanguageCode="en")
                
                self._service_status[service_name] = ServiceStatus.AVAILABLE
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code in ['Throttling', 'TooManyRequestsException']:
                self._service_status[service_name] = ServiceStatus.DEGRADED
            else:
                self._service_status[service_name] = ServiceStatus.UNAVAILABLE
        except Exception:
            self._service_status[service_name] = ServiceStatus.UNAVAILABLE
    
    def _check_external_api_health(self, service_name: str):
        """Check external API health."""
        # Placeholder for external API health checks
        self._service_status[service_name] = ServiceStatus.AVAILABLE
    
    def mark_service_degraded(self, service_name: str):
        """Mark a service as degraded."""
        self._service_status[service_name] = ServiceStatus.DEGRADED
        logger.warning(f"Service {service_name} marked as degraded")
    
    def mark_service_unavailable(self, service_name: str):
        """Mark a service as unavailable."""
        self._service_status[service_name] = ServiceStatus.UNAVAILABLE
        logger.error(f"Service {service_name} marked as unavailable")

# Global service health monitor
service_monitor = ServiceHealthMonitor()

def with_retry(
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,),
    service_name: Optional[str] = None
):
    """Decorator to add retry logic to functions."""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    # Check service health before attempting
                    if service_name:
                        status = service_monitor.get_service_status(service_name)
                        if status == ServiceStatus.UNAVAILABLE:
                            raise ServiceError(
                                f"Service {service_name} is unavailable",
                                ErrorCategory.EXTERNAL_API,
                                retryable=False,
                                recovery_suggestions=[
                                    "Try again in a few minutes",
                                    "Check service status page"
                                ]
                            )
                    
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    # Don't retry on certain error types
                    if isinstance(e, ServiceError) and not e.retryable:
                        raise
                    
                    if attempt < config.max_attempts - 1:
                        delay = min(
                            config.base_delay * (config.exponential_base ** attempt),
                            config.max_delay
                        )
                        
                        if config.jitter:
                            import random
                            delay *= (0.5 + random.random() * 0.5)
                        
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        
                        if service_name:
                            service_monitor.mark_service_degraded(service_name)
                        
                        await asyncio.sleep(delay)
                    else:
                        if service_name:
                            service_monitor.mark_service_unavailable(service_name)
            
            # All attempts failed
            if isinstance(last_exception, ServiceError):
                raise last_exception
            else:
                raise ServiceError(
                    f"All {config.max_attempts} attempts failed: {last_exception}",
                    ErrorCategory.EXTERNAL_API,
                    retryable=True,
                    recovery_suggestions=[
                        "Try again in a few minutes",
                        "Check your internet connection"
                    ]
                )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_attempts):
                try:
                    # Check service health before attempting
                    if service_name:
                        status = service_monitor.get_service_status(service_name)
                        if status == ServiceStatus.UNAVAILABLE:
                            raise ServiceError(
                                f"Service {service_name} is unavailable",
                                ErrorCategory.EXTERNAL_API,
                                retryable=False
                            )
                    
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    # Don't retry on certain error types
                    if isinstance(e, ServiceError) and not e.retryable:
                        raise
                    
                    if attempt < config.max_attempts - 1:
                        delay = min(
                            config.base_delay * (config.exponential_base ** attempt),
                            config.max_delay
                        )
                        
                        if config.jitter:
                            import random
                            delay *= (0.5 + random.random() * 0.5)
                        
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        
                        if service_name:
                            service_monitor.mark_service_degraded(service_name)
                        
                        time.sleep(delay)
                    else:
                        if service_name:
                            service_monitor.mark_service_unavailable(service_name)
            
            # All attempts failed
            if isinstance(last_exception, ServiceError):
                raise last_exception
            else:
                raise ServiceError(
                    f"All {config.max_attempts} attempts failed: {last_exception}",
                    ErrorCategory.EXTERNAL_API,
                    retryable=True
                )
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def handle_aws_error(e: Exception, service_name: str) -> ServiceError:
    """Convert AWS errors to ServiceError with appropriate categorization."""
    if isinstance(e, ClientError):
        error_code = e.response.get('Error', {}).get('Code', '')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        
        if error_code in ['Throttling', 'TooManyRequestsException', 'ThrottlingException']:
            return ServiceError(
                f"AWS {service_name} rate limit exceeded",
                ErrorCategory.RATE_LIMIT,
                retryable=True,
                recovery_suggestions=[
                    "Wait a few minutes before trying again",
                    "Reduce the frequency of requests"
                ]
            )
        elif error_code in ['AccessDenied', 'UnauthorizedOperation']:
            return ServiceError(
                f"AWS {service_name} access denied",
                ErrorCategory.AUTHENTICATION,
                retryable=False,
                recovery_suggestions=[
                    "Check AWS credentials and permissions",
                    "Contact system administrator"
                ]
            )
        elif error_code in ['InvalidParameterValue', 'ValidationException']:
            return ServiceError(
                f"Invalid parameters for AWS {service_name}",
                ErrorCategory.VALIDATION,
                retryable=False,
                recovery_suggestions=[
                    "Check input parameters",
                    "Refer to API documentation"
                ]
            )
        else:
            return ServiceError(
                f"AWS {service_name} error: {error_message}",
                ErrorCategory.AWS_SERVICE,
                retryable=True,
                recovery_suggestions=[
                    "Try again in a few minutes",
                    "Check AWS service status"
                ]
            )
    elif isinstance(e, BotoCoreError):
        return ServiceError(
            f"AWS {service_name} connection error",
            ErrorCategory.NETWORK,
            retryable=True,
            recovery_suggestions=[
                "Check internet connection",
                "Try again in a few minutes"
            ]
        )
    else:
        return ServiceError(
            f"Unexpected AWS {service_name} error: {str(e)}",
            ErrorCategory.AWS_SERVICE,
            retryable=True
        )

def handle_http_error(e: Exception, service_name: str) -> ServiceError:
    """Convert HTTP errors to ServiceError with appropriate categorization."""
    if isinstance(e, Timeout):
        return ServiceError(
            f"Timeout connecting to {service_name}",
            ErrorCategory.NETWORK,
            retryable=True,
            recovery_suggestions=[
                "Check internet connection",
                "Try again in a few minutes"
            ]
        )
    elif isinstance(e, ConnectionError):
        return ServiceError(
            f"Connection error to {service_name}",
            ErrorCategory.NETWORK,
            retryable=True,
            recovery_suggestions=[
                "Check internet connection",
                "Verify service URL"
            ]
        )
    elif isinstance(e, RequestException):
        return ServiceError(
            f"HTTP request error to {service_name}: {str(e)}",
            ErrorCategory.EXTERNAL_API,
            retryable=True,
            recovery_suggestions=[
                "Try again in a few minutes",
                "Check service status"
            ]
        )
    else:
        return ServiceError(
            f"Unexpected HTTP error to {service_name}: {str(e)}",
            ErrorCategory.EXTERNAL_API,
            retryable=True
        )

class GracefulDegradation:
    """Handles graceful degradation when services are unavailable."""
    
    @staticmethod
    def get_fallback_price_data(product_name: str) -> Dict[str, Any]:
        """Provide fallback price data when market data is unavailable."""
        logger.info(f"Using fallback price data for {product_name}")
        
        # Simple fallback based on product type
        base_prices = {
            "fertilizer": 50.0,
            "seed": 25.0,
            "pesticide": 75.0,
            "equipment": 500.0
        }
        
        # Determine product type from name
        product_lower = product_name.lower()
        base_price = 100.0  # Default
        
        for product_type, price in base_prices.items():
            if product_type in product_lower:
                base_price = price
                break
        
        return {
            "base_price": base_price,
            "price_range": {
                "p10": base_price * 0.8,
                "p25": base_price * 0.9,
                "p50": base_price,
                "p75": base_price * 1.1,
                "p90": base_price * 1.2
            },
            "confidence": 0.3,  # Low confidence for fallback data
            "data_source": "fallback",
            "limitations": [
                "Market data unavailable",
                "Using estimated pricing",
                "Actual prices may vary significantly"
            ]
        }
    
    @staticmethod
    def get_fallback_forecast(product_name: str) -> Dict[str, Any]:
        """Provide fallback forecast when AWS Forecast is unavailable."""
        logger.info(f"Using fallback forecast for {product_name}")
        
        return {
            "trend": "stable",
            "confidence": 0.2,
            "predictions": [],
            "seasonality": "unknown",
            "data_source": "fallback",
            "limitations": [
                "Forecast service unavailable",
                "No trend analysis available",
                "Consider manual market research"
            ]
        }
    
    @staticmethod
    def get_fallback_sentiment() -> Dict[str, Any]:
        """Provide fallback sentiment when AWS Comprehend is unavailable."""
        logger.info("Using fallback sentiment analysis")
        
        return {
            "sentiment": "neutral",
            "confidence": 0.2,
            "supply_risk": "unknown",
            "data_source": "fallback",
            "limitations": [
                "Sentiment analysis unavailable",
                "No market sentiment data",
                "Monitor news manually"
            ]
        }

def log_error_context(
    error: Exception,
    context: Dict[str, Any],
    user_id: Optional[str] = None,
    request_id: Optional[str] = None
):
    """Log error with full context for debugging."""
    logger.error(
        f"Error occurred: {type(error).__name__}: {str(error)}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "user_id": user_id,
            "request_id": request_id
        },
        exc_info=True
    )