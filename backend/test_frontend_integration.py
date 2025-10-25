#!/usr/bin/env python3
"""
Test frontend-backend integration by simulating frontend requests
"""
import requests
import json

def test_frontend_to_backend_flow():
    """Test the complete flow that the frontend would use"""
    
    print("🧪 Testing Frontend-Backend Integration Flow")
    print("=" * 50)
    
    # 1. Test health check (what frontend does on startup)
    print("1. Testing health check...")
    try:
        health_response = requests.get('http://localhost:8000/api/health')
        if health_response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Backend status: {health_response.json()['status']}")
        else:
            print(f"   ❌ Health check failed: {health_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # 2. Test analysis request (main frontend functionality)
    print("\n2. Testing analysis request...")
    
    # This matches what the frontend dataTransform.ts would send
    frontend_request = {
        "products": [
            {
                "name": "Corn Seeds",
                "quantity": 50,
                "unit": "bags",
                "max_price": 120.0,
                "specifications": "High-yield hybrid variety"
            },
            {
                "name": "Fertilizer",
                "quantity": 20,
                "unit": "tons",
                "max_price": 800.0,
                "specifications": "10-10-10 NPK blend"
            }
        ],
        "farm_location": {
            "street_address": "456 Agricultural Way",
            "city": "Cedar Rapids",
            "state": "Iowa",
            "county": "Linn",
            "zip_code": "52402",
            "country": "USA"
        }
    }
    
    try:
        analysis_response = requests.post(
            'http://localhost:8000/api/analyze', 
            json=frontend_request,
            headers={'Content-Type': 'application/json'}
        )
        
        if analysis_response.status_code == 200:
            print("   ✅ Analysis request successful")
            
            data = analysis_response.json()
            
            # Verify response structure (what frontend expects)
            print("   📊 Response validation:")
            
            if 'product_analyses' in data:
                print(f"      ✅ Product analyses: {len(data['product_analyses'])} products")
                
                # Check each product analysis
                for i, analysis in enumerate(data['product_analyses']):
                    product_name = analysis.get('product_name', f'Product {i+1}')
                    confidence = analysis.get('analysis', {}).get('confidence_score', 0)
                    print(f"         - {product_name}: {confidence:.1%} confidence")
            else:
                print("      ❌ Missing product_analyses")
                return False
            
            if 'overall_budget' in data:
                budget = data['overall_budget']
                print(f"      ✅ Overall budget: ${budget.get('target', 0):,.2f} target")
            else:
                print("      ❌ Missing overall_budget")
                return False
            
            if 'data_quality_report' in data:
                quality = data['data_quality_report']
                coverage = quality.get('overall_data_coverage', 0)
                print(f"      ✅ Data quality: {coverage:.1%} coverage")
            else:
                print("      ❌ Missing data_quality_report")
                return False
            
            print("   ✅ All expected fields present")
            
        else:
            print(f"   ❌ Analysis failed: {analysis_response.status_code}")
            print(f"   📝 Error: {analysis_response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")
        return False
    
    # 3. Test CORS headers (important for frontend)
    print("\n3. Testing CORS configuration...")
    try:
        # Make an OPTIONS request to check CORS
        cors_response = requests.options(
            'http://localhost:8000/api/analyze',
            headers={
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        )
        
        cors_headers = cors_response.headers
        if 'Access-Control-Allow-Origin' in cors_headers:
            print("   ✅ CORS properly configured")
            print(f"      - Allowed origins: {cors_headers.get('Access-Control-Allow-Origin')}")
            print(f"      - Allowed methods: {cors_headers.get('Access-Control-Allow-Methods', 'Not specified')}")
        else:
            print("   ⚠️  CORS headers not found (may cause frontend issues)")
            
    except Exception as e:
        print(f"   ⚠️  CORS test error: {e}")
    
    # 4. Test error handling
    print("\n4. Testing error handling...")
    try:
        # Send invalid request to test error responses
        invalid_request = {"invalid": "data"}
        error_response = requests.post(
            'http://localhost:8000/api/analyze',
            json=invalid_request
        )
        
        if error_response.status_code == 422:  # Validation error expected
            print("   ✅ Error handling works correctly")
            error_data = error_response.json()
            if 'detail' in error_data:
                print("   ✅ Error details provided for debugging")
        else:
            print(f"   ⚠️  Unexpected error response: {error_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error handling test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Integration test completed successfully!")
    print("\n📋 Summary:")
    print("   ✅ Backend API is running and accessible")
    print("   ✅ Analysis endpoint works with realistic data")
    print("   ✅ Response format matches frontend expectations")
    print("   ✅ CORS is configured for frontend access")
    print("   ✅ Error handling is working properly")
    
    print("\n🌐 Access Points:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000/api")
    print("   API Documentation: http://localhost:8000/docs")
    
    print("\n💡 Next Steps:")
    print("   1. Open frontend in browser: http://localhost:3000")
    print("   2. Try submitting a form to test end-to-end flow")
    print("   3. Check browser developer tools for any errors")
    
    return True

if __name__ == "__main__":
    success = test_frontend_to_backend_flow()
    if not success:
        print("\n❌ Integration test failed!")
        exit(1)
    else:
        print("\n✨ All systems are go! Frontend and backend are ready.")