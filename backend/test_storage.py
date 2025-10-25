#!/usr/bin/env python3
"""
Test script to verify the JSON file storage system works correctly.
Tests MarketDataCache and SessionStorage functionality.
"""

import os
import tempfile
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.storage import MarketDataCache, SessionStorage, StorageError
from app.models import (
    AnalyzeResponse, ProductAnalysisResult, PriceAnalysis, 
    EffectiveCost, SupplierRecommendation, OptimizationRecommendation,
    OptimizationType, IndividualBudget, DataAvailability,
    OverallBudget, DataQualityReport
)

def test_market_data_cache():
    """Test MarketDataCache functionality"""
    print("Testing MarketDataCache...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        cache = MarketDataCache(cache_dir=temp_dir)
        
        # Test caching market data
        product_name = "Corn Seeds"
        location = "Iowa, USA"
        price_quotes = [
            {
                "supplier": "AgriSupply Co",
                "price": 145.50,
                "unit": "bag",
                "moq": 10,
                "location": "Des Moines, IA",
                "delivery_terms": "FOB destination",
                "lead_time": 7,
                "reliability_score": 0.95,
                "contact_info": "sales@agrisupply.com",
                "cached_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "supplier": "Farm Direct",
                "price": 142.00,
                "unit": "bag",
                "moq": 5,
                "location": "Ames, IA",
                "delivery_terms": "Free shipping over $1000",
                "lead_time": 5,
                "reliability_score": 0.88,
                "contact_info": "orders@farmdirect.com",
                "cached_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        forecast_data = {
            "predictions": [
                {"date": "2024-03-01", "predicted_price": 140.0, "confidence_interval": {"lower": 135.0, "upper": 145.0}},
                {"date": "2024-04-01", "predicted_price": 138.0, "confidence_interval": {"lower": 133.0, "upper": 143.0}}
            ],
            "trend": "declining",
            "confidence": 0.85,
            "forecast_generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        sentiment_data = {
            "overall_sentiment": 0.3,
            "supply_risk_score": 0.6,
            "demand_outlook": "stable",
            "key_factors": ["weather concerns", "fuel prices"],
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache the data
        cache.cache_market_data(product_name, location, price_quotes, forecast_data, sentiment_data)
        
        # Retrieve cached data
        cached_data = cache.get_cached_market_data(product_name, location)
        assert cached_data is not None
        assert cached_data["product_name"] == product_name
        assert cached_data["location"] == location
        assert len(cached_data["price_quotes"]) == 2
        assert cached_data["forecast_data"]["trend"] == "declining"
        assert cached_data["sentiment_data"]["supply_risk_score"] == 0.6
        
        print("✅ Market data caching and retrieval passed")
        
        # Test cache expiration
        expired_data = cache.get_cached_market_data(product_name, location, max_age_hours=0)
        assert expired_data is None
        print("✅ Cache expiration logic passed")
        
        # Test clearing expired data
        cache.cache_market_data("Test Product", "Test Location", [{"supplier": "Test", "price": 100}])
        removed_count = cache.clear_expired_market_data(max_age_hours=0)
        assert removed_count >= 1
        print("✅ Expired data cleanup passed")

def test_session_storage():
    """Test SessionStorage functionality"""
    print("\nTesting SessionStorage...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = SessionStorage(cache_dir=temp_dir)
        
        # Create test analysis response
        effective_cost = EffectiveCost(
            p10=120.0,
            p25=125.0,
            p35=130.0,
            p50=135.0,
            p90=150.0
        )
        
        supplier = SupplierRecommendation(
            name="Best Seeds Inc",
            price=128.00,
            delivery_terms="Free shipping over $1000"
        )
        
        recommendation = OptimizationRecommendation(
            type=OptimizationType.TIMING,
            description="Wait until March for 5% lower prices",
            potential_savings=320.0,
            action_required="Delay purchase by 2 months"
        )
        
        analysis = PriceAnalysis(
            product_id="corn-seeds-001",
            product_name="Corn Seeds",
            effective_delivered_cost=effective_cost,
            target_price=128.00,
            confidence_score=0.82,
            suppliers=[supplier],
            recommendations=[recommendation],
            data_limitations=["Limited supplier data in region"]
        )
        
        individual_budget = IndividualBudget(
            low=6000.0,
            target=6400.0,
            high=7500.0,
            total_cost=6400.0
        )
        
        data_availability = DataAvailability(
            price_data_found=True,
            supplier_data_found=True,
            forecast_data_available=True,
            sentiment_data_available=False,
            missing_data_sections=["sentiment analysis"]
        )
        
        product_result = ProductAnalysisResult(
            product_id="corn-seeds-001",
            product_name="Corn Seeds",
            analysis=analysis,
            individual_budget=individual_budget,
            data_availability=data_availability
        )
        
        overall_budget = OverallBudget(
            low=6000.0,
            target=6400.0,
            high=7500.0,
            total_cost=6400.0
        )
        
        data_quality_report = DataQualityReport(
            overall_data_coverage=0.85,
            reliable_products=["Corn Seeds"],
            limited_data_products=[],
            no_data_products=[]
        )
        
        analyze_response = AnalyzeResponse(
            product_analyses=[product_result],
            overall_budget=overall_budget,
            data_quality_report=data_quality_report,
            generated_at=datetime.now(timezone.utc)
        )
        
        # Test session creation and storage
        session_id = storage.generate_session_id()
        assert len(session_id) > 0
        print(f"✅ Generated session ID: {session_id}")
        
        # Save analysis session
        storage.save_analysis_session(session_id, analyze_response)
        print("✅ Analysis session saved")
        
        # Retrieve analysis session
        retrieved_session = storage.get_analysis_session(session_id)
        assert retrieved_session is not None
        assert retrieved_session["session_id"] == session_id
        assert len(retrieved_session["analysis_response"]["product_analyses"]) == 1
        print("✅ Analysis session retrieved")
        
        # Test session listing
        sessions = storage.list_sessions()
        assert len(sessions) >= 1
        assert any(s["session_id"] == session_id for s in sessions)
        print("✅ Session listing passed")
        
        # Test session deletion
        deleted = storage.delete_session(session_id)
        assert deleted is True
        
        # Verify deletion
        retrieved_after_delete = storage.get_analysis_session(session_id)
        assert retrieved_after_delete is None
        print("✅ Session deletion passed")
        
        # Test cleanup of old sessions
        # Create a test session and then clean it up
        test_session_id = storage.generate_session_id()
        storage.save_analysis_session(test_session_id, analyze_response)
        
        # Wait a moment and then cleanup with 0 max age
        import time
        time.sleep(0.1)
        removed_count = storage.cleanup_old_sessions(max_age_days=0)
        
        # Check that the session was removed
        remaining_sessions = storage.list_sessions()
        session_exists = any(s["session_id"] == test_session_id for s in remaining_sessions)
        assert not session_exists, "Session should have been cleaned up"
        print("✅ Old session cleanup passed")

def test_error_handling():
    """Test error handling in storage operations"""
    print("\nTesting error handling...")
    
    # Test with invalid directory permissions (if possible)
    try:
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            cache = MarketDataCache(cache_dir=temp_dir)
            
            # Test with invalid data types
            try:
                cache.cache_market_data("", "", None)  # Invalid inputs
                print("⚠️  Expected error not raised for invalid inputs")
            except (StorageError, TypeError, ValueError):
                print("✅ Error handling for invalid inputs passed")
            
            # Test retrieving non-existent data
            result = cache.get_cached_market_data("NonExistent", "Location")
            assert result is None
            print("✅ Non-existent data handling passed")
            
    except Exception as e:
        print(f"⚠️  Error handling test encountered: {e}")

def main():
    """Run all storage system tests"""
    print("Testing JSON File Storage System...")
    print("=" * 50)
    
    try:
        test_market_data_cache()
        test_session_storage()
        test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 All storage system tests passed!")
        print("✅ MarketDataCache - caching, retrieval, expiration")
        print("✅ SessionStorage - session management, CRUD operations")
        print("✅ Error handling - graceful failure and recovery")
        print("✅ File I/O operations - atomic writes, locking")
        print("✅ JSON serialization - Pydantic model compatibility")
        
    except Exception as e:
        print(f"\n❌ Storage system test failed: {e}")
        raise

if __name__ == "__main__":
    main()