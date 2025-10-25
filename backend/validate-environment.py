#!/usr/bin/env python3
"""
Environment validation script for Farmer Budget Optimizer.
Validates configuration and dependencies before deployment.
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class EnvironmentValidator:
    """Validates environment configuration and dependencies."""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        
    def log_issue(self, message: str):
        """Log a critical issue."""
        self.issues.append(message)
        print(f"✗ {message}")
    
    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        print(f"⚠ {message}")
    
    def log_success(self, message: str):
        """Log a success."""
        print(f"✓ {message}")
    
    def validate_python_version(self) -> bool:
        """Validate Python version."""
        print("Validating Python version...")
        
        if sys.version_info < (3, 8):
            self.log_issue(f"Python 3.8+ required, found {sys.version_info.major}.{sys.version_info.minor}")
            return False
        
        self.log_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    
    def validate_dependencies(self) -> bool:
        """Validate Python dependencies."""
        print("Validating Python dependencies...")
        
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.log_issue("requirements.txt not found")
            return False
        
        try:
            # Check if virtual environment exists
            venv_path = self.project_root / "venv"
            if not venv_path.exists():
                self.log_warning("Virtual environment not found")
            else:
                self.log_success("Virtual environment found")
            
            # Try importing key dependencies
            key_deps = [
                "fastapi",
                "uvicorn",
                "pydantic",
                "boto3",
                "requests"
            ]
            
            for dep in key_deps:
                try:
                    __import__(dep)
                    self.log_success(f"{dep} available")
                except ImportError:
                    self.log_issue(f"Required dependency {dep} not installed")
                    return False
            
            return True
            
        except Exception as e:
            self.log_issue(f"Dependency validation failed: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """Validate application configuration."""
        print("Validating application configuration...")
        
        env_file = self.project_root / f".env.{self.environment}"
        if not env_file.exists():
            self.log_issue(f"Environment file .env.{self.environment} not found")
            return False
        
        self.log_success(f"Environment file .env.{self.environment} found")
        
        try:
            # Load and validate configuration
            sys.path.insert(0, str(self.project_root))
            os.environ["ENVIRONMENT"] = self.environment
            
            from config import get_settings
            settings = get_settings()
            
            # Validate required settings
            required_settings = [
                "app_name",
                "environment",
                "host",
                "port",
                "aws_region"
            ]
            
            for setting in required_settings:
                value = getattr(settings, setting, None)
                if value is None:
                    self.log_issue(f"Required setting {setting} not configured")
                    return False
                else:
                    self.log_success(f"{setting}: {value}")
            
            # Validate environment-specific settings
            if self.environment == "production":
                prod_settings = [
                    "aws_access_key_id",
                    "aws_secret_access_key"
                ]
                
                for setting in prod_settings:
                    value = getattr(settings, setting, None)
                    if not value or "your_" in str(value).lower():
                        self.log_issue(f"Production setting {setting} not properly configured")
                        return False
                    else:
                        self.log_success(f"{setting}: configured")
            
            return True
            
        except Exception as e:
            self.log_issue(f"Configuration validation failed: {e}")
            return False
    
    def validate_aws_credentials(self) -> bool:
        """Validate AWS credentials and permissions."""
        print("Validating AWS credentials...")
        
        if self.environment == "development":
            self.log_success("Skipping AWS validation for development environment")
            return True
        
        try:
            # Load settings
            sys.path.insert(0, str(self.project_root))
            from config import get_settings
            settings = get_settings()
            
            # Create AWS session
            session = boto3.Session(**settings.get_aws_config())
            
            # Test STS (basic credential validation)
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            self.log_success(f"AWS credentials valid for account: {identity.get('Account', 'Unknown')}")
            
            # Test required services
            services_to_test = [
                ('forecast', 'Amazon Forecast'),
                ('quicksight', 'AWS QuickSight'),
                ('comprehend', 'AWS Comprehend'),
                ('s3', 'Amazon S3')
            ]
            
            for service_name, service_display in services_to_test:
                try:
                    client = session.client(service_name)
                    
                    # Test basic service access
                    if service_name == 'forecast':
                        client.list_datasets()
                    elif service_name == 'quicksight':
                        client.list_users(AwsAccountId=identity['Account'], Namespace='default')
                    elif service_name == 'comprehend':
                        client.list_sentiment_detection_jobs()
                    elif service_name == 's3':
                        client.list_buckets()
                    
                    self.log_success(f"{service_display} access verified")
                    
                except ClientError as e:
                    error_code = e.response['Error']['Code']
                    if error_code in ['AccessDenied', 'UnauthorizedOperation']:
                        self.log_warning(f"{service_display} access denied - check IAM permissions")
                    else:
                        self.log_success(f"{service_display} service accessible")
                except Exception as e:
                    self.log_warning(f"{service_display} validation failed: {e}")
            
            return True
            
        except NoCredentialsError:
            self.log_issue("AWS credentials not found")
            return False
        except Exception as e:
            self.log_issue(f"AWS validation failed: {e}")
            return False
    
    def validate_network_connectivity(self) -> bool:
        """Validate network connectivity."""
        print("Validating network connectivity...")
        
        # Test external connectivity
        test_urls = [
            "https://httpbin.org/get",
            "https://aws.amazon.com",
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    self.log_success(f"Connectivity to {url}")
                else:
                    self.log_warning(f"Unexpected response from {url}: {response.status_code}")
            except Exception as e:
                self.log_warning(f"Cannot reach {url}: {e}")
        
        return True
    
    def validate_system_resources(self) -> bool:
        """Validate system resources."""
        print("Validating system resources...")
        
        try:
            # Check disk space
            import shutil
            total, used, free = shutil.disk_usage(self.project_root)
            free_gb = free // (1024**3)
            
            if free_gb < 1:
                self.log_issue(f"Insufficient disk space: {free_gb}GB free")
                return False
            elif free_gb < 5:
                self.log_warning(f"Low disk space: {free_gb}GB free")
            else:
                self.log_success(f"Disk space: {free_gb}GB free")
            
            # Check memory (basic check)
            try:
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    for line in meminfo.split('\n'):
                        if 'MemAvailable:' in line:
                            mem_kb = int(line.split()[1])
                            mem_gb = mem_kb / (1024**2)
                            
                            if mem_gb < 0.5:
                                self.log_warning(f"Low memory: {mem_gb:.1f}GB available")
                            else:
                                self.log_success(f"Memory: {mem_gb:.1f}GB available")
                            break
            except:
                self.log_warning("Cannot check memory usage")
            
            return True
            
        except Exception as e:
            self.log_warning(f"System resource check failed: {e}")
            return True  # Non-critical
    
    def validate_ports(self) -> bool:
        """Validate required ports are available."""
        print("Validating port availability...")
        
        import socket
        
        ports_to_check = [8000]  # Main application port
        
        if self.environment in ["production", "staging"]:
            ports_to_check.extend([80, 443])  # HTTP/HTTPS
        
        for port in ports_to_check:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('127.0.0.1', port))
                    
                    if result == 0:
                        self.log_warning(f"Port {port} is already in use")
                    else:
                        self.log_success(f"Port {port} is available")
            except Exception as e:
                self.log_warning(f"Cannot check port {port}: {e}")
        
        return True
    
    def validate_file_permissions(self) -> bool:
        """Validate file permissions."""
        print("Validating file permissions...")
        
        # Check if we can create necessary directories
        test_dirs = ["logs", "data", "cache", "backups"]
        
        for dir_name in test_dirs:
            dir_path = self.project_root / dir_name
            try:
                dir_path.mkdir(exist_ok=True)
                
                # Test write permissions
                test_file = dir_path / "test_write"
                test_file.write_text("test")
                test_file.unlink()
                
                self.log_success(f"Directory {dir_name} writable")
                
            except Exception as e:
                self.log_issue(f"Cannot write to {dir_name}: {e}")
                return False
        
        return True
    
    def validate_application_startup(self) -> bool:
        """Validate application can start."""
        print("Validating application startup...")
        
        try:
            # Try importing the main application
            sys.path.insert(0, str(self.project_root))
            
            from app.main import app
            self.log_success("Application imports successfully")
            
            # Try creating FastAPI app (basic validation)
            if hasattr(app, 'routes'):
                route_count = len(app.routes)
                self.log_success(f"Application has {route_count} routes configured")
            
            return True
            
        except Exception as e:
            self.log_issue(f"Application startup validation failed: {e}")
            return False
    
    def run_validation(self) -> Tuple[bool, Dict]:
        """Run complete validation suite."""
        print(f"Running environment validation for {self.environment}...")
        print("=" * 60)
        
        validation_results = {}
        
        # Run all validations
        validations = [
            ("Python Version", self.validate_python_version),
            ("Dependencies", self.validate_dependencies),
            ("Configuration", self.validate_configuration),
            ("AWS Credentials", self.validate_aws_credentials),
            ("Network Connectivity", self.validate_network_connectivity),
            ("System Resources", self.validate_system_resources),
            ("Port Availability", self.validate_ports),
            ("File Permissions", self.validate_file_permissions),
            ("Application Startup", self.validate_application_startup)
        ]
        
        for name, validation_func in validations:
            print(f"\n{name}:")
            try:
                result = validation_func()
                validation_results[name] = result
            except Exception as e:
                self.log_issue(f"{name} validation failed with exception: {e}")
                validation_results[name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in validation_results.values() if result)
        total = len(validation_results)
        
        print(f"Validations passed: {passed}/{total}")
        
        if self.issues:
            print(f"\nCritical issues ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  ✗ {issue}")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        success = len(self.issues) == 0
        
        if success:
            print(f"\n✓ Environment validation passed for {self.environment}")
        else:
            print(f"\n✗ Environment validation failed for {self.environment}")
            print("Please resolve critical issues before deployment.")
        
        return success, {
            "passed": passed,
            "total": total,
            "issues": self.issues,
            "warnings": self.warnings,
            "results": validation_results
        }

def main():
    """Main validation entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate environment for Farmer Budget Optimizer")
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "staging", "production"],
        default="development",
        help="Environment to validate"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    validator = EnvironmentValidator(args.environment)
    success, results = validator.run_validation()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()