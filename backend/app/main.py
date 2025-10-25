from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import logging
import os
import sys
from typing import Dict, Any, List, Optional

from .models import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    HealthResponse, 
    ErrorResponse, 
    ErrorDetail,
    ProductAnalysisResult,
    OverallBudget,
    DataQualityReport,
    # Advanced Optimization Models
    PriceAlertRequest,
    PriceAlert,
    BundlingAnalysisRequest,
    BundlingAnalysisResponse,
    BundlingOpportunity,
    PurchaseTrackingRequest,
    PurchaseTrackingResponse,
    PurchaseRecord,
    PurchasePerformanceSummary,
    FinancingAnalysisRequest,
    FinancingAnalysisResponse,
    FinancingOption,
    FinancingRecommendation
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

# Main analysis endpoint
@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_products(request: AnalyzeRequest):
    """
    Analyze agricultural products and provide price optimization recommendations.
    
    Integrates with PriceAnalysisAgent for processing with real data sources.
    Returns individual product analyses with data availability reporting.
    Includes overall budget and data quality report in response.
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.6, 3.7
    """
    request_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    logger.info(f"Request {request_id}: Starting analysis for {len(request.products)} products")
    
    try:
        # Input validation (Pydantic handles basic validation, we add business rules)
        if len(request.products) > 50:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_INPUT", 
                    "message": "Maximum 50 products allowed per request",
                    "retryable": False
                }
            )
        
        # Initialize Price Analysis Agent
        # Use mock data for MVP, disable AWS BI for initial implementation
        agent = PriceAnalysisAgent(use_mock_data=True, enable_aws_bi=False)
        
        # Perform analysis
        logger.info(f"Request {request_id}: Running price analysis")
        product_analyses = await agent.analyze_product_list(
            request.products, 
            request.farm_location
        )
        
        # Calculate overall budget
        overall_budget = _calculate_overall_budget(product_analyses)
        
        # Generate data quality report
        data_quality_report = _generate_data_quality_report(product_analyses)
        
        # Store analysis results
        try:
            storage_manager = get_storage_manager()
            analysis_response = AnalyzeResponse(
                product_analyses=product_analyses,
                overall_budget=overall_budget,
                data_quality_report=data_quality_report,
                generated_at=datetime.now()
            )
            session_id = storage_manager.save_analysis_result(analysis_response)
            logger.info(f"Request {request_id}: Analysis stored with session ID {session_id}")
        except Exception as e:
            logger.warning(f"Request {request_id}: Failed to store analysis: {e}")
            # Continue without storage - don't fail the request
        
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Request {request_id}: Analysis completed in {processing_time:.2f}s")
        
        return AnalyzeResponse(
            product_analyses=product_analyses,
            overall_budget=overall_budget,
            data_quality_report=data_quality_report,
            generated_at=datetime.now()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
        
    except Exception as e:
        logger.error(f"Request {request_id}: Analysis failed: {str(e)}", exc_info=True)
        
        # Return structured error response
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ANALYSIS_ERROR",
                "message": "Failed to complete price analysis",
                "details": {
                    "error_type": type(e).__name__,
                    "request_id": request_id
                },
                "retryable": True
            }
        )

# Storage management endpoints
@app.get("/api/storage/stats")
async def get_storage_stats():
    """
    Get statistics about stored data.
    Demonstrates the storage system functionality.
    """
    try:
        storage_manager = get_storage_manager()
        stats = storage_manager.get_storage_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "STORAGE_ERROR",
                "message": "Failed to retrieve storage statistics",
                "retryable": True
            }
        )

@app.get("/api/storage/sessions")
async def list_recent_sessions(limit: int = 10):
    """
    List recent analysis sessions.
    Demonstrates the session storage functionality.
    """
    try:
        storage_manager = get_storage_manager()
        sessions = storage_manager.list_recent_analyses(limit)
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "STORAGE_ERROR",
                "message": "Failed to retrieve analysis sessions",
                "retryable": True
            }
        )

@app.post("/api/storage/cleanup")
async def cleanup_old_data():
    """
    Clean up old cached data and analysis sessions.
    Demonstrates the storage maintenance functionality.
    """
    try:
        storage_manager = get_storage_manager()
        cleanup_stats = storage_manager.cleanup_old_data()
        return cleanup_stats
    except Exception as e:
        logger.error(f"Failed to cleanup data: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "STORAGE_ERROR",
                "message": "Failed to cleanup old data",
                "retryable": True
            }
        )

# Advanced Optimization Features (Task 7.2)

@app.post("/api/price-alerts", response_model=Dict[str, Any])
async def create_price_alert(alert_request: PriceAlertRequest):
    """
    Create a price alert for target price monitoring.
    
    Implements comprehensive price alert system with multiple alert types,
    threshold monitoring, and automated notifications.
    
    Requirements: 6.1 - Price alerts when target prices are reached
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Create price alert record
        alert = PriceAlert(
            alert_id=request_id,
            product_name=alert_request.product_name,
            target_price=alert_request.target_price,
            farm_location=alert_request.farm_location,
            contact_email=alert_request.contact_email,
            alert_type=alert_request.alert_type,
            threshold_percentage=alert_request.threshold_percentage,
            created_at=datetime.now(),
            expiry_date=alert_request.expiry_date,
            status="active"
        )
        
        # Get current market price for comparison
        try:
            market_service = MarketDataService(use_mock_data=True)
            current_quotes = await market_service.get_current_prices(
                alert_request.product_name, alert_request.farm_location
            )
            
            if current_quotes:
                current_price = sum(q.base_price for q in current_quotes) / len(current_quotes)
                alert.current_price = current_price
                
                # Check if alert should trigger immediately
                should_trigger = _check_alert_trigger(alert, current_price)
                if should_trigger:
                    alert.status = "triggered"
                    logger.info(f"Alert {request_id} triggered immediately - target price already met")
            
        except Exception as e:
            logger.warning(f"Could not fetch current price for alert: {e}")
        
        # Store alert (in production, this would go to a database)
        storage_manager = get_storage_manager()
        try:
            storage_manager.save_price_alert(alert)
            logger.info(f"Price alert {request_id} stored successfully")
        except Exception as e:
            logger.warning(f"Failed to store alert: {e}")
        
        # Prepare response
        response_data = {
            "alert_id": request_id,
            "message": "Price alert created successfully",
            "alert_details": alert.model_dump(),
            "current_market_price": alert.current_price,
            "monitoring_status": "active" if alert.status == "active" else "triggered",
            "estimated_check_frequency": "Every 6 hours",
            "notification_methods": ["email"],
            "next_check": (datetime.now() + timedelta(hours=6)).isoformat()
        }
        
        if alert.status == "triggered":
            response_data["immediate_trigger"] = True
            response_data["trigger_reason"] = "Target price already available in current market"
        
        return response_data
        
    except Exception as e:
        logger.error(f"Failed to create price alert: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ALERT_ERROR",
                "message": "Failed to create price alert",
                "retryable": True
            }
        )

@app.get("/api/price-alerts", response_model=Dict[str, Any])
async def list_price_alerts(
    status: Optional[str] = None,
    product_name: Optional[str] = None,
    limit: int = 20
):
    """
    List existing price alerts with optional filtering.
    
    Requirements: 6.1 - Price alert management and monitoring
    """
    try:
        storage_manager = get_storage_manager()
        alerts = storage_manager.list_price_alerts(
            status=status,
            product_name=product_name,
            limit=limit
        )
        
        return {
            "alerts": alerts,
            "total_count": len(alerts),
            "active_alerts": len([a for a in alerts if a.get("status") == "active"]),
            "triggered_alerts": len([a for a in alerts if a.get("status") == "triggered"])
        }
        
    except Exception as e:
        logger.error(f"Failed to list price alerts: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ALERT_ERROR",
                "message": "Failed to retrieve price alerts",
                "retryable": True
            }
        )

@app.delete("/api/price-alerts/{alert_id}")
async def cancel_price_alert(alert_id: str):
    """
    Cancel an existing price alert.
    
    Requirements: 6.1 - Price alert management
    """
    try:
        storage_manager = get_storage_manager()
        success = storage_manager.cancel_price_alert(alert_id)
        
        if success:
            return {
                "message": "Price alert cancelled successfully",
                "alert_id": alert_id,
                "cancelled_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "ALERT_NOT_FOUND",
                    "message": "Price alert not found",
                    "retryable": False
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel price alert: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ALERT_ERROR",
                "message": "Failed to cancel price alert",
                "retryable": True
            }
        )

@app.post("/api/bundling-analysis", response_model=BundlingAnalysisResponse)
async def analyze_cross_product_bundling(bundling_request: BundlingAnalysisRequest):
    """
    Analyze cross-product bundling opportunities from suppliers offering multiple items.
    
    Implements comprehensive bundling analysis including supplier bundles,
    group purchasing opportunities, and cooperative buying programs.
    
    Requirements: 6.2 - Cross-product bundling analysis
    """
    request_id = str(uuid.uuid4())
    
    try:
        products = bundling_request.products
        farm_location = bundling_request.farm_location
        
        logger.info(f"Starting bundling analysis for {len(products)} products")
        
        # Initialize market service and price calculator
        market_service = MarketDataService(use_mock_data=True)
        calculator = PriceCalculator()
        
        # Get individual product pricing
        individual_analyses = {}
        total_individual_cost = 0.0
        
        for product in products:
            try:
                # Get market data for each product
                quotes = await market_service.get_current_prices(product.name, farm_location)
                
                if quotes:
                    # Calculate effective cost for individual purchase
                    economic_analysis = calculator.perform_comprehensive_economic_analysis(
                        product, quotes, farm_location
                    )
                    
                    price_ranges = economic_analysis.get("price_analysis", {}).get("price_ranges", {})
                    target_price = price_ranges.get("p35", price_ranges.get("p50", quotes[0].base_price))
                    product_cost = target_price * product.quantity
                    
                    individual_analyses[product.name] = {
                        "target_price": target_price,
                        "quantity": product.quantity,
                        "total_cost": product_cost,
                        "quotes": quotes
                    }
                    total_individual_cost += product_cost
                else:
                    # Fallback pricing
                    estimated_price = product.max_price or 100.0
                    product_cost = estimated_price * product.quantity
                    individual_analyses[product.name] = {
                        "target_price": estimated_price,
                        "quantity": product.quantity,
                        "total_cost": product_cost,
                        "quotes": []
                    }
                    total_individual_cost += product_cost
                    
            except Exception as e:
                logger.warning(f"Error analyzing {product.name}: {e}")
                # Use fallback pricing
                estimated_price = product.max_price or 100.0
                product_cost = estimated_price * product.quantity
                individual_analyses[product.name] = {
                    "target_price": estimated_price,
                    "quantity": product.quantity,
                    "total_cost": product_cost,
                    "quotes": []
                }
                total_individual_cost += product_cost
        
        # Generate bundling opportunities
        bundling_opportunities = []
        
        # 1. Supplier Bundle Opportunities
        supplier_bundles = _generate_supplier_bundle_opportunities(
            products, individual_analyses, total_individual_cost
        )
        bundling_opportunities.extend(supplier_bundles)
        
        # 2. Group Purchase Opportunities
        if bundling_request.include_group_purchasing:
            group_opportunities = _generate_group_purchase_opportunities(
                products, individual_analyses, total_individual_cost, farm_location
            )
            bundling_opportunities.extend(group_opportunities)
        
        # 3. Cooperative Buying Programs
        cooperative_opportunities = _generate_cooperative_opportunities(
            products, individual_analyses, total_individual_cost, farm_location
        )
        bundling_opportunities.extend(cooperative_opportunities)
        
        # Sort opportunities by savings amount
        bundling_opportunities.sort(key=lambda x: x.savings_amount, reverse=True)
        
        # Limit to max_suppliers
        bundling_opportunities = bundling_opportunities[:bundling_request.max_suppliers]
        
        # Determine recommended bundle
        recommended_bundle = None
        if bundling_opportunities:
            # Recommend bundle with best combination of savings and confidence
            best_score = 0
            for opportunity in bundling_opportunities:
                score = (opportunity.savings_amount * 0.7) + (opportunity.confidence_score * 1000 * 0.3)
                if score > best_score:
                    best_score = score
                    recommended_bundle = opportunity
        
        max_savings = max([opp.savings_amount for opp in bundling_opportunities]) if bundling_opportunities else 0.0
        
        logger.info(f"Bundling analysis completed: {len(bundling_opportunities)} opportunities found")
        
        return BundlingAnalysisResponse(
            analysis_id=request_id,
            products_analyzed=len(products),
            bundling_opportunities=bundling_opportunities,
            total_opportunities=len(bundling_opportunities),
            max_potential_savings=max_savings,
            recommended_bundle=recommended_bundle,
            analysis_date=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Bundling analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "BUNDLING_ERROR",
                "message": "Failed to analyze bundling opportunities",
                "retryable": True
            }
        )

@app.post("/api/purchase-tracking", response_model=PurchaseTrackingResponse)
async def track_purchase(purchase_request: PurchaseTrackingRequest):
    """
    Track and compare actual purchase prices against recommended targets.
    
    Implements comprehensive purchase tracking with performance analytics,
    historical comparison, and learning from purchasing patterns.
    
    Requirements: 6.3 - Purchase tracking and comparison features
    Requirements: 6.4 - Learning from farmer purchasing patterns
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Calculate performance metrics
        actual_price = purchase_request.actual_price
        target_price = purchase_request.target_price or 0
        quantity = purchase_request.quantity
        total_cost = actual_price * quantity
        
        # Calculate variance metrics
        if target_price > 0:
            price_variance = actual_price - target_price
            price_variance_percentage = (price_variance / target_price) * 100
            
            if price_variance <= 0:
                performance_rating = "excellent"
            elif price_variance_percentage <= 5:
                performance_rating = "good"
            elif price_variance_percentage <= 15:
                performance_rating = "needs_improvement"
            else:
                performance_rating = "poor"
        else:
            price_variance = 0
            price_variance_percentage = 0
            performance_rating = "no_target_available"
        
        # Create purchase record
        purchase_record = PurchaseRecord(
            purchase_id=request_id,
            product_name=purchase_request.product_name,
            supplier=purchase_request.supplier,
            actual_price=actual_price,
            target_price=target_price,
            quantity=quantity,
            total_cost=total_cost,
            purchase_date=purchase_request.purchase_date,
            delivery_date=purchase_request.delivery_date,
            payment_terms=purchase_request.payment_terms,
            price_variance=price_variance,
            price_variance_percentage=price_variance_percentage,
            performance_rating=performance_rating,
            recorded_at=datetime.now(),
            notes=purchase_request.notes
        )
        
        # Store purchase record
        storage_manager = get_storage_manager()
        try:
            storage_manager.save_purchase_record(purchase_record)
            logger.info(f"Purchase record {request_id} stored successfully")
        except Exception as e:
            logger.warning(f"Failed to store purchase record: {e}")
        
        # Get historical performance for comparison
        historical_data = _get_historical_purchase_performance(
            purchase_request.product_name, storage_manager
        )
        
        # Calculate performance summary
        performance_summary = PurchasePerformanceSummary(
            rating=performance_rating,
            savings_vs_target=max(0, -price_variance),
            overspend_vs_target=max(0, price_variance),
            variance_percentage=price_variance_percentage,
            total_purchases=historical_data.get("total_purchases", 1),
            average_performance=historical_data.get("average_performance")
        )
        
        # Generate insights based on performance and historical data
        insights = _generate_purchase_insights(
            purchase_record, performance_summary, historical_data
        )
        
        # Generate recommendations for future purchases
        recommendations = _generate_purchase_recommendations(
            purchase_record, performance_summary, historical_data
        )
        
        # Prepare comparison data
        comparison_data = {
            "historical_average_price": historical_data.get("average_price"),
            "historical_best_price": historical_data.get("best_price"),
            "historical_worst_price": historical_data.get("worst_price"),
            "market_position": _calculate_market_position(actual_price, historical_data),
            "seasonal_comparison": historical_data.get("seasonal_data"),
            "supplier_performance": historical_data.get("supplier_performance", {}).get(purchase_request.supplier)
        }
        
        logger.info(f"Purchase tracking completed for {purchase_request.product_name}")
        
        return PurchaseTrackingResponse(
            purchase_id=request_id,
            purchase_record=purchase_record,
            performance_summary=performance_summary,
            insights=insights,
            recommendations=recommendations,
            comparison_data=comparison_data
        )
        
    except Exception as e:
        logger.error(f"Purchase tracking failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "TRACKING_ERROR",
                "message": "Failed to track purchase",
                "retryable": True
            }
        )

@app.get("/api/purchase-history/{product_name}")
async def get_purchase_history(
    product_name: str,
    limit: int = 20,
    supplier: Optional[str] = None
):
    """
    Get purchase history for a specific product with performance analytics.
    
    Requirements: 6.3, 6.4 - Purchase tracking and learning from patterns
    """
    try:
        storage_manager = get_storage_manager()
        history = storage_manager.get_purchase_history(
            product_name=product_name,
            limit=limit,
            supplier=supplier
        )
        
        # Calculate aggregate statistics
        if history:
            prices = [p["actual_price"] for p in history]
            performance_ratings = [p["performance_rating"] for p in history]
            
            analytics = {
                "total_purchases": len(history),
                "average_price": sum(prices) / len(prices),
                "lowest_price": min(prices),
                "highest_price": max(prices),
                "price_trend": _calculate_price_trend(history),
                "performance_distribution": {
                    rating: performance_ratings.count(rating) 
                    for rating in set(performance_ratings)
                },
                "top_suppliers": _get_top_suppliers(history),
                "seasonal_patterns": _analyze_seasonal_patterns(history)
            }
        else:
            analytics = {}
        
        return {
            "product_name": product_name,
            "purchase_history": history,
            "analytics": analytics,
            "total_records": len(history)
        }
        
    except Exception as e:
        logger.error(f"Failed to get purchase history: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "TRACKING_ERROR",
                "message": "Failed to retrieve purchase history",
                "retryable": True
            }
        )

@app.post("/api/financing-analysis", response_model=FinancingAnalysisResponse)
async def analyze_financing_options(financing_request: FinancingAnalysisRequest):
    """
    Analyze financing options including cash discounts versus payment terms.
    
    Implements comprehensive financing analysis with seasonal cash flow considerations,
    credit score impact, and farm-specific payment term optimization.
    
    Requirements: 6.5 - Financing options analysis including cash discounts versus payment terms
    Requirements: 6.6 - Integration with farm management systems to align purchasing with planting schedules
    """
    request_id = str(uuid.uuid4())
    
    try:
        total_amount = financing_request.total_purchase_amount
        cash_available = financing_request.cash_available
        credit_score = financing_request.credit_score
        preferred_terms = financing_request.preferred_terms_months
        risk_tolerance = financing_request.risk_tolerance
        seasonal_cash_flow = financing_request.seasonal_cash_flow or {}
        
        logger.info(f"Analyzing financing options for ${total_amount:,.2f} purchase")
        
        # Generate financing options based on credit profile and preferences
        financing_options = []
        
        # 1. Cash Payment Options
        cash_options = _generate_cash_payment_options(
            total_amount, cash_available, seasonal_cash_flow
        )
        financing_options.extend(cash_options)
        
        # 2. Short-term Financing (30-90 days)
        short_term_options = _generate_short_term_financing_options(
            total_amount, credit_score, seasonal_cash_flow
        )
        financing_options.extend(short_term_options)
        
        # 3. Medium-term Financing (6-18 months)
        medium_term_options = _generate_medium_term_financing_options(
            total_amount, credit_score, preferred_terms, risk_tolerance
        )
        financing_options.extend(medium_term_options)
        
        # 4. Long-term Financing (24+ months)
        if total_amount > 10000:  # Only for larger purchases
            long_term_options = _generate_long_term_financing_options(
                total_amount, credit_score, seasonal_cash_flow
            )
            financing_options.extend(long_term_options)
        
        # 5. Seasonal/Agricultural Financing
        seasonal_options = _generate_seasonal_financing_options(
            total_amount, credit_score, seasonal_cash_flow
        )
        financing_options.extend(seasonal_options)
        
        # Sort by recommendation score
        financing_options.sort(key=lambda x: x.recommendation_score, reverse=True)
        
        # Generate comprehensive recommendation
        recommendation = _generate_financing_recommendation(
            financing_options, total_amount, cash_available, 
            seasonal_cash_flow, risk_tolerance
        )
        
        # Generate analysis notes
        notes = _generate_financing_notes(
            total_amount, cash_available, credit_score, seasonal_cash_flow
        )
        
        logger.info(f"Financing analysis completed: {len(financing_options)} options generated")
        
        return FinancingAnalysisResponse(
            analysis_id=request_id,
            purchase_amount=total_amount,
            cash_available=cash_available,
            financing_options=financing_options,
            recommendation=recommendation,
            analysis_date=datetime.now(),
            notes=notes
        )
        
    except Exception as e:
        logger.error(f"Financing analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "FINANCING_ERROR",
                "message": "Failed to analyze financing options",
                "retryable": True
            }
        )

@app.post("/api/group-purchasing")
async def analyze_group_purchasing_opportunities(group_request: Dict[str, Any]):
    """
    Identify regional cooperative purchasing programs and group buying opportunities.
    
    Requirements: 6.6, 6.7 - Regional cooperative purchasing programs and group buying opportunities
    """
    request_id = str(uuid.uuid4())
    
    try:
        products = group_request.get("products", [])
        farm_location = group_request.get("farm_location", {})
        group_size = group_request.get("target_group_size", 5)
        
        # Analyze group purchasing potential
        group_opportunities = []
        
        for product in products:
            product_name = product.get("name", "")
            quantity = product.get("quantity", 0)
            estimated_price = product.get("max_price", 100)
            
            # Calculate group purchase benefits
            individual_cost = quantity * estimated_price
            
            # Different group purchase scenarios
            scenarios = [
                {
                    "type": "Local Farm Cooperative",
                    "min_participants": 3,
                    "discount_rate": 0.08,
                    "coordination_fee": 50,
                    "delivery_savings": 0.03
                },
                {
                    "type": "Regional Buying Group",
                    "min_participants": 5,
                    "discount_rate": 0.12,
                    "coordination_fee": 100,
                    "delivery_savings": 0.05
                },
                {
                    "type": "State Agricultural Cooperative",
                    "min_participants": 10,
                    "discount_rate": 0.15,
                    "coordination_fee": 200,
                    "delivery_savings": 0.08
                }
            ]
            
            for scenario in scenarios:
                if group_size >= scenario["min_participants"]:
                    # Calculate savings
                    volume_discount = individual_cost * scenario["discount_rate"]
                    delivery_savings = individual_cost * scenario["delivery_savings"]
                    total_savings = volume_discount + delivery_savings - scenario["coordination_fee"]
                    
                    if total_savings > 0:
                        group_opportunities.append({
                            "product_name": product_name,
                            "group_type": scenario["type"],
                            "minimum_participants": scenario["min_participants"],
                            "individual_cost": individual_cost,
                            "group_cost": individual_cost - total_savings,
                            "total_savings": total_savings,
                            "savings_percentage": (total_savings / individual_cost) * 100,
                            "coordination_fee": scenario["coordination_fee"],
                            "estimated_timeline": "2-4 weeks to organize",
                            "requirements": [
                                f"Minimum {scenario['min_participants']} participating farms",
                                "Coordinated delivery scheduling",
                                "Shared payment terms"
                            ]
                        })
        
        # Find existing cooperatives in the area (mock data)
        regional_cooperatives = _find_regional_cooperatives(farm_location)
        
        return {
            "analysis_id": request_id,
            "group_opportunities": group_opportunities,
            "regional_cooperatives": regional_cooperatives,
            "organization_tips": [
                "Contact local extension office for farmer contact lists",
                "Use social media and farm forums to recruit participants",
                "Establish clear payment and delivery terms upfront",
                "Consider seasonal timing for maximum participation"
            ],
            "next_steps": [
                "Identify potential participating farms in your area",
                "Contact regional cooperatives for existing programs",
                "Calculate minimum viable group size for target savings",
                "Set up coordination meeting with interested farmers"
            ]
        }
        
    except Exception as e:
        logger.error(f"Group purchasing analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "GROUP_PURCHASE_ERROR",
                "message": "Failed to analyze group purchasing opportunities",
                "retryable": True
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
            "price_alerts": "/api/price-alerts",
            "bundling_analysis": "/api/bundling-analysis", 
            "purchase_tracking": "/api/purchase-tracking",
            "purchase_history": "/api/purchase-history/{product_name}",
            "financing_analysis": "/api/financing-analysis",
            "group_purchasing": "/api/group-purchasing",
            "storage_stats": "/api/storage/stats",
            "storage_sessions": "/api/storage/sessions",
            "storage_cleanup": "/api/storage/cleanup",
            "docs": "/docs"
        },
        "advanced_features": {
            "price_alerts": "Monitor target prices and get notifications",
            "bundling_analysis": "Find cross-product bundling opportunities",
            "purchase_tracking": "Track and compare actual vs target prices",
            "financing_analysis": "Analyze financing options and cash flow",
            "group_purchasing": "Identify cooperative buying opportunities"
        }
    }

# Helper functions for analysis endpoint

def _calculate_overall_budget(product_analyses: List[ProductAnalysisResult]) -> OverallBudget:
    """
    Calculate overall budget from individual product analyses.
    
    Args:
        product_analyses: List of product analysis results
        
    Returns:
        OverallBudget with aggregated costs
    """
    if not product_analyses:
        return OverallBudget(low=0.0, target=0.0, high=0.0, total_cost=0.0)
    
    total_low = sum(analysis.individual_budget.low for analysis in product_analyses)
    total_target = sum(analysis.individual_budget.target for analysis in product_analyses)
    total_high = sum(analysis.individual_budget.high for analysis in product_analyses)
    total_cost = sum(analysis.individual_budget.total_cost for analysis in product_analyses)
    
    return OverallBudget(
        low=total_low,
        target=total_target,
        high=total_high,
        total_cost=total_cost
    )

def _generate_data_quality_report(product_analyses: List[ProductAnalysisResult]) -> DataQualityReport:
    """
    Generate data quality report from product analyses.
    
    Args:
        product_analyses: List of product analysis results
        
    Returns:
        DataQualityReport with quality metrics
    """
    if not product_analyses:
        return DataQualityReport(
            overall_data_coverage=0.0,
            reliable_products=[],
            limited_data_products=[],
            no_data_products=[]
        )
    
    reliable_products = []
    limited_data_products = []
    no_data_products = []
    
    total_coverage = 0.0
    
    for analysis in product_analyses:
        product_name = analysis.product_name
        data_availability = analysis.data_availability
        confidence_score = analysis.analysis.confidence_score
        
        # Calculate coverage score for this product
        coverage_factors = [
            1.0 if data_availability.price_data_found else 0.0,
            1.0 if data_availability.supplier_data_found else 0.0,
            1.0 if data_availability.forecast_data_available else 0.0,
            1.0 if data_availability.sentiment_data_available else 0.0
        ]
        product_coverage = sum(coverage_factors) / len(coverage_factors)
        total_coverage += product_coverage
        
        # Categorize products by data quality
        if confidence_score >= 0.7 and data_availability.price_data_found:
            reliable_products.append(product_name)
        elif confidence_score >= 0.3 and data_availability.price_data_found:
            limited_data_products.append(product_name)
        else:
            no_data_products.append(product_name)
    
    overall_coverage = total_coverage / len(product_analyses)
    
    return DataQualityReport(
        overall_data_coverage=overall_coverage,
        reliable_products=reliable_products,
        limited_data_products=limited_data_products,
        no_data_products=no_data_products
    )

# Helper functions for advanced optimization features

from .models import ProductInput, FarmLocation  # Additional imports for helper functions

def _check_alert_trigger(alert: PriceAlert, current_price: float) -> bool:
    """Check if a price alert should trigger based on current market price."""
    if alert.alert_type == "price_drop":
        return current_price <= alert.target_price
    elif alert.alert_type == "price_rise":
        return current_price >= alert.target_price
    elif alert.alert_type == "availability":
        return True  # Simplified - would check actual availability
    return False

def _generate_supplier_bundle_opportunities(
    products: List[ProductInput], 
    individual_analyses: Dict[str, Any], 
    total_individual_cost: float
) -> List[BundlingOpportunity]:
    """Generate supplier bundle opportunities."""
    opportunities = []
    
    # Mock supplier bundles - in production, this would query real supplier data
    suppliers = [
        {
            "name": "AgriSupply Co.",
            "bundle_discount": 0.08,
            "min_products": 2,
            "delivery_terms": "Free delivery for orders over $5,000",
            "validity": "30 days from quote"
        },
        {
            "name": "Farm Direct Supply",
            "bundle_discount": 0.06,
            "min_products": 3,
            "delivery_terms": "Standard delivery included",
            "validity": "14 days from quote"
        },
        {
            "name": "Regional Agricultural Supply",
            "bundle_discount": 0.10,
            "min_products": 2,
            "delivery_terms": "Coordinated delivery available",
            "validity": "21 days from quote"
        }
    ]
    
    for supplier in suppliers:
        if len(products) >= supplier["min_products"]:
            bundle_cost = total_individual_cost * (1 - supplier["bundle_discount"])
            savings = total_individual_cost - bundle_cost
            
            opportunity = BundlingOpportunity(
                supplier=supplier["name"],
                products_included=[p.name for p in products],
                individual_total_cost=total_individual_cost,
                bundle_cost=bundle_cost,
                savings_amount=savings,
                savings_percentage=supplier["bundle_discount"] * 100,
                minimum_order_quantity=f"All {len(products)} products together",
                delivery_terms=supplier["delivery_terms"],
                bundle_validity=supplier["validity"],
                bundle_type="supplier_bundle",
                confidence_score=0.8
            )
            opportunities.append(opportunity)
    
    return opportunities

def _generate_group_purchase_opportunities(
    products: List[ProductInput], 
    individual_analyses: Dict[str, Any], 
    total_individual_cost: float,
    farm_location: FarmLocation
) -> List[BundlingOpportunity]:
    """Generate group purchase opportunities."""
    opportunities = []
    
    # Group purchase scenarios
    group_scenarios = [
        {
            "name": "Local Farm Cooperative",
            "discount": 0.12,
            "min_farms": 5,
            "coordination_fee": 100
        },
        {
            "name": "Regional Buying Group",
            "discount": 0.15,
            "min_farms": 8,
            "coordination_fee": 200
        }
    ]
    
    for scenario in group_scenarios:
        bundle_cost = total_individual_cost * (1 - scenario["discount"]) + scenario["coordination_fee"]
        savings = total_individual_cost - bundle_cost
        
        if savings > 0:
            opportunity = BundlingOpportunity(
                supplier=scenario["name"],
                products_included=[p.name for p in products],
                individual_total_cost=total_individual_cost,
                bundle_cost=bundle_cost,
                savings_amount=savings,
                savings_percentage=((savings / total_individual_cost) * 100),
                minimum_order_quantity=f"Group purchase with {scenario['min_farms']} farms minimum",
                delivery_terms="Coordinated delivery to reduce costs",
                bundle_validity="Group purchase window: 14 days",
                bundle_type="group_purchase",
                confidence_score=0.7
            )
            opportunities.append(opportunity)
    
    return opportunities

def _generate_cooperative_opportunities(
    products: List[ProductInput], 
    individual_analyses: Dict[str, Any], 
    total_individual_cost: float,
    farm_location: FarmLocation
) -> List[BundlingOpportunity]:
    """Generate cooperative buying program opportunities."""
    opportunities = []
    
    # State/regional cooperative programs
    cooperative_discount = 0.18  # 18% cooperative discount
    membership_fee = 250
    
    bundle_cost = total_individual_cost * (1 - cooperative_discount) + membership_fee
    savings = total_individual_cost - bundle_cost
    
    if savings > 0:
        opportunity = BundlingOpportunity(
            supplier=f"{farm_location.state} Agricultural Cooperative",
            products_included=[p.name for p in products],
            individual_total_cost=total_individual_cost,
            bundle_cost=bundle_cost,
            savings_amount=savings,
            savings_percentage=((savings / total_individual_cost) * 100),
            minimum_order_quantity="Cooperative membership required",
            delivery_terms="Member delivery network",
            bundle_validity="Annual membership benefits",
            bundle_type="cooperative",
            confidence_score=0.9
        )
        opportunities.append(opportunity)
    
    return opportunities

def _get_historical_purchase_performance(
    product_name: str, 
    storage_manager: Any
) -> Dict[str, Any]:
    """Get historical purchase performance data."""
    try:
        history = storage_manager.get_purchase_history(product_name, limit=50)
        
        if not history:
            return {"total_purchases": 0}
        
        prices = [p["actual_price"] for p in history]
        performance_scores = []
        
        for purchase in history:
            if purchase["performance_rating"] == "excellent":
                performance_scores.append(1.0)
            elif purchase["performance_rating"] == "good":
                performance_scores.append(0.8)
            elif purchase["performance_rating"] == "needs_improvement":
                performance_scores.append(0.6)
            else:
                performance_scores.append(0.4)
        
        return {
            "total_purchases": len(history),
            "average_price": sum(prices) / len(prices),
            "best_price": min(prices),
            "worst_price": max(prices),
            "average_performance": sum(performance_scores) / len(performance_scores),
            "recent_trend": _calculate_recent_trend(history[-5:]) if len(history) >= 5 else "insufficient_data"
        }
        
    except Exception as e:
        logger.warning(f"Could not retrieve historical data: {e}")
        return {"total_purchases": 0}

def _calculate_recent_trend(recent_purchases: List[Dict[str, Any]]) -> str:
    """Calculate recent price trend from purchase history."""
    if len(recent_purchases) < 3:
        return "insufficient_data"
    
    prices = [p["actual_price"] for p in recent_purchases]
    
    # Simple trend calculation
    first_half = sum(prices[:len(prices)//2]) / (len(prices)//2)
    second_half = sum(prices[len(prices)//2:]) / (len(prices) - len(prices)//2)
    
    change_pct = ((second_half - first_half) / first_half) * 100
    
    if change_pct > 5:
        return "increasing"
    elif change_pct < -5:
        return "decreasing"
    else:
        return "stable"

def _generate_purchase_insights(
    purchase_record: PurchaseRecord,
    performance_summary: PurchasePerformanceSummary,
    historical_data: Dict[str, Any]
) -> List[str]:
    """Generate insights based on purchase performance."""
    insights = []
    
    # Performance-based insights
    if purchase_record.performance_rating == "excellent":
        insights.append(f"Excellent purchase! You saved ${performance_summary.savings_vs_target:.2f} compared to target price")
    elif purchase_record.performance_rating == "good":
        insights.append("Good purchase performance - close to target pricing")
    elif purchase_record.performance_rating == "needs_improvement":
        insights.append(f"Price was ${performance_summary.overspend_vs_target:.2f} above target - consider alternative strategies")
    
    # Historical comparison insights
    if historical_data.get("total_purchases", 0) > 1:
        avg_price = historical_data.get("average_price", 0)
        if purchase_record.actual_price < avg_price:
            savings_vs_avg = avg_price - purchase_record.actual_price
            insights.append(f"Great timing! Price is ${savings_vs_avg:.2f} below your historical average")
        elif purchase_record.actual_price > avg_price * 1.1:
            insights.append("Price is significantly above your historical average - market conditions may be unfavorable")
    
    # Trend insights
    trend = historical_data.get("recent_trend")
    if trend == "increasing":
        insights.append("Recent price trend is upward - good timing to purchase before further increases")
    elif trend == "decreasing":
        insights.append("Prices have been declining recently - consider if purchase could have been delayed")
    
    return insights

def _generate_purchase_recommendations(
    purchase_record: PurchaseRecord,
    performance_summary: PurchasePerformanceSummary,
    historical_data: Dict[str, Any]
) -> List[str]:
    """Generate recommendations for future purchases."""
    recommendations = []
    
    # Performance-based recommendations
    if purchase_record.performance_rating in ["needs_improvement", "poor"]:
        recommendations.append("Set up price alerts for this product to catch better pricing opportunities")
        recommendations.append("Consider bundling with other products for volume discounts")
        recommendations.append("Research additional suppliers for competitive pricing")
    
    # Historical pattern recommendations
    if historical_data.get("total_purchases", 0) >= 3:
        avg_performance = historical_data.get("average_performance", 0.5)
        if avg_performance < 0.7:
            recommendations.append("Consider changing your purchasing strategy - historical performance suggests room for improvement")
    
    # Seasonal recommendations
    current_month = datetime.now().month
    if current_month in [3, 4, 5]:  # Spring
        recommendations.append("Track seasonal patterns - spring purchases often have higher prices")
    elif current_month in [9, 10, 11]:  # Fall
        recommendations.append("Fall timing may offer better pricing for next season's inputs")
    
    # General recommendations
    recommendations.extend([
        "Track market trends and seasonal patterns for optimal timing",
        "Build relationships with multiple suppliers for competitive options",
        "Consider group purchasing with neighboring farms for volume discounts"
    ])
    
    return recommendations[:5]  # Limit to top 5 recommendations

def _calculate_market_position(actual_price: float, historical_data: Dict[str, Any]) -> str:
    """Calculate market position of the purchase price."""
    if not historical_data or historical_data.get("total_purchases", 0) == 0:
        return "no_historical_data"
    
    best_price = historical_data.get("best_price", actual_price)
    worst_price = historical_data.get("worst_price", actual_price)
    
    if actual_price <= best_price * 1.05:  # Within 5% of best price
        return "excellent"
    elif actual_price <= (best_price + worst_price) / 2:  # Below average
        return "good"
    elif actual_price <= worst_price * 0.95:  # Within 5% of worst price
        return "poor"
    else:
        return "average"

def _calculate_price_trend(history: List[Dict[str, Any]]) -> str:
    """Calculate overall price trend from purchase history."""
    if len(history) < 3:
        return "insufficient_data"
    
    # Sort by purchase date
    sorted_history = sorted(history, key=lambda x: x.get("purchase_date", ""))
    prices = [p["actual_price"] for p in sorted_history]
    
    # Calculate trend using linear regression (simplified)
    n = len(prices)
    x_sum = sum(range(n))
    y_sum = sum(prices)
    xy_sum = sum(i * prices[i] for i in range(n))
    x2_sum = sum(i * i for i in range(n))
    
    slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum * x_sum)
    
    # Determine trend based on slope
    avg_price = y_sum / n
    slope_pct = (slope / avg_price) * 100
    
    if slope_pct > 2:
        return "increasing"
    elif slope_pct < -2:
        return "decreasing"
    else:
        return "stable"

def _get_top_suppliers(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Get top suppliers by performance from purchase history."""
    supplier_stats = {}
    
    for purchase in history:
        supplier = purchase.get("supplier", "Unknown")
        if supplier not in supplier_stats:
            supplier_stats[supplier] = {
                "name": supplier,
                "purchases": 0,
                "total_cost": 0,
                "avg_price": 0,
                "performance_scores": []
            }
        
        stats = supplier_stats[supplier]
        stats["purchases"] += 1
        stats["total_cost"] += purchase.get("total_cost", 0)
        
        # Convert performance rating to score
        rating = purchase.get("performance_rating", "average")
        if rating == "excellent":
            stats["performance_scores"].append(1.0)
        elif rating == "good":
            stats["performance_scores"].append(0.8)
        elif rating == "needs_improvement":
            stats["performance_scores"].append(0.6)
        else:
            stats["performance_scores"].append(0.4)
    
    # Calculate averages and sort by performance
    for supplier, stats in supplier_stats.items():
        if stats["purchases"] > 0:
            stats["avg_performance"] = sum(stats["performance_scores"]) / len(stats["performance_scores"])
            stats["avg_price"] = stats["total_cost"] / stats["purchases"]
    
    # Sort by performance score, then by number of purchases
    top_suppliers = sorted(
        supplier_stats.values(),
        key=lambda x: (x["avg_performance"], x["purchases"]),
        reverse=True
    )
    
    return top_suppliers[:5]  # Return top 5 suppliers

def _analyze_seasonal_patterns(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze seasonal patterns in purchase history."""
    if len(history) < 6:
        return {"insufficient_data": True}
    
    monthly_data = {}
    
    for purchase in history:
        try:
            # Extract month from purchase date
            purchase_date = purchase.get("purchase_date", "")
            if purchase_date:
                month = datetime.fromisoformat(purchase_date.replace('Z', '+00:00')).month
                
                if month not in monthly_data:
                    monthly_data[month] = {
                        "prices": [],
                        "purchases": 0
                    }
                
                monthly_data[month]["prices"].append(purchase.get("actual_price", 0))
                monthly_data[month]["purchases"] += 1
        except Exception:
            continue
    
    # Calculate monthly averages
    seasonal_analysis = {}
    for month, data in monthly_data.items():
        if data["purchases"] > 0:
            seasonal_analysis[month] = {
                "avg_price": sum(data["prices"]) / len(data["prices"]),
                "purchase_count": data["purchases"],
                "month_name": [
                    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
                ][month - 1]
            }
    
    # Find best and worst months
    if seasonal_analysis:
        best_month = min(seasonal_analysis.keys(), key=lambda m: seasonal_analysis[m]["avg_price"])
        worst_month = max(seasonal_analysis.keys(), key=lambda m: seasonal_analysis[m]["avg_price"])
        
        return {
            "monthly_data": seasonal_analysis,
            "best_month": {
                "month": best_month,
                "avg_price": seasonal_analysis[best_month]["avg_price"],
                "name": seasonal_analysis[best_month]["month_name"]
            },
            "worst_month": {
                "month": worst_month,
                "avg_price": seasonal_analysis[worst_month]["avg_price"],
                "name": seasonal_analysis[worst_month]["month_name"]
            }
        }
    
    return {"insufficient_data": True}

def _generate_cash_payment_options(
    total_amount: float, 
    cash_available: float, 
    seasonal_cash_flow: Dict[str, float]
) -> List[FinancingOption]:
    """Generate cash payment financing options."""
    options = []
    
    # Standard cash payment with discount
    cash_discount_rates = [0.02, 0.03, 0.05]  # 2%, 3%, 5% discounts
    
    for discount_rate in cash_discount_rates:
        cash_payment_amount = total_amount * (1 - discount_rate)
        
        if cash_available >= cash_payment_amount:
            option = FinancingOption(
                option=f"Cash Payment ({discount_rate*100:.0f}% discount)",
                total_cost=cash_payment_amount,
                upfront_payment=cash_payment_amount,
                monthly_payment=0,
                total_interest=0,
                savings_vs_full_price=total_amount - cash_payment_amount,
                cash_flow_impact="High upfront payment, preserves credit capacity",
                recommendation_score=95 - int(discount_rate * 100),
                pros=[
                    f"${total_amount - cash_payment_amount:.2f} immediate savings",
                    "No interest charges or ongoing payments",
                    "Strengthens supplier relationships"
                ],
                cons=[
                    f"Requires ${cash_payment_amount:,.2f} upfront",
                    "Reduces working capital reserves",
                    "May impact cash flow for other needs"
                ],
                terms_months=0,
                interest_rate=0
            )
            options.append(option)
    
    return options

def _generate_short_term_financing_options(
    total_amount: float, 
    credit_score: Optional[int], 
    seasonal_cash_flow: Dict[str, float]
) -> List[FinancingOption]:
    """Generate short-term financing options (30-90 days)."""
    options = []
    
    # Net terms options
    net_terms = [30, 60, 90]
    
    for days in net_terms:
        # Interest rate based on credit score and term length
        if credit_score and credit_score >= 750:
            interest_rate = 0.01 * (days / 30)  # 1% per month for excellent credit
        elif credit_score and credit_score >= 650:
            interest_rate = 0.02 * (days / 30)  # 2% per month for good credit
        else:
            interest_rate = 0.03 * (days / 30)  # 3% per month for fair credit
        
        total_cost = total_amount * (1 + interest_rate)
        
        option = FinancingOption(
            option=f"{days}-Day Net Terms",
            total_cost=total_cost,
            upfront_payment=0,
            monthly_payment=total_cost if days <= 30 else 0,
            total_interest=total_cost - total_amount,
            savings_vs_full_price=0,
            cash_flow_impact=f"Payment due in {days} days",
            recommendation_score=85 - (days // 30) * 5,
            pros=[
                "Preserves immediate cash flow",
                "Standard industry terms",
                "No complex approval process"
            ],
            cons=[
                f"${total_cost - total_amount:.2f} in interest charges",
                f"Large payment due in {days} days",
                "May require personal guarantee"
            ],
            terms_months=0,
            interest_rate=interest_rate * 12  # Annualized
        )
        options.append(option)
    
    return options

def _generate_medium_term_financing_options(
    total_amount: float, 
    credit_score: Optional[int], 
    preferred_terms: Optional[int], 
    risk_tolerance: str
) -> List[FinancingOption]:
    """Generate medium-term financing options (6-18 months)."""
    options = []
    
    terms_options = [6, 12, 18]
    if preferred_terms and preferred_terms in range(6, 19):
        terms_options = [preferred_terms] + [t for t in terms_options if t != preferred_terms]
    
    for months in terms_options:
        # Interest rate based on credit score and risk tolerance
        base_rate = 0.06  # 6% base annual rate
        
        if credit_score:
            if credit_score >= 750:
                base_rate = 0.05
            elif credit_score >= 650:
                base_rate = 0.07
            else:
                base_rate = 0.09
        
        # Adjust for term length
        annual_rate = base_rate + (months - 6) * 0.002  # Slight increase for longer terms
        monthly_rate = annual_rate / 12
        
        # Calculate monthly payment using loan formula
        monthly_payment = total_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        total_cost = monthly_payment * months
        
        option = FinancingOption(
            option=f"{months}-Month Equipment Financing",
            total_cost=total_cost,
            upfront_payment=0,
            monthly_payment=monthly_payment,
            total_interest=total_cost - total_amount,
            savings_vs_full_price=0,
            cash_flow_impact=f"${monthly_payment:.2f} monthly for {months} months",
            recommendation_score=75 - abs(months - 12) * 2,  # Prefer 12-month terms
            pros=[
                "Predictable monthly payments",
                "Preserves working capital",
                "Builds business credit history"
            ],
            cons=[
                f"${total_cost - total_amount:.2f} total interest cost",
                "Monthly payment obligation",
                "May require collateral"
            ],
            terms_months=months,
            interest_rate=annual_rate
        )
        options.append(option)
    
    return options

def _generate_long_term_financing_options(
    total_amount: float, 
    credit_score: Optional[int], 
    seasonal_cash_flow: Dict[str, float]
) -> List[FinancingOption]:
    """Generate long-term financing options (24+ months)."""
    options = []
    
    if total_amount < 10000:  # Only for larger purchases
        return options
    
    terms_options = [24, 36, 48]
    
    for months in terms_options:
        # Lower rates for longer terms on equipment
        base_rate = 0.08 + (months - 24) * 0.001  # Slight increase for longer terms
        
        if credit_score:
            if credit_score >= 750:
                base_rate -= 0.015
            elif credit_score >= 650:
                base_rate -= 0.005
            else:
                base_rate += 0.01
        
        monthly_rate = base_rate / 12
        monthly_payment = total_amount * (monthly_rate * (1 + monthly_rate)**months) / ((1 + monthly_rate)**months - 1)
        total_cost = monthly_payment * months
        
        option = FinancingOption(
            option=f"{months}-Month Equipment Loan",
            total_cost=total_cost,
            upfront_payment=0,
            monthly_payment=monthly_payment,
            total_interest=total_cost - total_amount,
            savings_vs_full_price=0,
            cash_flow_impact=f"${monthly_payment:.2f} monthly for {months//12} years",
            recommendation_score=65 - (months - 24) // 12 * 5,
            pros=[
                "Lowest monthly payment",
                "Maximum cash flow preservation",
                "Tax advantages for equipment"
            ],
            cons=[
                f"${total_cost - total_amount:.2f} total interest cost",
                "Long-term commitment",
                "Equipment serves as collateral"
            ],
            terms_months=months,
            interest_rate=base_rate
        )
        options.append(option)
    
    return options

def _generate_seasonal_financing_options(
    total_amount: float, 
    credit_score: Optional[int], 
    seasonal_cash_flow: Dict[str, float]
) -> List[FinancingOption]:
    """Generate seasonal/agricultural financing options."""
    options = []
    
    # Seasonal payment plan (pay after harvest)
    harvest_months = [9, 10, 11]  # Fall harvest season
    current_month = datetime.now().month
    
    # Calculate months until harvest
    months_to_harvest = 12 - current_month + 9 if current_month > 9 else 9 - current_month
    if months_to_harvest <= 0:
        months_to_harvest = 12
    
    # Seasonal rate (typically lower due to agricultural focus)
    seasonal_rate = 0.055  # 5.5% annual rate for agricultural financing
    if credit_score and credit_score >= 700:
        seasonal_rate = 0.045
    
    # Calculate cost with seasonal terms
    interest_cost = total_amount * seasonal_rate * (months_to_harvest / 12)
    total_cost = total_amount + interest_cost
    
    option = FinancingOption(
        option="Seasonal Agricultural Financing",
        total_cost=total_cost,
        upfront_payment=0,
        monthly_payment=0,  # Balloon payment at harvest
        total_interest=interest_cost,
        savings_vs_full_price=0,
        cash_flow_impact=f"Payment due at harvest ({months_to_harvest} months)",
        recommendation_score=80,
        pros=[
            "Aligns payments with farm income cycle",
            "Lower agricultural interest rates",
            "No monthly payment pressure"
        ],
        cons=[
            f"${interest_cost:.2f} interest cost",
            "Large balloon payment required",
            "Dependent on successful harvest"
        ],
        terms_months=months_to_harvest,
        interest_rate=seasonal_rate
    )
    options.append(option)
    
    return options

def _generate_financing_recommendation(
    financing_options: List[FinancingOption],
    total_amount: float,
    cash_available: float,
    seasonal_cash_flow: Dict[str, float],
    risk_tolerance: str
) -> FinancingRecommendation:
    """Generate comprehensive financing recommendation."""
    if not financing_options:
        return FinancingRecommendation(
            recommended_option="Manual Research Required",
            reasoning="No suitable financing options found for your situation",
            key_benefits=["Contact lenders directly for custom terms"],
            considerations=["Explore alternative funding sources"]
        )
    
    best_option = financing_options[0]  # Already sorted by recommendation score
    
    # Determine reasoning based on cash position and option type
    cash_ratio = cash_available / total_amount
    
    if cash_ratio >= 1.0 and "Cash Payment" in best_option.option:
        reasoning = f"With ${cash_available:,.2f} available cash, cash payment maximizes savings"
    elif cash_ratio < 0.5 and "Month" in best_option.option:
        reasoning = f"Limited cash (${cash_available:,.2f}) makes financing the practical choice"
    elif "Seasonal" in best_option.option:
        reasoning = "Seasonal financing aligns payments with agricultural income cycles"
    else:
        reasoning = f"Balanced approach considering ${cash_available:,.2f} available cash and ${total_amount:,.2f} purchase"
    
    # Generate cash flow analysis if seasonal data available
    cash_flow_analysis = None
    if seasonal_cash_flow:
        cash_flow_analysis = {
            "monthly_impact": best_option.monthly_payment,
            "peak_cash_months": [month for month, flow in seasonal_cash_flow.items() if flow > 0],
            "low_cash_months": [month for month, flow in seasonal_cash_flow.items() if flow < 0],
            "alignment_score": 0.8  # Mock score
        }
    
    return FinancingRecommendation(
        recommended_option=best_option.option,
        reasoning=reasoning,
        key_benefits=best_option.pros[:3],
        considerations=best_option.cons[:2],
        cash_flow_analysis=cash_flow_analysis
    )

def _generate_financing_notes(
    total_amount: float,
    cash_available: float,
    credit_score: Optional[int],
    seasonal_cash_flow: Dict[str, float]
) -> List[str]:
    """Generate financing analysis notes."""
    notes = [
        "Interest rates are estimates and may vary by lender and current market conditions",
        "Consider seasonal cash flow patterns when choosing financing terms",
        "Equipment financing may offer tax advantages - consult your accountant"
    ]
    
    if credit_score:
        if credit_score >= 750:
            notes.append("Excellent credit score qualifies you for the best available rates")
        elif credit_score < 650:
            notes.append("Consider improving credit score for better financing terms in the future")
    else:
        notes.append("Providing credit score information can help secure better financing terms")
    
    if cash_available / total_amount > 0.5:
        notes.append("Strong cash position provides flexibility in financing choices")
    
    if seasonal_cash_flow:
        notes.append("Seasonal cash flow data helps optimize payment timing with farm income")
    
    notes.append("Early payment options may be available for financed purchases")
    
    return notes

def _find_regional_cooperatives(farm_location: FarmLocation) -> List[Dict[str, Any]]:
    """Find regional cooperatives (mock data for MVP)."""
    # Mock regional cooperative data
    cooperatives = [
        {
            "name": f"{farm_location.state} Farm Bureau Cooperative",
            "type": "State Agricultural Cooperative",
            "services": ["Group purchasing", "Equipment financing", "Crop insurance"],
            "membership_fee": 150,
            "contact": f"contact@{farm_location.state.lower()}farmbureau.org",
            "phone": "(555) 123-4567",
            "website": f"www.{farm_location.state.lower()}farmbureau.org",
            "estimated_savings": "10-20% on agricultural inputs"
        },
        {
            "name": f"{farm_location.county} County Farmers Cooperative",
            "type": "Local Cooperative",
            "services": ["Bulk purchasing", "Shared equipment", "Marketing"],
            "membership_fee": 75,
            "contact": f"info@{farm_location.county.lower()}coop.com",
            "phone": "(555) 234-5678",
            "website": f"www.{farm_location.county.lower()}coop.com",
            "estimated_savings": "8-15% on bulk orders"
        },
        {
            "name": "Regional Agricultural Alliance",
            "type": "Multi-State Cooperative",
            "services": ["Volume purchasing", "Logistics coordination", "Market intelligence"],
            "membership_fee": 200,
            "contact": "membership@regionalagriance.org",
            "phone": "(555) 345-6789",
            "website": "www.regionalagriance.org",
            "estimated_savings": "12-25% on large volume orders"
        }
    ]
    
    return cooperatives

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)