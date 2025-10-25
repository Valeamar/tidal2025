import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from botocore.exceptions import ClientError, BotoCoreError
import pandas as pd

logger = logging.getLogger(__name__)

class AmazonForecastService:
    """
    Service for integrating with Amazon Forecast to predict agricultural product prices.
    Handles dataset preparation, training, and price prediction queries with confidence intervals.
    """
    
    def __init__(self, region_name: str = 'us-east-1'):
        """Initialize the Amazon Forecast service client."""
        try:
            self.forecast_client = boto3.client('forecast', region_name=region_name)
            self.forecast_query_client = boto3.client('forecastquery', region_name=region_name)
            self.s3_client = boto3.client('s3', region_name=region_name)
            self.region = region_name
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise
    
    def prepare_forecast_dataset(self, product_name: str, price_data: List[Dict]) -> Dict:
        """
        Prepare dataset for Amazon Forecast training.
        
        Args:
            product_name: Name of the agricultural product
            price_data: List of price data points with timestamp and price
            
        Returns:
            Dict containing dataset preparation results
        """
        try:
            # Convert price data to DataFrame for processing
            df = pd.DataFrame(price_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Ensure minimum data requirements (Amazon Forecast needs at least 100 data points)
            if len(df) < 100:
                logger.warning(f"Insufficient data for {product_name}: {len(df)} points (minimum 100 required)")
                return {
                    'success': False,
                    'error': 'Insufficient historical data for reliable forecasting',
                    'data_points': len(df)
                }
            
            # Format data for Amazon Forecast (timestamp, target_value, item_id)
            forecast_data = []
            for _, row in df.iterrows():
                forecast_data.append({
                    'timestamp': row['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    'target_value': float(row['price']),
                    'item_id': product_name.lower().replace(' ', '_')
                })
            
            return {
                'success': True,
                'dataset': forecast_data,
                'data_points': len(forecast_data),
                'date_range': {
                    'start': df['timestamp'].min().isoformat(),
                    'end': df['timestamp'].max().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Dataset preparation failed for {product_name}: {str(e)}")
            return {
                'success': False,
                'error': f'Dataset preparation error: {str(e)}'
            }
    
    def create_forecast_dataset_group(self, dataset_group_name: str, domain: str = 'CUSTOM') -> Dict:
        """
        Create a dataset group in Amazon Forecast.
        
        Args:
            dataset_group_name: Name for the dataset group
            domain: Forecast domain (CUSTOM for agricultural products)
            
        Returns:
            Dict containing creation results
        """
        try:
            response = self.forecast_client.create_dataset_group(
                DatasetGroupName=dataset_group_name,
                Domain=domain,
                Tags=[
                    {
                        'Key': 'Application',
                        'Value': 'FarmerBudgetOptimizer'
                    },
                    {
                        'Key': 'Purpose',
                        'Value': 'AgriculturalPricePrediction'
                    }
                ]
            )
            
            return {
                'success': True,
                'dataset_group_arn': response['DatasetGroupArn']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceAlreadyExistsException':
                # Dataset group already exists, get its ARN
                try:
                    response = self.forecast_client.describe_dataset_group(
                        DatasetGroupArn=f"arn:aws:forecast:{self.region}:*:dataset-group/{dataset_group_name}"
                    )
                    return {
                        'success': True,
                        'dataset_group_arn': response['DatasetGroupArn'],
                        'already_exists': True
                    }
                except Exception:
                    pass
            
            logger.error(f"Failed to create dataset group {dataset_group_name}: {str(e)}")
            return {
                'success': False,
                'error': f'Dataset group creation failed: {str(e)}'
            }
    
    def query_price_forecast(self, predictor_arn: str, item_id: str, 
                           forecast_horizon: int = 30) -> Dict:
        """
        Query Amazon Forecast for price predictions with confidence intervals.
        
        Args:
            predictor_arn: ARN of the trained predictor
            item_id: Product identifier
            forecast_horizon: Number of days to forecast
            
        Returns:
            Dict containing forecast results with confidence intervals
        """
        try:
            response = self.forecast_query_client.query_forecast(
                ForecastArn=predictor_arn,
                Filters={
                    'item_id': item_id
                }
            )
            
            forecast_data = response.get('Forecast', {})
            predictions = forecast_data.get('Predictions', {})
            
            # Extract confidence intervals (p10, p50, p90)
            forecast_results = {
                'item_id': item_id,
                'forecast_horizon_days': forecast_horizon,
                'predictions': [],
                'confidence_intervals': {
                    'p10': [],  # 10th percentile (pessimistic)
                    'p50': [],  # 50th percentile (median)
                    'p90': []   # 90th percentile (optimistic)
                }
            }
            
            # Process each quantile
            for quantile, values in predictions.items():
                quantile_key = f"p{int(float(quantile) * 100)}"
                if quantile_key in forecast_results['confidence_intervals']:
                    for value in values:
                        forecast_results['confidence_intervals'][quantile_key].append({
                            'timestamp': value.get('Timestamp'),
                            'value': float(value.get('Value', 0))
                        })
            
            # Calculate seasonality and trend indicators
            seasonality_analysis = self._analyze_seasonality(forecast_results['confidence_intervals']['p50'])
            trend_analysis = self._detect_trend(forecast_results['confidence_intervals']['p50'])
            
            forecast_results.update({
                'seasonality': seasonality_analysis,
                'trend': trend_analysis,
                'generated_at': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'forecast': forecast_results
            }
            
        except ClientError as e:
            logger.error(f"Forecast query failed for {item_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Forecast query error: {str(e)}',
                'fallback_available': True
            }
        except Exception as e:
            logger.error(f"Unexpected error in forecast query: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected forecast error: {str(e)}',
                'fallback_available': True
            }
    
    def _analyze_seasonality(self, price_data: List[Dict]) -> Dict:
        """
        Analyze seasonality patterns in price data.
        
        Args:
            price_data: List of price data points with timestamps
            
        Returns:
            Dict containing seasonality analysis
        """
        try:
            if len(price_data) < 12:  # Need at least a year of data
                return {
                    'seasonal_pattern_detected': False,
                    'reason': 'Insufficient data for seasonality analysis'
                }
            
            df = pd.DataFrame(price_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['month'] = df['timestamp'].dt.month
            
            # Calculate monthly averages
            monthly_avg = df.groupby('month')['value'].mean()
            overall_avg = df['value'].mean()
            
            # Detect seasonal variations (>20% deviation from average)
            seasonal_months = []
            for month, avg_price in monthly_avg.items():
                deviation = abs(avg_price - overall_avg) / overall_avg
                if deviation > 0.2:  # 20% threshold
                    seasonal_months.append({
                        'month': month,
                        'average_price': float(avg_price),
                        'deviation_percent': float(deviation * 100)
                    })
            
            return {
                'seasonal_pattern_detected': len(seasonal_months) > 0,
                'seasonal_months': seasonal_months,
                'peak_month': int(monthly_avg.idxmax()) if len(monthly_avg) > 0 else None,
                'low_month': int(monthly_avg.idxmin()) if len(monthly_avg) > 0 else None
            }
            
        except Exception as e:
            logger.error(f"Seasonality analysis failed: {str(e)}")
            return {
                'seasonal_pattern_detected': False,
                'error': str(e)
            }
    
    def _detect_trend(self, price_data: List[Dict]) -> Dict:
        """
        Detect price trends in the forecast data.
        
        Args:
            price_data: List of price data points
            
        Returns:
            Dict containing trend analysis
        """
        try:
            if len(price_data) < 5:
                return {
                    'trend_detected': False,
                    'reason': 'Insufficient data for trend analysis'
                }
            
            values = [point['value'] for point in price_data]
            
            # Simple linear trend calculation
            x = list(range(len(values)))
            n = len(values)
            
            # Calculate slope using least squares
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            
            # Determine trend direction and strength
            trend_strength = abs(slope) / (sum_y / n) if sum_y != 0 else 0
            
            if trend_strength < 0.01:  # Less than 1% change
                trend_direction = 'stable'
            elif slope > 0:
                trend_direction = 'increasing'
            else:
                trend_direction = 'decreasing'
            
            return {
                'trend_detected': trend_strength >= 0.01,
                'direction': trend_direction,
                'strength': float(trend_strength),
                'slope': float(slope)
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {str(e)}")
            return {
                'trend_detected': False,
                'error': str(e)
            }
    
    def handle_forecast_errors(self, error: Exception) -> Dict:
        """
        Handle Amazon Forecast service errors and provide fallback options.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Dict containing error handling results and fallback options
        """
        error_response = {
            'service_available': False,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'fallback_options': []
        }
        
        if isinstance(error, ClientError):
            error_code = error.response['Error']['Code']
            
            if error_code in ['ThrottlingException', 'ServiceUnavailableException']:
                error_response['fallback_options'].extend([
                    'retry_with_backoff',
                    'use_cached_forecast',
                    'simple_trend_analysis'
                ])
                error_response['retryable'] = True
                
            elif error_code in ['AccessDeniedException', 'UnauthorizedOperation']:
                error_response['fallback_options'].extend([
                    'use_historical_averages',
                    'simple_trend_analysis'
                ])
                error_response['retryable'] = False
                
            elif error_code == 'ResourceNotFoundException':
                error_response['fallback_options'].extend([
                    'create_new_predictor',
                    'use_historical_averages'
                ])
                error_response['retryable'] = True
        
        else:
            # Network or other errors
            error_response['fallback_options'].extend([
                'retry_with_backoff',
                'use_cached_forecast',
                'simple_trend_analysis'
            ])
            error_response['retryable'] = True
        
        return error_response