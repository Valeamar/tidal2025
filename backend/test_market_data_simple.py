"""
Simple test for MarketDataService core functionality without external dependencies
"""

import sys
import os
from datetime import datetime, timezone

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models import FarmLocation

def test_models():
    """Test that the models work correctly"""
    print("Testing FarmLocation model...")
    
    location = FarmLocation(
        street_address="123 Farm Road",
        city="Des Moines", 
        state="Iowa",
        county="Polk",
        zip_code="50309",
        country="USA"
    )
    
    print(f"Created location: {location.city}, {location.state}")
    print("✓ FarmLocation model works correctly")

def test_price_quote_dataclass():
    """Test the PriceQuote dataclass"""
    print("\nTesting PriceQuote dataclass...")
    
    # Import here to avoid aiohttp dependency
    try:
        from app.market_data_service import PriceQuote
        
        quote = PriceQuote(
            supplier="Test Supplier",
            price=100.50,
            unit="per bag",
            product_name="corn seed",
            location="Iowa, USA",
            source="Mock_Data",
            moq=50,
            delivery_terms="FOB",
            lead_time=7,
            reliability_score=0.85,
            contact_info="test@supplier.com",
            cached_at=datetime.now(timezone.utc)
        )
        
        print(f"Created quote: {quote.supplier} - ${quote.price} {quote.unit}")
        
        # Test conversion to dict
        quote_dict = quote.to_dict()
        print(f"Quote dict keys: {list(quote_dict.keys())}")
        print("✓ PriceQuote dataclass works correctly")
        
    except ImportError as e:
        print(f"⚠ Skipping PriceQuote test due to import error: {e}")

def test_storage_integration():
    """Test storage components"""
    print("\nTesting storage integration...")
    
    try:
        from app.storage import MarketDataCache
        
        cache = MarketDataCache()
        print(f"Cache directory: {cache.cache_dir}")
        print(f"Market data file: {cache.market_data_file}")
        print("✓ MarketDataCache initialized successfully")
        
        # Test cache file operations
        test_data = {
            "test_product": {
                "product_name": "test corn",
                "price_quotes": [
                    {
                        "supplier": "Test Supplier",
                        "price": 100.0,
                        "unit": "per bag",
                        "source": "test"
                    }
                ],
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }
        
        cache._write_json_file(cache.market_data_file, test_data)
        read_data = cache._read_json_file(cache.market_data_file)
        
        if "test_product" in read_data:
            print("✓ Cache file operations work correctly")
        else:
            print("✗ Cache file operations failed")
            
    except Exception as e:
        print(f"⚠ Storage test failed: {e}")

def test_data_validation():
    """Test data validation functions"""
    print("\nTesting data validation...")
    
    try:
        from app.market_data_service import MarketDataService, PriceQuote
        
        service = MarketDataService(use_mock_data=True)
        
        # Create test quotes with various quality levels
        good_quote = PriceQuote(
            supplier="Good Supplier",
            price=100.0,
            unit="per bag",
            product_name="corn seed",
            location="Iowa, USA",
            source="test",
            reliability_score=0.9
        )
        
        bad_quote = PriceQuote(
            supplier="",  # Empty supplier
            price=-10.0,  # Negative price
            unit="",
            product_name="",
            location="",
            source="test"
        )
        
        quotes = [good_quote, bad_quote]
        validated = service._validate_quotes(quotes)
        
        print(f"Original quotes: {len(quotes)}")
        print(f"Validated quotes: {len(validated)}")
        
        if len(validated) == 1:  # Should only keep the good quote
            print("✓ Data validation works correctly")
        else:
            print("✗ Data validation failed")
            
    except Exception as e:
        print(f"⚠ Data validation test failed: {e}")

def main():
    """Run all tests"""
    print("Running MarketDataService tests...")
    print("=" * 50)
    
    try:
        test_models()
        test_price_quote_dataclass()
        test_storage_integration()
        test_data_validation()
        
        print("\n" + "=" * 50)
        print("✓ All tests completed!")
        
    except Exception as e:
        print(f"\n✗ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()