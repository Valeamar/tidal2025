"""
AWS Client Configuration and Management

This module provides centralized AWS client configuration and authentication
for the Farmer Budget Optimizer application following AWS best practices.
"""

import os
import boto3
from botocore.exceptions import (
    ClientError, NoCredentialsError, PartialCredentialsError,
    BotoCoreError, EndpointConnectionError, ReadTimeoutError
)
from botocore.config import Config
from typing import Optional, Dict, Any
import logging
from functools import lru_cache
import time

logger = logging.getLogger(__name__)


class AWSClientError(Exception):
    """Custom exception for AWS client errors"""
    pass


class AWSClientManager:
    """
    Manages AWS service clients with proper authentication and error handling.
    
    Provides centralized configuration for Forecast, QuickSight, and Comprehend services
    following AWS best practices for client configuration, retry logic, and error handling.
    """
    
    def __init__(self, region_name: Optional[str] = None):
        """
        Initialize AWS client manager with best practice configurations.
        
        Args:
            region_name: AWS region name. If None, uses environment variable or default.
        """
        self.region_name = region_name or os.getenv('AWS_REGION', 'us-east-1')
        self._session = None
        self._clients = {}
        
        # AWS best practice: Configure retry and timeout settings
        self._client_config = Config(
            region_name=self.region_name,
            retries={
                'max_attempts': 3,
                'mode': 'adaptive'  # AWS recommended retry mode
            },
            max_pool_connections=50,
            read_timeout=60,
            connect_timeout=10
        )
        
        # Validate credentials on initialization
        self._validate_credentials()
    
    def _validate_credentials(self) -> None:
        """
        Validate AWS credentials are properly configured.
        
        Raises:
            AWSClientError: If credentials are missing or invalid
        """
        try:
            # Create a simple STS client to test credentials
            sts_client = boto3.client('sts', region_name=self.region_name)
            sts_client.get_caller_identity()
            logger.info(f"AWS credentials validated for region: {self.region_name}")
        except NoCredentialsError:
            raise AWSClientError(
                "AWS credentials not found. Please configure AWS_ACCESS_KEY_ID and "
                "AWS_SECRET_ACCESS_KEY environment variables or use IAM roles."
            )
        except PartialCredentialsError:
            raise AWSClientError(
                "Incomplete AWS credentials. Please ensure both AWS_ACCESS_KEY_ID and "
                "AWS_SECRET_ACCESS_KEY are configured."
            )
        except ClientError as e:
            raise AWSClientError(f"AWS credential validation failed: {e}")
    
    @property
    def session(self) -> boto3.Session:
        """
        Get or create boto3 session.
        
        Returns:
            boto3.Session: Configured AWS session
        """
        if self._session is None:
            self._session = boto3.Session(region_name=self.region_name)
        return self._session
    
    def _get_client(self, service_name: str, **kwargs) -> boto3.client:
        """
        Get or create AWS service client with caching and best practice configuration.
        
        Args:
            service_name: AWS service name (e.g., 'forecast', 'quicksight')
            **kwargs: Additional client configuration
            
        Returns:
            boto3.client: Configured AWS service client
            
        Raises:
            AWSClientError: If client creation fails
        """
        client_key = f"{service_name}_{hash(frozenset(kwargs.items()))}"
        
        if client_key not in self._clients:
            try:
                # Merge custom config with default best practice config
                merged_config = self._client_config.merge(kwargs.get('config', Config()))
                client_kwargs = {**kwargs, 'config': merged_config}
                
                self._clients[client_key] = self.session.client(
                    service_name,
                    **client_kwargs
                )
                logger.info(f"Created {service_name} client for region {self.region_name}")
            except (ClientError, BotoCoreError) as e:
                raise AWSClientError(f"Failed to create {service_name} client: {e}")
            except Exception as e:
                raise AWSClientError(f"Unexpected error creating {service_name} client: {e}")
        
        return self._clients[client_key]
    
    @property
    def forecast_client(self) -> boto3.client:
        """
        Get Amazon Forecast client.
        
        Returns:
            boto3.client: Forecast service client
        """
        return self._get_client('forecast')
    
    @property
    def forecastquery_client(self) -> boto3.client:
        """
        Get Amazon Forecast Query client for making predictions.
        
        Returns:
            boto3.client: Forecast Query service client
        """
        return self._get_client('forecastquery')
    
    @property
    def quicksight_client(self) -> boto3.client:
        """
        Get Amazon QuickSight client.
        
        Returns:
            boto3.client: QuickSight service client
        """
        return self._get_client('quicksight')
    
    @property
    def comprehend_client(self) -> boto3.client:
        """
        Get Amazon Comprehend client.
        
        Returns:
            boto3.client: Comprehend service client
        """
        return self._get_client('comprehend')
    
    @property
    def s3_client(self) -> boto3.client:
        """
        Get Amazon S3 client for data storage.
        
        Returns:
            boto3.client: S3 service client
        """
        return self._get_client('s3')
    
    def test_service_connectivity(self, service_name: str) -> Dict[str, Any]:
        """
        Test connectivity to a specific AWS service with proper error handling.
        
        Args:
            service_name: Name of the service to test ('forecast', 'quicksight', 'comprehend')
            
        Returns:
            Dict containing test results
        """
        start_time = time.time()
        
        try:
            if service_name == 'forecast':
                client = self.forecast_client
                # AWS best practice: Use minimal operations for health checks
                response = client.list_datasets(MaxResults=1)
                return {
                    'service': service_name,
                    'status': 'connected',
                    'region': self.region_name,
                    'test_operation': 'list_datasets',
                    'response_time_ms': round((time.time() - start_time) * 1000, 2),
                    'response_metadata': response.get('ResponseMetadata', {})
                }
            
            elif service_name == 'quicksight':
                client = self.quicksight_client
                # AWS best practice: Use account-level operations for QuickSight health checks
                aws_account_id = self.session.client('sts').get_caller_identity()['Account']
                response = client.describe_account_settings(AwsAccountId=aws_account_id)
                return {
                    'service': service_name,
                    'status': 'connected',
                    'region': self.region_name,
                    'test_operation': 'describe_account_settings',
                    'response_time_ms': round((time.time() - start_time) * 1000, 2),
                    'account_id': aws_account_id
                }
            
            elif service_name == 'comprehend':
                client = self.comprehend_client
                # AWS best practice: Use list operations for Comprehend health checks
                response = client.list_dominant_language_detection_jobs(MaxResults=1)
                return {
                    'service': service_name,
                    'status': 'connected',
                    'region': self.region_name,
                    'test_operation': 'list_dominant_language_detection_jobs',
                    'response_time_ms': round((time.time() - start_time) * 1000, 2),
                    'response_metadata': response.get('ResponseMetadata', {})
                }
            
            else:
                return {
                    'service': service_name,
                    'status': 'error',
                    'message': f'Unknown service: {service_name}',
                    'response_time_ms': round((time.time() - start_time) * 1000, 2)
                }
                
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            # AWS best practice: Categorize errors for better handling
            is_retryable = error_code in [
                'Throttling', 'ThrottlingException', 'ServiceUnavailable',
                'InternalServerError', 'RequestTimeout'
            ]
            
            return {
                'service': service_name,
                'status': 'error',
                'error_code': error_code,
                'error_message': error_message,
                'region': self.region_name,
                'is_retryable': is_retryable,
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }
        except (EndpointConnectionError, ReadTimeoutError) as e:
            return {
                'service': service_name,
                'status': 'connection_error',
                'error_message': f'Network connectivity issue: {str(e)}',
                'region': self.region_name,
                'is_retryable': True,
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }
        except Exception as e:
            return {
                'service': service_name,
                'status': 'error',
                'error_message': f'Unexpected error: {str(e)}',
                'region': self.region_name,
                'is_retryable': False,
                'response_time_ms': round((time.time() - start_time) * 1000, 2)
            }
    
    def test_all_services(self) -> Dict[str, Dict[str, Any]]:
        """
        Test connectivity to all AWS services used by the application.
        
        Returns:
            Dict mapping service names to test results
        """
        services = ['forecast', 'quicksight', 'comprehend']
        results = {}
        
        for service in services:
            results[service] = self.test_service_connectivity(service)
        
        return results


# Global client manager instance
@lru_cache(maxsize=1)
def get_aws_client_manager() -> AWSClientManager:
    """
    Get singleton AWS client manager instance.
    
    Returns:
        AWSClientManager: Configured client manager
    """
    return AWSClientManager()


# Convenience functions for getting individual clients
def get_forecast_client() -> boto3.client:
    """Get Amazon Forecast client."""
    return get_aws_client_manager().forecast_client


def get_forecastquery_client() -> boto3.client:
    """Get Amazon Forecast Query client."""
    return get_aws_client_manager().forecastquery_client


def get_quicksight_client() -> boto3.client:
    """Get Amazon QuickSight client."""
    return get_aws_client_manager().quicksight_client


def get_comprehend_client() -> boto3.client:
    """Get Amazon Comprehend client."""
    return get_aws_client_manager().comprehend_client


def get_s3_client() -> boto3.client:
    """Get Amazon S3 client."""
    return get_aws_client_manager().s3_client


# AWS Best Practice Utility Functions

def execute_aws_api_call(client, operation_name: str, **kwargs) -> Dict[str, Any]:
    """
    Execute AWS API call with proper error handling and logging.
    
    Args:
        client: AWS service client
        operation_name: Name of the API operation to call
        **kwargs: Parameters for the API call
        
    Returns:
        Dict containing the API response
        
    Raises:
        AWSClientError: If the API call fails after retries
    """
    start_time = time.time()
    
    try:
        # Get the operation method from the client
        operation = getattr(client, operation_name)
        
        # Execute the API call
        response = operation(**kwargs)
        
        # Log successful API call
        duration = round((time.time() - start_time) * 1000, 2)
        logger.info(
            f"AWS API call successful: {operation_name} "
            f"(duration: {duration}ms, region: {client.meta.region_name})"
        )
        
        return response
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        duration = round((time.time() - start_time) * 1000, 2)
        
        logger.error(
            f"AWS API call failed: {operation_name} "
            f"(error: {error_code}, duration: {duration}ms, region: {client.meta.region_name})"
        )
        
        # AWS best practice: Provide specific error information
        raise AWSClientError(
            f"AWS {operation_name} failed: {error_code} - {error_message}"
        )
        
    except Exception as e:
        duration = round((time.time() - start_time) * 1000, 2)
        logger.error(
            f"Unexpected error in AWS API call: {operation_name} "
            f"(duration: {duration}ms, region: {client.meta.region_name}): {str(e)}"
        )
        
        raise AWSClientError(f"Unexpected error in {operation_name}: {str(e)}")


def is_aws_error_retryable(error_code: str) -> bool:
    """
    Determine if an AWS error is retryable based on AWS best practices.
    
    Args:
        error_code: AWS error code
        
    Returns:
        Boolean indicating if the error is retryable
    """
    retryable_errors = {
        'Throttling', 'ThrottlingException', 'ServiceUnavailable',
        'InternalServerError', 'RequestTimeout', 'RequestTimeoutException',
        'PriorRequestNotComplete', 'ConnectionError', 'HTTPSConnectionPool'
    }
    
    return error_code in retryable_errors


def get_aws_service_endpoints(region_name: str) -> Dict[str, str]:
    """
    Get AWS service endpoints for the specified region.
    
    Args:
        region_name: AWS region name
        
    Returns:
        Dict mapping service names to their endpoints
    """
    return {
        'forecast': f'https://forecast.{region_name}.amazonaws.com',
        'forecastquery': f'https://forecastquery.{region_name}.amazonaws.com',
        'quicksight': f'https://quicksight.{region_name}.amazonaws.com',
        'comprehend': f'https://comprehend.{region_name}.amazonaws.com',
        's3': f'https://s3.{region_name}.amazonaws.com'
    }