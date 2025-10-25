#!/usr/bin/env python3
"""
Test advanced features of the backend API
"""
import requests
import json
from datetime import datetime, timedelta

def test_price_alerts():
    """Test price alert functionality"""
    print("🔔 Testing Price Alert Feature...")
    
    alert_request = {
        "product_name": "Corn Seeds",
        "target_price": 100.0,
        "farm_location": {
            "street_address": "123 Farm Road",
            "city": "Des Moines",
            "state": "Iowa",
            "county": "Polk",
            "zip_code": "50309",
            "country": "USA"
        },
        "contact_email": "farmer@example.com",
        "alert_type": "price_drop",
        "threshold_percentage": 5.0,
        "expiry_date": (datetime.now() + timedelta(days=30)).isoformat()
    }
    
    try:
        response = requests.post('http://localhost:8000/api/price-alerts', json=alert_request)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Price alert created: {data['alert_id']}")
            print(f"   📊 Monitoring status: {data['monitoring_status']}")
            return True
        else:
            print(f"   ❌ Price alert failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Price alert error: {e}")
        return False

def test_bundling_analysis():
    """Test bundling analysis functionality"""
    print("\n📦 Testing Bundling Analysis Feature...")
    
    bundling_request = {
        "products": [
            {
                "name": "Corn Seeds",
                "quantity": 50,
                "unit": "bags",
                "max_price": 120.0
            },
            {
                "name": "Fertilizer",
                "quantity": 20,
                "unit": "tons",
                "max_price": 800.0
            }
        ],
        "farm_location": {
            "street_address": "123 Farm Road",
            "city": "Des Moines",
            "state": "Iowa",
            "county": "Polk",
            "zip_code": "50309",
            "country": "USA"
        },
        "max_suppliers": 5,
        "include_group_purchasing": True
    }
    
    try:
        response = requests.post('http://localhost:8000/api/bundling-analysis', json=bundling_request)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Bundling analysis completed")
            print(f"   📊 Opportunities found: {data['total_opportunities']}")
            print(f"   💰 Max potential savings: ${data['max_potential_savings']:,.2f}")
            if data['recommended_bundle']:
                print(f"   🎯 Recommended: {data['recommended_bundle']['supplier']}")
            return True
        else:
            print(f"   ❌ Bundling analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Bundling analysis error: {e}")
        return False

def test_financing_analysis():
    """Test financing analysis functionality"""
    print("\n💳 Testing Financing Analysis Feature...")
    
    financing_request = {
        "total_purchase_amount": 15000.0,
        "cash_available": 8000.0,
        "credit_score": 720,
        "preferred_terms_months": 12,
        "risk_tolerance": "moderate",
        "seasonal_cash_flow": {
            "spring": -5000,
            "summer": 2000,
            "fall": 15000,
            "winter": -2000
        }
    }
    
    try:
        response = requests.post('http://localhost:8000/api/financing-analysis', json=financing_request)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Financing analysis completed")
            print(f"   📊 Options available: {len(data['financing_options'])}")
            if data['recommendation']:
                print(f"   🎯 Recommended: {data['recommendation']['recommended_option']}")
            return True
        else:
            print(f"   ❌ Financing analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Financing analysis error: {e}")
        return False

def test_storage_endpoints():
    """Test storage management endpoints"""
    print("\n💾 Testing Storage Management...")
    
    try:
        # Test storage stats
        stats_response = requests.get('http://localhost:8000/api/storage/stats')
        if stats_response.status_code == 200:
            print("   ✅ Storage stats accessible")
        
        # Test recent sessions
        sessions_response = requests.get('http://localhost:8000/api/storage/sessions')
        if sessions_response.status_code == 200:
            data = sessions_response.json()
            print(f"   ✅ Recent sessions: {data['count']} found")
        
        return True
    except Exception as e:
        print(f"   ❌ Storage test error: {e}")
        return False

def main():
    """Run all advanced feature tests"""
    print("🚀 Testing Advanced Backend Features")
    print("=" * 50)
    
    results = []
    
    # Test each advanced feature
    results.append(test_price_alerts())
    results.append(test_bundling_analysis())
    results.append(test_financing_analysis())
    results.append(test_storage_endpoints())
    
    print("\n" + "=" * 50)
    print("📊 Advanced Features Test Results:")
    
    features = ["Price Alerts", "Bundling Analysis", "Financing Analysis", "Storage Management"]
    for i, (feature, result) in enumerate(zip(features, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {feature}: {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 All advanced features are working correctly!")
        print("\n💡 Available Advanced Features:")
        print("   🔔 Price Alerts - Monitor target prices")
        print("   📦 Bundling Analysis - Find bulk purchase opportunities")
        print("   💳 Financing Analysis - Compare payment options")
        print("   💾 Storage Management - Track analysis history")
        print("   🤝 Group Purchasing - Cooperative buying programs")
    else:
        print("\n⚠️  Some advanced features need attention")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ Backend is fully functional with all advanced features!")
    else:
        print("\n🔧 Some features may need debugging")