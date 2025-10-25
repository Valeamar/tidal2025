import boto3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, BotoCoreError
import uuid

logger = logging.getLogger(__name__)

class AWSQuickSightService:
    """
    Service for integrating with AWS QuickSight to provide ML insights and embedded dashboards.
    Handles data source setup, dashboard creation, and anomaly detection for agricultural data.
    """
    
    def __init__(self, region_name: str = 'us-east-1', aws_account_id: str = None):
        """Initialize the AWS QuickSight service client."""
        try:
            self.quicksight_client = boto3.client('quicksight', region_name=region_name)
            self.s3_client = boto3.client('s3', region_name=region_name)
            self.region = region_name
            self.aws_account_id = aws_account_id or boto3.client('sts').get_caller_identity()['Account']
        except Exception as e:
            logger.error(f"Failed to initialize AWS QuickSight clients: {str(e)}")
            raise
    
    def setup_data_source(self, data_source_name: str, s3_bucket: str, 
                         s3_key: str) -> Dict:
        """
        Set up QuickSight data source for agricultural price data.
        
        Args:
            data_source_name: Name for the data source
            s3_bucket: S3 bucket containing the data
            s3_key: S3 key path to the data file
            
        Returns:
            Dict containing data source setup results
        """
        try:
            data_source_id = f"agricultural-data-{uuid.uuid4().hex[:8]}"
            
            # Create S3 data source
            response = self.quicksight_client.create_data_source(
                AwsAccountId=self.aws_account_id,
                DataSourceId=data_source_id,
                Name=data_source_name,
                Type='S3',
                DataSourceParameters={
                    'S3Parameters': {
                        'ManifestFileLocation': {
                            'Bucket': s3_bucket,
                            'Key': s3_key
                        }
                    }
                },
                Permissions=[
                    {
                        'Principal': f"arn:aws:quicksight:{self.region}:{self.aws_account_id}:user/default/farmer-budget-optimizer",
                        'Actions': [
                            'quicksight:DescribeDataSource',
                            'quicksight:DescribeDataSourcePermissions',
                            'quicksight:PassDataSource',
                            'quicksight:UpdateDataSource',
                            'quicksight:DeleteDataSource'
                        ]
                    }
                ],
                Tags=[
                    {
                        'Key': 'Application',
                        'Value': 'FarmerBudgetOptimizer'
                    },
                    {
                        'Key': 'DataType',
                        'Value': 'AgriculturalPrices'
                    }
                ]
            )
            
            return {
                'success': True,
                'data_source_id': data_source_id,
                'data_source_arn': response['Arn'],
                'creation_status': response['CreationStatus']
            }
            
        except ClientError as e:
            logger.error(f"Failed to create QuickSight data source: {str(e)}")
            return {
                'success': False,
                'error': f'Data source creation failed: {str(e)}'
            }
    
    def create_ml_insights_dashboard(self, dashboard_name: str, data_source_id: str) -> Dict:
        """
        Create QuickSight dashboard with ML insights for agricultural data analysis.
        
        Args:
            dashboard_name: Name for the dashboard
            data_source_id: ID of the data source to use
            
        Returns:
            Dict containing dashboard creation results
        """
        try:
            dashboard_id = f"agricultural-insights-{uuid.uuid4().hex[:8]}"
            
            # Define dashboard definition with ML insights
            dashboard_definition = {
                'DataSetIdentifierDeclarations': [
                    {
                        'DataSetIdentifier': 'agricultural_data',
                        'DataSetArn': f"arn:aws:quicksight:{self.region}:{self.aws_account_id}:dataset/{data_source_id}"
                    }
                ],
                'Sheets': [
                    {
                        'SheetId': 'price_trends_sheet',
                        'Name': 'Price Trends & Anomalies',
                        'Visuals': [
                            {
                                'LineChartVisual': {
                                    'VisualId': 'price_trend_chart',
                                    'Title': {
                                        'Visibility': 'VISIBLE',
                                        'FormatText': {
                                            'PlainText': 'Agricultural Product Price Trends'
                                        }
                                    },
                                    'FieldWells': {
                                        'LineChartAggregatedFieldWells': {
                                            'Category': [
                                                {
                                                    'DateDimensionField': {
                                                        'FieldId': 'date_field',
                                                        'Column': {
                                                            'DataSetIdentifier': 'agricultural_data',
                                                            'ColumnName': 'timestamp'
                                                        }
                                                    }
                                                }
                                            ],
                                            'Values': [
                                                {
                                                    'NumericalMeasureField': {
                                                        'FieldId': 'price_field',
                                                        'Column': {
                                                            'DataSetIdentifier': 'agricultural_data',
                                                            'ColumnName': 'price'
                                                        }
                                                    }
                                                }
                                            ],
                                            'Colors': [
                                                {
                                                    'CategoricalDimensionField': {
                                                        'FieldId': 'product_field',
                                                        'Column': {
                                                            'DataSetIdentifier': 'agricultural_data',
                                                            'ColumnName': 'product_name'
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            },
                            {
                                'InsightVisual': {
                                    'VisualId': 'anomaly_detection',
                                    'Title': {
                                        'Visibility': 'VISIBLE',
                                        'FormatText': {
                                            'PlainText': 'Price Anomaly Detection'
                                        }
                                    },
                                    'DataSetIdentifier': 'agricultural_data',
                                    'InsightConfiguration': {
                                        'Computations': [
                                            {
                                                'TopBottomRanked': {
                                                    'ComputationId': 'anomaly_computation',
                                                    'Name': 'Price Anomalies',
                                                    'Category': {
                                                        'DateDimensionField': {
                                                            'FieldId': 'anomaly_date',
                                                            'Column': {
                                                                'DataSetIdentifier': 'agricultural_data',
                                                                'ColumnName': 'timestamp'
                                                            }
                                                        }
                                                    },
                                                    'Value': {
                                                        'NumericalMeasureField': {
                                                            'FieldId': 'anomaly_price',
                                                            'Column': {
                                                                'DataSetIdentifier': 'agricultural_data',
                                                                'ColumnName': 'price'
                                                            }
                                                        }
                                                    },
                                                    'ResultSize': 10,
                                                    'Type': 'TOP'
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    },
                    {
                        'SheetId': 'correlation_analysis_sheet',
                        'Name': 'Market Correlations',
                        'Visuals': [
                            {
                                'ScatterPlotVisual': {
                                    'VisualId': 'correlation_scatter',
                                    'Title': {
                                        'Visibility': 'VISIBLE',
                                        'FormatText': {
                                            'PlainText': 'Price Correlation Analysis'
                                        }
                                    },
                                    'FieldWells': {
                                        'ScatterPlotCategoricallyAggregatedFieldWells': {
                                            'XAxis': [
                                                {
                                                    'NumericalMeasureField': {
                                                        'FieldId': 'external_factor_x',
                                                        'Column': {
                                                            'DataSetIdentifier': 'agricultural_data',
                                                            'ColumnName': 'external_factor_value'
                                                        }
                                                    }
                                                }
                                            ],
                                            'YAxis': [
                                                {
                                                    'NumericalMeasureField': {
                                                        'FieldId': 'price_y',
                                                        'Column': {
                                                            'DataSetIdentifier': 'agricultural_data',
                                                            'ColumnName': 'price'
                                                        }
                                                    }
                                                }
                                            ],
                                            'Category': [
                                                {
                                                    'CategoricalDimensionField': {
                                                        'FieldId': 'product_category',
                                                        'Column': {
                                                            'DataSetIdentifier': 'agricultural_data',
                                                            'ColumnName': 'product_name'
                                                        }
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
            
            # Create the dashboard
            response = self.quicksight_client.create_dashboard(
                AwsAccountId=self.aws_account_id,
                DashboardId=dashboard_id,
                Name=dashboard_name,
                Definition=dashboard_definition,
                Permissions=[
                    {
                        'Principal': f"arn:aws:quicksight:{self.region}:{self.aws_account_id}:user/default/farmer-budget-optimizer",
                        'Actions': [
                            'quicksight:DescribeDashboard',
                            'quicksight:ListDashboardVersions',
                            'quicksight:UpdateDashboardPermissions',
                            'quicksight:QueryDashboard',
                            'quicksight:UpdateDashboard',
                            'quicksight:DeleteDashboard',
                            'quicksight:DescribeDashboardPermissions',
                            'quicksight:ExportToCsv'
                        ]
                    }
                ],
                Tags=[
                    {
                        'Key': 'Application',
                        'Value': 'FarmerBudgetOptimizer'
                    },
                    {
                        'Key': 'DashboardType',
                        'Value': 'MLInsights'
                    }
                ]
            )
            
            return {
                'success': True,
                'dashboard_id': dashboard_id,
                'dashboard_arn': response['Arn'],
                'creation_status': response['CreationStatus']
            }
            
        except ClientError as e:
            logger.error(f"Failed to create QuickSight dashboard: {str(e)}")
            return {
                'success': False,
                'error': f'Dashboard creation failed: {str(e)}'
            }    def
 generate_embedded_dashboard_url(self, dashboard_id: str, user_arn: str) -> Dict:
        """
        Generate embedded dashboard URL for frontend display.
        
        Args:
            dashboard_id: ID of the dashboard to embed
            user_arn: ARN of the user requesting access
            
        Returns:
            Dict containing embedded URL and session details
        """
        try:
            # Generate embed URL for dashboard
            response = self.quicksight_client.generate_embed_url_for_anonymous_user(
                AwsAccountId=self.aws_account_id,
                Namespace='default',
                SessionLifetimeInMinutes=600,  # 10 hours
                AuthorizedResourceArns=[
                    f"arn:aws:quicksight:{self.region}:{self.aws_account_id}:dashboard/{dashboard_id}"
                ],
                ExperienceConfiguration={
                    'Dashboard': {
                        'InitialDashboardId': dashboard_id
                    }
                },
                AllowedDomains=[
                    'localhost:3000',
                    '127.0.0.1:3000'
                ]
            )
            
            return {
                'success': True,
                'embed_url': response['EmbedUrl'],
                'request_id': response['RequestId'],
                'session_lifetime_minutes': 600
            }
            
        except ClientError as e:
            logger.error(f"Failed to generate embed URL for dashboard {dashboard_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Embed URL generation failed: {str(e)}'
            }
    
    def detect_price_anomalies(self, price_data: List[Dict], 
                              sensitivity: float = 2.0) -> Dict:
        """
        Implement ML-based anomaly detection for price patterns.
        
        Args:
            price_data: List of price data points with timestamps and values
            sensitivity: Anomaly detection sensitivity (standard deviations)
            
        Returns:
            Dict containing detected anomalies and analysis
        """
        try:
            if len(price_data) < 10:
                return {
                    'anomalies_detected': False,
                    'reason': 'Insufficient data for anomaly detection'
                }
            
            # Extract price values and calculate statistics
            prices = [float(point['price']) for point in price_data]
            timestamps = [point['timestamp'] for point in price_data]
            
            # Calculate rolling statistics for anomaly detection
            window_size = min(30, len(prices) // 3)  # Use 30-day window or 1/3 of data
            anomalies = []
            
            for i in range(window_size, len(prices)):
                # Calculate rolling mean and standard deviation
                window_data = prices[i-window_size:i]
                mean_price = sum(window_data) / len(window_data)
                variance = sum((x - mean_price) ** 2 for x in window_data) / len(window_data)
                std_dev = variance ** 0.5
                
                # Check if current price is an anomaly
                current_price = prices[i]
                z_score = abs(current_price - mean_price) / std_dev if std_dev > 0 else 0
                
                if z_score > sensitivity:
                    anomaly_type = 'spike' if current_price > mean_price else 'drop'
                    anomalies.append({
                        'timestamp': timestamps[i],
                        'price': current_price,
                        'expected_price': mean_price,
                        'deviation': current_price - mean_price,
                        'z_score': z_score,
                        'type': anomaly_type,
                        'severity': 'high' if z_score > 3.0 else 'medium'
                    })
            
            # Analyze anomaly patterns
            pattern_analysis = self._analyze_anomaly_patterns(anomalies)
            
            return {
                'anomalies_detected': len(anomalies) > 0,
                'anomaly_count': len(anomalies),
                'anomalies': anomalies,
                'pattern_analysis': pattern_analysis,
                'sensitivity_used': sensitivity
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {str(e)}")
            return {
                'anomalies_detected': False,
                'error': str(e)
            }
    
    def analyze_market_correlations(self, price_data: List[Dict], 
                                  external_factors: List[Dict]) -> Dict:
        """
        Analyze correlations between agricultural prices and external factors.
        
        Args:
            price_data: List of price data points
            external_factors: List of external factor data (weather, fuel prices, etc.)
            
        Returns:
            Dict containing correlation analysis results
        """
        try:
            if len(price_data) < 10 or len(external_factors) < 10:
                return {
                    'correlations_found': False,
                    'reason': 'Insufficient data for correlation analysis'
                }
            
            correlations = []
            
            # Analyze correlation with each external factor
            for factor in external_factors:
                factor_name = factor.get('name', 'unknown')
                factor_values = factor.get('values', [])
                
                if len(factor_values) < len(price_data):
                    continue
                
                # Calculate Pearson correlation coefficient
                prices = [float(point['price']) for point in price_data]
                factors = [float(val) for val in factor_values[:len(prices)]]
                
                correlation = self._calculate_correlation(prices, factors)
                
                if abs(correlation) > 0.3:  # Significant correlation threshold
                    correlations.append({
                        'factor_name': factor_name,
                        'correlation_coefficient': correlation,
                        'strength': self._classify_correlation_strength(correlation),
                        'direction': 'positive' if correlation > 0 else 'negative'
                    })
            
            # Sort by correlation strength
            correlations.sort(key=lambda x: abs(x['correlation_coefficient']), reverse=True)
            
            return {
                'correlations_found': len(correlations) > 0,
                'correlation_count': len(correlations),
                'correlations': correlations,
                'strongest_correlation': correlations[0] if correlations else None
            }
            
        except Exception as e:
            logger.error(f"Correlation analysis failed: {str(e)}")
            return {
                'correlations_found': False,
                'error': str(e)
            }
    
    def _analyze_anomaly_patterns(self, anomalies: List[Dict]) -> Dict:
        """
        Analyze patterns in detected anomalies.
        
        Args:
            anomalies: List of detected anomalies
            
        Returns:
            Dict containing pattern analysis
        """
        if not anomalies:
            return {'patterns_detected': False}
        
        # Count anomaly types
        spikes = sum(1 for a in anomalies if a['type'] == 'spike')
        drops = sum(1 for a in anomalies if a['type'] == 'drop')
        
        # Analyze temporal clustering
        timestamps = [datetime.fromisoformat(a['timestamp'].replace('Z', '+00:00')) for a in anomalies]
        timestamps.sort()
        
        clusters = []
        current_cluster = [timestamps[0]]
        
        for i in range(1, len(timestamps)):
            time_diff = (timestamps[i] - timestamps[i-1]).days
            if time_diff <= 7:  # Within a week
                current_cluster.append(timestamps[i])
            else:
                if len(current_cluster) > 1:
                    clusters.append(current_cluster)
                current_cluster = [timestamps[i]]
        
        if len(current_cluster) > 1:
            clusters.append(current_cluster)
        
        return {
            'patterns_detected': True,
            'spike_count': spikes,
            'drop_count': drops,
            'dominant_type': 'spike' if spikes > drops else 'drop',
            'temporal_clusters': len(clusters),
            'clustered_anomalies': sum(len(cluster) for cluster in clusters)
        }
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """
        Calculate Pearson correlation coefficient between two datasets.
        
        Args:
            x: First dataset
            y: Second dataset
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        n = len(x)
        if n != len(y) or n == 0:
            return 0.0
        
        # Calculate means
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        # Calculate correlation coefficient
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        sum_sq_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        sum_sq_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        denominator = (sum_sq_x * sum_sq_y) ** 0.5
        
        return numerator / denominator if denominator != 0 else 0.0
    
    def _classify_correlation_strength(self, correlation: float) -> str:
        """
        Classify correlation strength based on coefficient value.
        
        Args:
            correlation: Correlation coefficient
            
        Returns:
            String classification of correlation strength
        """
        abs_corr = abs(correlation)
        
        if abs_corr >= 0.7:
            return 'strong'
        elif abs_corr >= 0.5:
            return 'moderate'
        elif abs_corr >= 0.3:
            return 'weak'
        else:
            return 'negligible'