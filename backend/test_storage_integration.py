#!/usr/bin/env python3
"""
Test script to verify the storage system integration with FastAPI.
"""

import asyncio
from app.main import app
from app.storage_utils import get_storage_manager
from app.models import (
    AnalyzeResponse, ProductAnalysisResult, PriceAnalysis, 
    EffectiveCost, SupplierRecommendation, OptimizationType,
    OptimizationRecommendation, IndividualBudget, DataAvailability,
    OverallBudget, DataQualityReport
)
from datetime import datetime, timezone

async def test_storage_integration():
    """Test the storage system integration"""
    print("Testing storage system integration...")
    
    # Get storage manager
    storage_manager = get_storage_manager()
    
    # Create test data
    effective_cost = EffectiveCost(
        p10=120.0,
        p25=125.0,
        p35=130.0,
        p50=135.0,
        p90=150.0
    )
    
    supplier = SupplierRecommendation(
        name="Test Supplier",
        price=128.00,
        delivery_terms="Test terms"
    )
    
    recommendation = OptimizationRecommendation(
        type=OptimizationType.TIMING,
        description="Test recommendation",
        potential_savings=100.0,
        action_required="Test action"
    )
    
    analysis = PriceAnalysis(
        product_id="test-001",
        product_name="Test Product",
        effective_delivered_cost=effective_cost,
        target_price=128.00,
        confidence_score=0.85,
        suppliers=[supplier],
        recommendations=[recommendation],
        data_limitations=[]
    )
    
    individual_budget = IndividualBudget(
        low=1000.0,
        target=1200.0,
        high=1500.0,
        total_cost=1200.0
    )
    
    data_availability = DataAvailability(
        price_data_found=True,
        supplier_data_found=True,
        forecast_data_available=False,
        sentiment_data_available=False,
        missing_data_sections=[]
    )
    
    product_result = ProductAnalysisResult(
        product_id="test-001",
        product_name="Test Product",
        analysis=analysis,
        individual_budget=individual_budget,
        data_availability=data_availability
    )
    
    overall_budget = OverallBudget(
        low=1000.0,
        target=1200.0,
        high=1500.0,
        total_cost=1200.0
    )
    
    data_quality_report = DataQualityReport(
        overall_data_coverage=0.85,
        reliable_products=["Test Product"],
        limited_data_products=[],
        no_data_products=[]
    )
    
    analyze_response = AnalyzeResponse(
        product_analyses=[product_result],
        overall_budget=overall_budget,
        data_quality_report=data_quality_report,
        generated_at=datetime.now(timezone.utc)
    )
    
    # Test saving analysis result
    session_id = storage_manager.save_analysis_result(analyze_response)
    print(f"✅ Saved analysis result with session ID: {session_id}")
    
    # Test retrieving analysis result
    retrieved_result = storage_manager.get_analysis_result(session_id)
    assert retrieved_result is not None
    assert retrieved_result.product_analyses[0].product_name == "Test Product"
    print("✅ Retrieved analysis result successfully")
    
    # Test listing sessions
    sessions = storage_manager.list_recent_analyses()
    assert len(sessions) >= 1
    print(f"✅ Listed {len(sessions)} recent sessions")
    
    # Test storage stats
    stats = storage_manager.get_storage_stats()
    assert "total_sessions" in stats
    print(f"✅ Generated storage stats: {stats['total_sessions']} total sessions")
    
    # Test cleanup
    cleanup_stats = storage_manager.cleanup_old_data()
    print(f"✅ Cleanup completed: {cleanup_stats}")
    
    print("\n🎉 Storage system integration test passed!")

if __name__ == "__main__":
    asyncio.run(test_storage_integration())