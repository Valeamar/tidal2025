from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import logging
from typing import Dict, Any

from .models import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    HealthResponse, 
    ErrorResponse, 
    ErrorDetail
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Farmer Budget Optimizer API",
    description="AI-powered agricultural input price optimization service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = str(uuid.uuid4())
    logger.error(f"Request {request_id} failed: {str(exc)}", exc_info=True)
    
    error_response = ErrorResponse(
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            retryable=False
        ),
        request_id=request_id,
        timestamp=datetime.now()
    )
    
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )

# Health check endpoint
@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify the API is running.
    Returns current timestamp and status.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now()
    )

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