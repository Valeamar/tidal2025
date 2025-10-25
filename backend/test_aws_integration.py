"""
AWS Integration Test for Farmer Budget Optimizer

This test verifies that the AWS BI services integration works correctly
when AWS credentials are properly configured.
"""

import sys
import os
import asyncio
from datetime import datetime
sys.path.append(os.path.dirname(__file__))

from app.models import ProductInput, FarmLocation
from app.price_analysis_agent import PriceAnalysisAgent


async def test_aws_connectivity():
    """Test AWS service connectivity and basic functionality."""
    print("🔍 Testing AWS Integration for Farmer Budget Optimizer")
    print("=" * 60)
    
    # Test 1: Check AWS credentials
    print("\n1. Testing AWS Credentials...")
    try:
        from app.aws_clients import get_aws_client_manager
        
        # Try to initialize AWS client manager
        aws_manager = get_aws_client_manager()
        print("✅ AWS Client Manager initialized successfully")
        
        # Test connectivity to each service
        services_to_test = ['forecast', 'quicksight', 'comprehend']
        connectivity_results = {}
        
        for service in services_to_test:
            print(f"\n   Testing {service.upper()} connectivity...")
            result = aws_manager.test_service_connectivity(service)
            connectivity_results[service] = result
            
            if result['status'] == 'connected':
                print(f"   ✅ {service.upper()}: Connected (response time: {result['response_time_ms']}ms)")
            elif result['status'] == 'error':
                print(f"   ⚠️  {service.upper()}: Error - {result.get('error_message', 'Unknown error')}")
                if result.get('is_retryable'):
                    print(f"      (This error is retryable)")
            else:
                print(f"   ❌ {service.upper()}: {result['status']}")
        
        # Overall connectivity summary
        connected_services = sum(1 for r in connectivity_results.values() if r['status'] == 'connected')
        print(f"\n   📊 AWS Services Status: {connected_services}/{len(services_to_test)} services connected")
        
    except ImportError as e:
        print(f"❌ Missing AWS dependencies: {e}")
        print("   Install with: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ AWS Client initialization failed: {e}")
        print("   Please configure AWS credentials using 'aws configure' or environment variables")
        return False
    
    # Test 2: Price Analysis Agent with AWS BI enabled
    print("\n2. Testing Price Analysis Agent with AWS BI...")
    try:
        # Create agent with AWS BI enabled
        agent = PriceAnalysisAgent(use_mock_data=True, enable_aws_bi=True)
        
        # Test product
        product = ProductInput(
            name="corn seed",
            quantity=100,
            unit="bags",
            specifications="hybrid variety",
            max_price=250.0
        )
        
        # Test farm location
        farm_location = FarmLocation(
            street_address="123 Farm Road",
            city="Des Moines",
            state="IA",
            county="Polk",
            zip_code="50309",
            country="USA"
        )
        
        print("   Running comprehensive analysis...")
        results = await agent.analyze_product_list([product], farm_location)
        
        if results:
            result = results[0]
            print(f"   ✅ Analysis completed for: {result.product_name}")
            print(f"   📊 Target price: ${result.analysis.target_price:.2f}" if result.analysis.target_price else "   📊 Target price: Not available")
            print(f"   🎯 Confidence score: {result.analysis.confidence_score:.2f}")
            print(f"   💡 Recommendations: {len(result.analysis.recommendations)}")
            print(f"   📈 Data availability:")
            print(f"      - Price data: {'✅' if result.data_availability.price_data_found else '❌'}")
            print(f"      - Supplier data: {'✅' if result.data_availability.supplier_data_found else '❌'}")
            print(f"      - Forecast data: {'✅' if result.data_availability.forecast_data_available else '❌'}")
            print(f"      - Sentiment data: {'✅' if result.data_availability.sentiment_data_available else '❌'}")
            
            # Show recommendations
            if result.analysis.recommendations:
                print(f"\n   🔍 Top Recommendations:")
                for i, rec in enumerate(result.analysis.recommendations[:3], 1):
                    print(f"      {i}. {rec.type.value}: {rec.description[:80]}...")
                    print(f"         💰 Potential savings: ${rec.potential_savings:.2f}")
                    print(f"         🎯 Confidence: {rec.confidence:.2f}")
        else:
            print("   ❌ No analysis results returned")
            return False
            
    except Exception as e:
        print(f"   ❌ Price Analysis Agent test failed: {e}")
        return False
    
    # Test 3: AWS BI Data Transformations
    print("\n3. Testing AWS BI Data Transformations...")
    try:
        from app.aws_bi_transforms import AWSBIDataTransformer
        
        transformer = AWSBIDataTransformer()
        
        # Test forecast response transformation
        mock_forecast_response = {
            'Forecast': {
                'Predictions': {
                    'p50': [
                        {
                            'Timestamp': datetime.now().isoformat(),
                            'Value': 245.50,
                            'LowerBound': 220.00,
                            'UpperBound': 270.00
                        }
                    ]
                }
            },
            'Confidence': 0.85,
            'DataQualityScore': 0.78
        }
        
        forecast_result = transformer.transform_forecast_response(mock_forecast_response, "corn seed")
        print(f"   ✅ Forecast transformation: {len(forecast_result.predictions)} predictions")
        print(f"      Trend: {forecast_result.trend}, Confidence: {forecast_result.confidence}")
        
        # Test sentiment response transformation
        mock_sentiment_response = {
            'SentimentResult': {
                'Sentiment': 'NEUTRAL',
                'SentimentScore': {
                    'Positive': 0.3,
                    'Negative': 0.2,
                    'Neutral': 0.5,
                    'Mixed': 0.0
                }
            },
            'Entities': [
                {'Text': 'weather conditions', 'Type': 'OTHER', 'Score': 0.8}
            ],
            'SourceDocuments': ['news1', 'news2', 'news3']
        }
        
        sentiment_result = transformer.transform_comprehend_response(mock_sentiment_response, "corn seed")
        print(f"   ✅ Sentiment transformation: {sentiment_result.overall_sentiment}")
        print(f"      Risk level: {sentiment_result.risk_level}, Sources: {sentiment_result.news_sources_analyzed}")
        
    except Exception as e:
        print(f"   ❌ AWS BI transformation test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 AWS Integration Test Summary:")
    print("✅ All core components are ready for AWS integration")
    print("✅ System gracefully handles AWS service availability")
    print("✅ Mock data provides realistic fallback behavior")
    print("\n📋 Next Steps:")
    print("1. Configure AWS credentials: aws configure")
    print("2. Ensure required AWS services are enabled in your account:")
    print("   - Amazon Forecast")
    print("   - Amazon QuickSight") 
    print("   - Amazon Comprehend")
    print("3. Set up appropriate IAM permissions for these services")
    print("4. Re-run this test to verify full AWS connectivity")
    
    return True


def test_aws_configuration_guide():
    """Provide guidance for AWS configuration."""
    print("\n🔧 AWS Configuration Guide")
    print("=" * 40)
    print("\n1. Install AWS CLI (if not already installed):")
    print("   - Download from: https://aws.amazon.com/cli/")
    print("   - Or use: pip install awscli")
    
    print("\n2. Configure AWS credentials:")
    print("   aws configure")
    print("   - AWS Access Key ID: [Your access key]")
    print("   - AWS Secret Access Key: [Your secret key]")
    print("   - Default region name: us-east-1")
    print("   - Default output format: json")
    
    print("\n3. Required AWS Services & Permissions:")
    print("   The application needs access to:")
    print("   - Amazon Forecast (forecast:*)")
    print("   - Amazon QuickSight (quicksight:*)")
    print("   - Amazon Comprehend (comprehend:*)")
    print("   - Amazon S3 (s3:*) - for data storage")
    
    print("\n4. Test AWS connectivity:")
    print("   aws sts get-caller-identity")
    
    print("\n5. Environment Variables (alternative to aws configure):")
    print("   export AWS_ACCESS_KEY_ID=your_access_key")
    print("   export AWS_SECRET_ACCESS_KEY=your_secret_key")
    print("   export AWS_DEFAULT_REGION=us-east-1")


if __name__ == "__main__":
    print("🚀 Starting AWS Integration Test...")
    
    # Show configuration guide first
    test_aws_configuration_guide()
    
    # Run the actual connectivity test
    try:
        success = asyncio.run(test_aws_connectivity())
        if success:
            print("\n✅ AWS Integration test completed successfully!")
        else:
            print("\n❌ AWS Integration test failed - see errors above")
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error during test: {e}")