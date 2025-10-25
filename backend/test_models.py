#!/usr/bin/env python3
"""
Simple test script to verify the Pydantic models work correctly.
This validates the core data model classes implementation.
"""

from app.models import (
    ProductInput, FarmInfo, FarmLocation, PriceAnalysis, 
    SupplierRecommendation, EffectiveCost, OptimizationRecommendation,
    OptimizationType
)
from datetime import datetime

def test_product_input():
    """Test ProductInput model validation"""
    # Valid product input
    product = ProductInput(
        name="Corn Seeds",
        quantity=50.0,
        unit="bags",
        specifications="Non-GMO, 90% germination rate",
        preferred_brands=["Pioneer", "DeKalb"],
        max_price=150.0
    )
    assert product.name == "Corn Seeds"
    assert product.quantity == 50.0
    print("✅ ProductInput validation passed")

def test_farm_info():
    """Test FarmInfo and FarmLocation models"""
    location = FarmLocation(
        street_address="123 Farm Road",
        city="Ames",
        state="Iowa",
        county="Story County",
        zip_code="50010",
        country="USA"
    )
    
    farm = FarmInfo(
        location=location,
        farm_size=500.0,
        crop_types=["corn", "soybeans"]
    )
    assert farm.location.city == "Ames"
    assert farm.farm_size == 500.0
    print("✅ FarmInfo and FarmLocation validation passed")

def test_effective_cost():
    """Test EffectiveCost (PriceRanges) model"""
    cost = EffectiveCost(
        p10=120.0,
        p25=125.0,
        p35=130.0,
        p50=135.0,
        p90=150.0
    )
    assert cost.p25 == 125.0
    assert cost.p90 == 150.0
    print("✅ EffectiveCost (PriceRanges) validation passed")

def test_supplier_recommendation():
    """Test SupplierRecommendation model with optional fields"""
    # Required fields only
    supplier1 = SupplierRecommendation(
        name="AgriSupply Co",
        price=145.50
    )
    assert supplier1.name == "AgriSupply Co"
    assert supplier1.delivery_terms is None
    
    # With optional fields
    supplier2 = SupplierRecommendation(
        name="Farm Direct",
        price=142.00,
        delivery_terms="FOB destination",
        lead_time=7,
        reliability=0.95,
        moq=10,
        contact_info="sales@farmdirect.com",
        location="Des Moines, IA"
    )
    assert supplier2.reliability == 0.95
    assert supplier2.moq == 10
    print("✅ SupplierRecommendation validation passed")

def test_optimization_recommendation():
    """Test OptimizationRecommendation model"""
    recommendation = OptimizationRecommendation(
        type=OptimizationType.BULK_DISCOUNT,
        description="Purchase 100+ bags for 10% discount",
        potential_savings=750.0,
        action_required="Increase order quantity to 100 bags",
        confidence=0.85
    )
    assert recommendation.type == OptimizationType.BULK_DISCOUNT
    assert recommendation.potential_savings == 750.0
    print("✅ OptimizationRecommendation validation passed")

def test_price_analysis():
    """Test complete PriceAnalysis model"""
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
    
    assert analysis.product_name == "Corn Seeds"
    assert analysis.confidence_score == 0.82
    assert len(analysis.suppliers) == 1
    assert len(analysis.recommendations) == 1
    print("✅ PriceAnalysis validation passed")

def main():
    """Run all model validation tests"""
    print("Testing Pydantic data models...")
    
    test_product_input()
    test_farm_info()
    test_effective_cost()
    test_supplier_recommendation()
    test_optimization_recommendation()
    test_price_analysis()
    
    print("\n🎉 All core data model classes validated successfully!")
    print("✅ ProductInput - with required/optional field validation")
    print("✅ FarmInfo - with nested FarmLocation")
    print("✅ EffectiveCost - price ranges (p10-p90 percentiles)")
    print("✅ SupplierRecommendation - with optional supplier fields")
    print("✅ OptimizationRecommendation - with enum types")
    print("✅ PriceAnalysis - complete model integration")

if __name__ == "__main__":
    main()