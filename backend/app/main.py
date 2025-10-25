from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import logging
import os
from typing import Dict, Any

from .models import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    HealthResponse, 
    ErrorResponse, 
    ErrorDetail
)
from .error_handling import (
    ServiceError, 
    ErrorCategory, 
    service_monitor, 
    log_error_context,
    GracefulDegradation
)

# Configure comprehensive logging
from .logging_config import setup_logging, get_logger, log_request_start, log_request_end

# Import configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import get_settings

# Get settings
settings = get_settings()

# Setup logging with configuration
setup_logging(
    log_level=settings.log_level,
    log_format=settings.log_format,
    log_file=settings.log_file,
    enable_json=settings.log_json
)

logger = get_logger(__name__)
logger.info(f"Starting Farmer Budget Optimizer API v{settings.app_version} in {settings.environment} mode")

# Create FastAPI application
app = FastAPI(
    title="Farmer Budget Optimizer API",
    description="AI-powered agricultural input price optimization service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS with settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing and context."""
    import time
    
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Add request ID to request state for use in handlers
    request.state.request_id = request_id
    
    # Log request start
    log_request_start(
        request_id=request_id,
        method=request.method,
        url=str(request.url)
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log request completion
        log_request_end(
            request_id=request_id,
            status_code=response.status_code,
            duration_ms=duration_ms
        )
        
        # Add request ID to response headers for debugging
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Calculate duration for failed requests
        duration_ms = (time.time() - start_time) * 1000
        
        # Log failed request
        log_request_end(
            request_id=request_id,
            status_code=500,
            duration_ms=duration_ms
        )
        
        # Re-raise the exception to be handled by exception handlers
        raise

# Enhanced global exception handler
@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    request_id = str(uuid.uuid4())
    
    # Log error with context
    log_error_context(
        exc,
        context={
            "url": str(request.url),
            "method": request.method,
            "category": exc.category.value,
            "retryable": exc.retryable
        },
        request_id=request_id
    )
    
    # Determine HTTP status code based on error category
    status_codes = {
        ErrorCategory.VALIDATION: 400,
        ErrorCategory.AUTHENTICATION: 401,
        ErrorCategory.RATE_LIMIT: 429,
        ErrorCategory.EXTERNAL_API: 503,
        ErrorCategory.AWS_SERVICE: 503,
        ErrorCategory.NETWORK: 503,
        ErrorCategory.PROCESSING: 500,
        ErrorCategory.CONFIGURATION: 500
    }
    
    status_code = status_codes.get(exc.category, 500)
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.category.value,
            message=exc.user_message,
            details={
                "recovery_suggestions": exc.recovery_suggestions,
                "technical_details": str(exc) if log_level == "DEBUG" else None
            },
            retryable=exc.retryable
        ),
        request_id=request_id,
        timestamp=datetime.now()
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = str(uuid.uuid4())
    
    log_error_context(
        exc,
        context={
            "url": str(request.url),
            "method": request.method,
            "status_code": exc.status_code
        },
        request_id=request_id
    )
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="HTTP_ERROR",
            message=exc.detail if isinstance(exc.detail, str) else "HTTP error occurred",
            details=exc.detail if isinstance(exc.detail, dict) else None,
            retryable=exc.status_code >= 500
        ),
        request_id=request_id,
        timestamp=datetime.now()
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    
    log_error_context(
        exc,
        context={
            "url": str(request.url),
            "method": request.method,
            "unexpected": True
        },
        request_id=request_id
    )
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred. Please try again later.",
            details={
                "recovery_suggestions": [
                    "Try again in a few minutes",
                    "Contact support if the problem persists"
                ],
                "technical_details": str(exc) if log_level == "DEBUG" else None
            },
            retryable=True
        ),
        request_id=request_id,
        timestamp=datetime.now()
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )

# Enhanced health check endpoint with service monitoring
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Enhanced health check endpoint that monitors external service dependencies.
    Returns current timestamp, status, and service availability.
    """
    try:
        # Check critical services
        services_to_check = ["aws_forecast", "aws_quicksight", "aws_comprehend"]
        service_statuses = {}
        
        for service in services_to_check:
            try:
                status = service_monitor.get_service_status(service)
                service_statuses[service] = status.value
            except Exception as e:
                logger.warning(f"Health check failed for {service}: {e}")
                service_statuses[service] = "UNKNOWN"
        
        # Check system resources
        system_status = {}
        try:
            import shutil
            import psutil
            
            # Disk space
            total, used, free = shutil.disk_usage(".")
            free_gb = free // (1024**3)
            system_status["disk_free_gb"] = free_gb
            system_status["disk_usage_percent"] = (used / total) * 100
            
            # Memory usage
            memory = psutil.virtual_memory()
            system_status["memory_usage_percent"] = memory.percent
            system_status["memory_available_gb"] = memory.available / (1024**3)
            
            # CPU usage
            system_status["cpu_usage_percent"] = psutil.cpu_percent(interval=1)
            
        except ImportError:
            # psutil not available, basic checks only
            try:
                import shutil
                total, used, free = shutil.disk_usage(".")
                free_gb = free // (1024**3)
                system_status["disk_free_gb"] = free_gb
                system_status["disk_usage_percent"] = (used / total) * 100
            except:
                system_status["error"] = "Cannot check system resources"
        except Exception as e:
            system_status["error"] = f"System check failed: {e}"
        
        # Determine overall health
        unavailable_services = [
            service for service, status in service_statuses.items() 
            if status == "UNAVAILABLE"
        ]
        
        # Check for system resource issues
        resource_issues = []
        if "disk_free_gb" in system_status and system_status["disk_free_gb"] < 1:
            resource_issues.append("low_disk_space")
        if "memory_usage_percent" in system_status and system_status["memory_usage_percent"] > 90:
            resource_issues.append("high_memory_usage")
        if "cpu_usage_percent" in system_status and system_status["cpu_usage_percent"] > 90:
            resource_issues.append("high_cpu_usage")
        
        # Determine overall status
        if len(unavailable_services) == len(services_to_check) or "low_disk_space" in resource_issues:
            overall_status = "unhealthy"
        elif unavailable_services or resource_issues:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(),
            details={
                "services": service_statuses,
                "system": system_status,
                "unavailable_services": unavailable_services,
                "resource_issues": resource_issues,
                "environment": settings.environment,
                "version": settings.app_version
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            details={"error": "Health check failed", "exception": str(e)}
        )

# Readiness probe endpoint for Kubernetes/container orchestration
@app.get("/api/ready")
async def readiness_check():
    """
    Readiness probe endpoint for container orchestration.
    Returns 200 if the application is ready to serve traffic.
    """
    try:
        # Basic readiness checks
        checks = {
            "configuration": False,
            "directories": False,
            "dependencies": False
        }
        
        # Check configuration
        try:
            _ = settings.app_name
            checks["configuration"] = True
        except:
            pass
        
        # Check required directories exist
        try:
            import os
            required_dirs = [settings.data_dir, settings.cache_dir, settings.log_file and os.path.dirname(settings.log_file)]
            required_dirs = [d for d in required_dirs if d]  # Filter out None values
            
            for directory in required_dirs:
                if not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
            
            checks["directories"] = True
        except:
            pass
        
        # Check critical dependencies are importable
        try:
            import boto3
            import requests
            checks["dependencies"] = True
        except:
            pass
        
        if all(checks.values()):
            return {"status": "ready", "checks": checks}
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "checks": checks}
            )
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )

# Liveness probe endpoint for Kubernetes/container orchestration
@app.get("/api/live")
async def liveness_check():
    """
    Liveness probe endpoint for container orchestration.
    Returns 200 if the application is alive and should not be restarted.
    """
    return {"status": "alive", "timestamp": datetime.now()}

# Main analysis endpoint (placeholder for now)
@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_products(request: AnalyzeRequest):
    """
    Analyze agricultural products and provide price optimization recommendations.
    
    This endpoint will be implemented in subsequent tasks.
    For now, it returns a validation error to indicate the endpoint exists
    but functionality is not yet implemented.
    """
    raise HTTPException(
        status_code=501,
        detail={
            "code": "NOT_IMPLEMENTED",
            "message": "Analysis functionality will be implemented in subsequent tasks",
            "retryable": False
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "name": "Farmer Budget Optimizer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/api/health",
            "analyze": "/api/analyze",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)