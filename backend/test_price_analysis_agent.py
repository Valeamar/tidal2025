"""
Test for Price Analysis Agent

Simple test to verify the price analysis agent works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.models import ProductInput, FarmLocation
from app.intelligent_recommendations import IntelligentRecommendationEngine, RecommendationValidator


def test_intelligent_recommendations():
    """Test the intelligent recommendations system."""
    print("Testing Intelligent Recommendations System...")
    
    # Create test data
    product = ProductInput(
        name="corn seed",
        quantity=100,
        unit="bags",
        specifications="hybrid variety",
        max_price=250.0
    )
    
    farm_location = FarmLocation(
        street_address="123 Farm Road",
        city="Des Moines", 
        state="IA",
        county="Polk",
        zip_code="50309",
        country="USA"
    )
    
    # Test recommendation engine
    engine = IntelligentRecommendationEngine()
    
    # Mock data quality
    market_data_quality = {
        "overall_score": 0.7,
        "quote_count": 5,
        "supplier_data_found": True,
        "source_diversity": 3,
        "reliability_score": 0.8,
        "freshness_score": 0.9
    }
    
    # Mock economic analysis
    economic_analysis = {
        "seasonality_analysis": {
            "seasonal_savings_potential_pct": 8.5,
            "optimal_purchase_month": 2,
            "current_season_multiplier": 1.15
        },
        "supplier_evaluations": [
            {
                "supplier": "AgriCorp Supply",
                "effective_price": 240.0,
                "moq_met": False,
                "moq_shortfall": 50,
                "price_break_savings": 15.0,
                "lead_time": 14,
                "reliability_score": 0.9
            }
        ]
    }
    
    # Generate recommendations
    recommendations = engine.generate_comprehensive_recommendations(
        product=product,
        farm_location=farm_location,
        aws_bi_result=None,  # No AWS BI for this test
        market_data_quality=market_data_quality,
        economic_analysis=economic_analysis
    )
    
    print(f"Generated {len(recommendations)} recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.type.value}: {rec.description}")
        print(f"   Action: {rec.action_required}")
        print(f"   Savings: ${rec.potential_savings:.2f}")
        print(f"   Confidence: {rec.confidence:.2f}")
        print()
    
    # Test recommendation validation
    validator = RecommendationValidator()
    valid_recommendations = validator.validate_recommendations(
        recommendations, product
    )
    
    print(f"Validated {len(valid_recommendations)} recommendations")
    
    print("✅ Intelligent Recommendations System test passed!")


if __name__ == "__main__":
    test_intelligent_recommendations()