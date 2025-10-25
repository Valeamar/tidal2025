"""
Test script for MarketDataService functionality
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Test with mock data only to avoid aiohttp dependency issues
from app.models import FarmLocation

async def test_market_data_service():
    """Test the MarketDataService with mock data"""
    print("Testing MarketDataService...")
    
    # Create test location
    location = FarmLocation(
        street_address="123 Farm Road",
        city="Des Moines",
        state="Iowa",
        county="Polk",
        zip_code="50309",
        country="USA"
    )
    
    # Test with mock data
    service = MarketDataService(use_mock_data=True)
    
    print(f"Initialized service with {len(service.data_sources)} data sources")
    
    # Test getting prices for a product
    product_name = "corn seed"
    print(f"\nGetting prices for '{product_name}'...")
    
    quotes = await service.get_current_prices(product_name, location)
    print(f"Found {len(quotes)} price quotes:")
    
    for i, quote in enumerate(quotes[:3]):  # Show first 3 quotes
        print(f"  {i+1}. {quote.supplier}: ${quote.price:.2f} {quote.unit}")
        print(f"     Source: {quote.source}, Reliability: {quote.reliability_score}")
    
    # Test availability report
    print(f"\nGetting availability report for '{product_name}'...")
    availability = await service.get_product_availability(product_name, location)
    print(f"Total sources: {availability['total_sources']}")
    print(f"Sources with data: {availability['sources_with_data']}")
    print(f"Total quotes: {availability['total_quotes']}")
    if availability['price_range']:
        print(f"Price range: ${availability['price_range']['min']:.2f} - ${availability['price_range']['max']:.2f}")
    
    # Test cache stats
    print(f"\nCache statistics:")
    cache_stats = service.get_cache_stats()
    print(f"Cached products: {cache_stats['total_cached_products']}")
    print(f"Total quotes: {cache_stats['total_price_quotes']}")
    print(f"Mock data enabled: {cache_stats['mock_data_enabled']}")

async def test_enhanced_service():
    """Test the EnhancedMarketDataService with graceful data handling"""
    print("\n" + "="*50)
    print("Testing EnhancedMarketDataService...")
    
    # Create test location
    location = FarmLocation(
        street_address="456 Agriculture Lane",
        city="Cedar Rapids", 
        state="Iowa",
        county="Linn",
        zip_code="52402",
        country="USA"
    )
    
    # Test with enhanced service
    enhanced_service = EnhancedMarketDataService(use_mock_data=True)
    
    # Test multiple products with partial analysis
    products = ["corn seed", "soybean seed", "fertilizer", "diesel fuel", "unknown_product"]
    
    print(f"\nAnalyzing {len(products)} products with fallback handling...")
    
    results = await enhanced_service.analyze_product_list_with_fallbacks(products, location)
    
    if "error" in results:
        print(f"Analysis failed: {results['message']}")
        return
    
    # Display results
    analysis = results["analysis_results"]
    recommendations = results["budget_recommendations"]
    
    print(f"\nAnalysis Summary:")
    print(f"Total products: {analysis['total_products']}")
    print(f"Successful analyses: {analysis['successful_analyses']}")
    print(f"Partial analyses: {analysis['partial_analyses']}")
    print(f"Failed analyses: {analysis['failed_analyses']}")
    
    print(f"\nData Quality:")
    quality = results["data_quality_summary"]
    print(f"Overall confidence: {quality['overall_confidence']:.2f}")
    print(f"Data coverage: {quality['data_coverage']:.1f}%")
    print(f"Products with reliable data: {quality['products_with_reliable_data']}")
    print(f"Products needing manual research: {quality['products_needing_manual_research']}")
    
    print(f"\nBudget Recommendations:")
    print(f"Approach: {recommendations['budgeting_approach']}")
    print(f"Confidence level: {recommendations['confidence_level']}")
    
    if recommendations['recommended_actions']:
        print("Recommended actions:")
        for action in recommendations['recommended_actions']:
            print(f"  - {action}")
    
    if recommendations['risk_factors']:
        print("Risk factors:")
        for risk in recommendations['risk_factors']:
            print(f"  - {risk}")
    
    print(f"\nNext Steps:")
    for step in results["next_steps"]:
        print(f"  - {step}")

async def main():
    """Run all tests"""
    try:
        await test_market_data_service()
        await test_enhanced_service()
        print("\n" + "="*50)
        print("All tests completed successfully!")
    
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())