#!/usr/bin/env python3
"""
Simple integration test for frontend-backend communication
"""
import requests
import json
import sys

BACKEND_URL = 'http://localhost:8000/api'
FRONTEND_URL = 'http://localhost:3000'

def test_backend_health():
    """Test backend health endpoint"""
    try:
        print('Testing backend health endpoint...')
        response = requests.get(f'{BACKEND_URL}/health', timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f'✅ Backend health check passed: {data}')
        return True
    except Exception as e:
        print(f'❌ Backend health check failed: {e}')
        return False

def test_backend_analyze():
    """Test backend analyze endpoint"""
    try:
        print('Testing backend analyze endpoint...')
        
        test_request = {
            "products": [
                {
                    "name": "Corn Seeds",
                    "quantity": 100,
                    "max_price": 150.0,
                    "urgency": "medium"
                }
            ],
            "farm_location": {
                "state": "Iowa",
                "county": "Polk",
                "zip_code": "50309"
            }
        }
        
        response = requests.post(f'{BACKEND_URL}/analyze', json=test_request, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        print('✅ Backend analyze endpoint passed')
        print(f'Response structure:')
        print(f'  - Product analyses: {len(data.get("product_analyses", []))}')
        print(f'  - Overall budget: {"✓" if data.get("overall_budget") else "✗"}')
        print(f'  - Data quality report: {"✓" if data.get("data_quality_report") else "✗"}')
        return True
    except Exception as e:
        print(f'❌ Backend analyze endpoint failed: {e}')
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f'Error details: {error_data}')
            except:
                print(f'Error response: {e.response.text}')
        return False

def test_frontend_access():
    """Test frontend accessibility"""
    try:
        print('Testing frontend accessibility...')
        response = requests.get(FRONTEND_URL, timeout=5)
        response.raise_for_status()
        print('✅ Frontend is accessible')
        return True
    except Exception as e:
        print(f'❌ Frontend access failed: {e}')
        return False

def main():
    """Run integration tests"""
    print('🚀 Starting integration tests...\n')
    
    backend_health = test_backend_health()
    print()
    
    backend_analyze = test_backend_analyze()
    print()
    
    frontend_access = test_frontend_access()
    print()
    
    print('📊 Test Results:')
    print(f'Backend Health: {"✅" if backend_health else "❌"}')
    print(f'Backend Analyze: {"✅" if backend_analyze else "❌"}')
    print(f'Frontend Access: {"✅" if frontend_access else "❌"}')
    
    all_passed = backend_health and backend_analyze and frontend_access
    print(f'\n{"🎉" if all_passed else "⚠️"} Integration test {"PASSED" if all_passed else "FAILED"}')
    
    if all_passed:
        print('\n✨ Your frontend and backend are successfully integrated!')
        print('🌐 Frontend: http://localhost:3000')
        print('🔧 Backend API: http://localhost:8000/api')
        print('📚 API Docs: http://localhost:8000/docs')
    else:
        print('\n🔧 Troubleshooting tips:')
        if not backend_health:
            print('  - Check if backend server is running on port 8000')
        if not backend_analyze:
            print('  - Check backend logs for analysis errors')
        if not frontend_access:
            print('  - Check if frontend server is running on port 3000')
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())