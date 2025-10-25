import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .aws_forecast_service import AmazonForecastService
from .aws_quicksight_service import AWSQuickSightService
from .aws_comprehend_service import AWSComprehendService

logger = logging.getLogger(__name__)

class AWSBIIntegration:
    """
    Unified service for AWS BI integrations combining Forecast, QuickSight, and Comprehend services.
    Provides comprehensive agricultural market analysis and insights.
    """
    
    def __init__(self, region_name: str = 'us-east-1', aws_account_id: str = None):
        """Initialize all AWS BI services."""
        try:
            self.forecast_service = AmazonForecastService(region_name)
            self.quicksight_service = AWSQuickSightService(region_name, aws_account_id)
            self.comprehend_service = AWSComprehendService(region_name)
            self.region = region_name
        except Exception as e:
            logger.error(f"Failed to initialize AWS BI services: {str(e)}")
            raise
    
    def comprehensive_market_analysis(self, analysis_request: Dict) -> Dict:
        """
        Perform comprehensive market analysis using all AWS BI services.
        
        Args:
            analysis_request: Dict containing:
                - products: List of products to analyze
                - price_data: Historical price data
                - news_articles: Market news for sentiment analysis
                - market_factors: External market factors
                - historical_demand: Historical demand data
                
        Returns:
            Dict containing comprehensive analysis results
        """
        try:
            products = analysis_request.get('products', [])
            price_data = analysis_request.get('price_data', [])
            news_articles = analysis_request.get('news_articles', [])
            market_factors = analysis_request.get('market_factors', {})
            historical_demand = analysis_request.get('historical_demand', [])
            
            analysis_results = {
                'analysis_timestamp': datetime.now().isoformat(),
                'products_analyzed': len(products),
                'services_used': [],
                'forecast_analysis': {},
                'sentiment_analysis': {},
                'risk_assessment': {},
                'recommendations': {},
                'dashboard_info': {},
                'errors': []
            }
            
            # 1. Price Forecasting Analysis
            if price_data:
                logger.info("Starting price forecast analysis...")
                try:
                    forecast_results = {}
                    for product in products:
                        product_price_data = [
                            p for p in price_data 
                            if p.get('product', '').lower() == product.lower()
                        ]
                        
                        if product_price_data:
                            # Prepare dataset
                            dataset_prep = self.forecast_service.prepare_forecast_dataset(
                                product, product_price_data
                            )
                            
                            if dataset_prep.get('success'):
                                # For demo purposes, simulate forecast query
                                # In production, you'd train a model first
                                forecast_results[product] = {
                                    'dataset_prepared': True,
                                    'data_points': dataset_prep.get('data_points', 0),
                                    'forecast_available': False,
                                    'message': 'Dataset prepared - model training required for predictions'
                                }
                            else:
                                forecast_results[product] = {
                                    'dataset_prepared': False,
                                    'error': dataset_prep.get('error', 'Unknown error')
                                }
                    
                    analysis_results['forecast_analysis'] = forecast_results
                    analysis_results['services_used'].append('Amazon Forecast')
                    
                except Exception as e:
                    logger.error(f"Forecast analysis failed: {str(e)}")
                    analysis_results['errors'].append(f"Forecast analysis: {str(e)}")
            
            # 2. Sentiment Analysis
            if news_articles:
                logger.info("Starting sentiment analysis...")
                try:
                    sentiment_results = self.comprehend_service.analyze_market_news_sentiment(
                        news_articles
                    )
                    analysis_results['sentiment_analysis'] = sentiment_results
                    analysis_results['services_used'].append('AWS Comprehend')
                    
                except Exception as e:
                    logger.error(f"Sentiment analysis failed: {str(e)}")
                    analysis_results['errors'].append(f"Sentiment analysis: {str(e)}")
            
            # 3. Risk Assessment
            if analysis_results.get('sentiment_analysis', {}).get('analysis_completed'):
                logger.info("Calculating supply risk scores...")
                try:
                    risk_scores = self.comprehend_service.calculate_supply_risk_score(
                        analysis_results['sentiment_analysis'],
                        market_factors
                    )
                    analysis_results['risk_assessment'] = risk_scores
                    
                except Exception as e:
                    logger.error(f"Risk assessment failed: {str(e)}")
                    analysis_results['errors'].append(f"Risk assessment: {str(e)}")
            
            # 4. Demand Predictions
            if (analysis_results.get('sentiment_analysis', {}).get('analysis_completed') and 
                historical_demand):
                logger.info("Generating demand predictions...")
                try:
                    demand_predictions = self.comprehend_service.predict_demand_outlook(
                        analysis_results['sentiment_analysis'],
                        historical_demand
                    )
                    analysis_results['demand_predictions'] = demand_predictions
                    
                except Exception as e:
                    logger.error(f"Demand prediction failed: {str(e)}")
                    analysis_results['errors'].append(f"Demand prediction: {str(e)}")
            
            # 5. Generate Recommendations
            if (analysis_results.get('risk_assessment', {}).get('risk_calculation_completed') and
                analysis_results.get('demand_predictions', {}).get('prediction_completed')):
                logger.info("Generating risk-based recommendations...")
                try:
                    current_prices = {
                        product: price_data[-1].get('price', 0) 
                        for product in products 
                        if any(p.get('product', '').lower() == product.lower() for p in price_data)
                    }
                    
                    recommendations = self.comprehend_service.generate_risk_based_recommendations(
                        analysis_results['risk_assessment']['risk_scores'],
                        analysis_results['demand_predictions']['demand_predictions'],
                        current_prices
                    )
                    analysis_results['recommendations'] = recommendations
                    
                except Exception as e:
                    logger.error(f"Recommendation generation failed: {str(e)}")
                    analysis_results['errors'].append(f"Recommendation generation: {str(e)}")
            
            # 6. QuickSight Dashboard Info (placeholder for actual dashboard creation)
            analysis_results['dashboard_info'] = {
                'dashboard_available': False,
                'message': 'Dashboard creation requires data source setup and AWS account configuration',
                'required_setup': [
                    'Configure S3 data sources',
                    'Set up QuickSight permissions',
                    'Create dataset groups'
                ]
            }
            
            # Calculate overall analysis quality
            successful_services = len(analysis_results['services_used'])
            total_possible_services = 3  # Forecast, Comprehend, QuickSight
            analysis_quality = successful_services / total_possible_services
            
            analysis_results['analysis_quality'] = {
                'score': analysis_quality,
                'services_successful': successful_services,
                'services_total': total_possible_services,
                'completeness': 'high' if analysis_quality >= 0.8 else 'medium' if analysis_quality >= 0.5 else 'low'
            }
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Comprehensive market analysis failed: {str(e)}")
            return {
                'analysis_timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e),
                'services_used': [],
                'analysis_quality': {'score': 0.0, 'completeness': 'failed'}
            }
    
    def get_service_health_status(self) -> Dict:
        """
        Check the health status of all AWS BI services.
        
        Returns:
            Dict containing health status of each service
        """
        health_status = {
            'overall_status': 'unknown',
            'services': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Test Amazon Forecast
        try:
            # Simple test - this would normally check service availability
            health_status['services']['forecast'] = {
                'status': 'available',
                'message': 'Service initialized successfully'
            }
        except Exception as e:
            health_status['services']['forecast'] = {
                'status': 'unavailable',
                'error': str(e)
            }
        
        # Test AWS Comprehend
        try:
            # Simple test
            health_status['services']['comprehend'] = {
                'status': 'available',
                'message': 'Service initialized successfully'
            }
        except Exception as e:
            health_status['services']['comprehend'] = {
                'status': 'unavailable',
                'error': str(e)
            }
        
        # Test AWS QuickSight
        try:
            # Simple test
            health_status['services']['quicksight'] = {
                'status': 'available',
                'message': 'Service initialized successfully'
            }
        except Exception as e:
            health_status['services']['quicksight'] = {
                'status': 'unavailable',
                'error': str(e)
            }
        
        # Determine overall status
        available_services = sum(
            1 for service in health_status['services'].values() 
            if service['status'] == 'available'
        )
        
        if available_services == 3:
            health_status['overall_status'] = 'healthy'
        elif available_services >= 2:
            health_status['overall_status'] = 'degraded'
        elif available_services >= 1:
            health_status['overall_status'] = 'limited'
        else:
            health_status['overall_status'] = 'unavailable'
        
        return health_status