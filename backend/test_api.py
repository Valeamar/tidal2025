#!/usr/bin/env python3
"""
Test the API endpoints directly
"""
import requests
import json

def test_health():
    try:
        response = requests.get('http://localhost:8000/api/health')
        print(f"Health endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health test failed: {e}")
        return False

def test_analyze():
    try:
        test_data = {
            "products": [
                {
                    "name": "Corn Seeds",
                    "quantity": 100,
                    "unit": "bags",
                    "max_price": 150.0,
                    "specifications": "Non-GMO hybrid corn seeds"
                }
            ],
            "farm_location": {
                "street_address": "123 Farm Road",
                "city": "Des Moines",
                "state": "Iowa",
                "county": "Polk", 
                "zip_code": "50309",
                "country": "USA"
            }
        }
        
        response = requests.post('http://localhost:8000/api/analyze', json=test_data)
        print(f"Analyze endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Analysis successful!")
            print(f"Products analyzed: {len(data.get('product_analyses', []))}")
            print(f"Overall budget present: {bool(data.get('overall_budget'))}")
            return True
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Analyze test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing API endpoints...")
    
    health_ok = test_health()
    print()
    
    analyze_ok = test_analyze()
    print()
    
    if health_ok and analyze_ok:
        print("✅ All tests passed! Backend is working correctly.")
    else:
        print("❌ Some tests failed.")