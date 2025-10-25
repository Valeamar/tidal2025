#!/usr/bin/env python3
"""
Deployment verification script for Farmer Budget Optimizer.
Verifies that the deployment is working correctly.
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

class DeploymentVerifier:
    """Verifies deployment is working correctly."""
    
    def __init__(self, environment: str = "development", base_url: str = None):
        self.environment = environment
        self.base_url = base_url or "http://127.0.0.1:8000"
        self.project_root = Path(__file__).parent
        self.results = {}
        
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result."""
        self.results[test_name] = {"success": success, "message": message}
        status = "✓" if success else "✗"
        print(f"{status} {test_name}: {message}")
    
    def test_service_status(self) -> bool:
        """Test if the service is running (for production/staging)."""
        if self.environment == "development":
            return True
        
        service_name = f"farmer-budget-optimizer-{self.environment}"
        
        try:
            result = subprocess.run(
                ["systemctl", "is-active", service_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip() == "active":
                self.log_result("Service Status", True, f"{service_name} is active")
                return True
            else:
                self.log_result("Service Status", False, f"{service_name} is not active")
                return False
                
        except Exception as e:
            self.log_result("Service Status", False, f"Cannot check service status: {e}")
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test the health endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=30)
            
            if response.status_code == 200:
                health_data = response.json()
                status = health_data.get("status", "unknown")
                
                if status == "healthy":
                    self.log_result("Health Endpoint", True, "Service is healthy")
                    return True
                elif status == "degraded":
                    self.log_result("Health Endpoint", True, "Service is degraded but functional")
                    return True
                else:
                    self.log_result("Health Endpoint", False, f"Service status: {status}")
                    return False
            else:
                self.log_result("Health Endpoint", False, f"HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_result("Health Endpoint", False, "Cannot connect to service")
            return False
        except Exception as e:
            self.log_result("Health Endpoint", False, f"Health check failed: {e}")
            return False
    
    def test_readiness_endpoint(self) -> bool:
        """Test the readiness endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/ready", timeout=10)
            
            if response.status_code == 200:
                self.log_result("Readiness Endpoint", True, "Service is ready")
                return True
            else:
                ready_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                message = ready_data.get("status", f"HTTP {response.status_code}")
                self.log_result("Readiness Endpoint", False, message)
                return False
                
        except Exception as e:
            self.log_result("Readiness Endpoint", False, f"Readiness check failed: {e}")
            return False
    
    def test_liveness_endpoint(self) -> bool:
        """Test the liveness endpoint."""
        try:
            response = requests.get(f"{self.base_url}/api/live", timeout=10)
            
            if response.status_code == 200:
                self.log_result("Liveness Endpoint", True, "Service is alive")
                return True
            else:
                self.log_result("Liveness Endpoint", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Liveness Endpoint", False, f"Liveness check failed: {e}")
            return False
    
    def test_api_documentation(self) -> bool:
        """Test API documentation endpoints."""
        endpoints = [
            ("/docs", "Swagger UI"),
            ("/redoc", "ReDoc"),
            ("/openapi.json", "OpenAPI Schema")
        ]
        
        all_success = True
        
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    self.log_result(f"API Docs - {name}", True, "Accessible")
                else:
                    self.log_result(f"API Docs - {name}", False, f"HTTP {response.status_code}")
                    all_success = False
                    
            except Exception as e:
                self.log_result(f"API Docs - {name}", False, f"Failed: {e}")
                all_success = False
        
        return all_success
    
    def test_cors_configuration(self) -> bool:
        """Test CORS configuration."""
        try:
            # Test preflight request
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{self.base_url}/api/health", headers=headers, timeout=10)
            
            if response.status_code in [200, 204]:
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                }
                
                if any(cors_headers.values()):
                    self.log_result("CORS Configuration", True, "CORS headers present")
                    return True
                else:
                    self.log_result("CORS Configuration", False, "No CORS headers found")
                    return False
            else:
                self.log_result("CORS Configuration", False, f"Preflight failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("CORS Configuration", False, f"CORS test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling."""
        try:
            # Test 404 error
            response = requests.get(f"{self.base_url}/api/nonexistent", timeout=10)
            
            if response.status_code == 404:
                self.log_result("Error Handling - 404", True, "Returns proper 404")
            else:
                self.log_result("Error Handling - 404", False, f"Expected 404, got {response.status_code}")
                return False
            
            # Test method not allowed
            response = requests.patch(f"{self.base_url}/api/health", timeout=10)
            
            if response.status_code == 405:
                self.log_result("Error Handling - 405", True, "Returns proper 405")
            else:
                self.log_result("Error Handling - 405", False, f"Expected 405, got {response.status_code}")
                return False
            
            return True
            
        except Exception as e:
            self.log_result("Error Handling", False, f"Error handling test failed: {e}")
            return False
    
    def test_response_times(self) -> bool:
        """Test response times."""
        endpoints = [
            "/api/health",
            "/api/ready",
            "/api/live"
        ]
        
        all_fast = True
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200 and response_time < 1000:  # Less than 1 second
                    self.log_result(f"Response Time - {endpoint}", True, f"{response_time:.0f}ms")
                elif response.status_code == 200:
                    self.log_result(f"Response Time - {endpoint}", False, f"Slow response: {response_time:.0f}ms")
                    all_fast = False
                else:
                    self.log_result(f"Response Time - {endpoint}", False, f"HTTP {response.status_code}")
                    all_fast = False
                    
            except Exception as e:
                self.log_result(f"Response Time - {endpoint}", False, f"Failed: {e}")
                all_fast = False
        
        return all_fast
    
    def test_ssl_configuration(self) -> bool:
        """Test SSL configuration (for production)."""
        if self.environment == "development" or not self.base_url.startswith("https"):
            self.log_result("SSL Configuration", True, "Skipped for development/HTTP")
            return True
        
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10, verify=True)
            
            if response.status_code == 200:
                self.log_result("SSL Configuration", True, "SSL certificate valid")
                return True
            else:
                self.log_result("SSL Configuration", False, f"HTTPS request failed: {response.status_code}")
                return False
                
        except requests.exceptions.SSLError as e:
            self.log_result("SSL Configuration", False, f"SSL error: {e}")
            return False
        except Exception as e:
            self.log_result("SSL Configuration", False, f"SSL test failed: {e}")
            return False
    
    def test_log_files(self) -> bool:
        """Test log file creation and writing."""
        try:
            # Check if log directory exists
            log_dir = self.project_root / "logs"
            if not log_dir.exists():
                self.log_result("Log Files", False, "Log directory does not exist")
                return False
            
            # Check for log files
            log_files = list(log_dir.glob("*.log"))
            
            if log_files:
                # Check if log files are being written to
                latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
                file_age = time.time() - latest_log.stat().st_mtime
                
                if file_age < 3600:  # Less than 1 hour old
                    self.log_result("Log Files", True, f"Recent log activity in {latest_log.name}")
                    return True
                else:
                    self.log_result("Log Files", False, f"No recent log activity (last: {file_age/3600:.1f}h ago)")
                    return False
            else:
                self.log_result("Log Files", False, "No log files found")
                return False
                
        except Exception as e:
            self.log_result("Log Files", False, f"Log file test failed: {e}")
            return False
    
    def run_verification(self) -> bool:
        """Run complete verification suite."""
        print(f"Running deployment verification for {self.environment}...")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        # Run all tests
        tests = [
            ("Service Status", self.test_service_status),
            ("Health Endpoint", self.test_health_endpoint),
            ("Readiness Endpoint", self.test_readiness_endpoint),
            ("Liveness Endpoint", self.test_liveness_endpoint),
            ("API Documentation", self.test_api_documentation),
            ("CORS Configuration", self.test_cors_configuration),
            ("Error Handling", self.test_error_handling),
            ("Response Times", self.test_response_times),
            ("SSL Configuration", self.test_ssl_configuration),
            ("Log Files", self.test_log_files)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n{test_name}:")
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_result(test_name, False, f"Test failed with exception: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        print(f"Tests passed: {passed}/{total}")
        
        failed_tests = [name for name, result in self.results.items() if not result["success"]]
        
        if failed_tests:
            print(f"\nFailed tests:")
            for test in failed_tests:
                print(f"  ✗ {test}: {self.results[test]['message']}")
        
        success = passed == total
        
        if success:
            print(f"\n✓ Deployment verification passed for {self.environment}")
            print("The application is ready for use!")
        else:
            print(f"\n✗ Deployment verification failed for {self.environment}")
            print("Please resolve the issues above.")
        
        return success

def main():
    """Main verification entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify deployment of Farmer Budget Optimizer")
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "staging", "production"],
        default="development",
        help="Environment to verify"
    )
    parser.add_argument(
        "--url", "-u",
        help="Base URL to test (default: http://127.0.0.1:8000)"
    )
    parser.add_argument(
        "--wait", "-w",
        type=int,
        default=0,
        help="Wait time in seconds before starting verification"
    )
    
    args = parser.parse_args()
    
    if args.wait > 0:
        print(f"Waiting {args.wait} seconds for service to start...")
        time.sleep(args.wait)
    
    verifier = DeploymentVerifier(args.environment, args.url)
    success = verifier.run_verification()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()