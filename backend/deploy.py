#!/usr/bin/env python3
"""
Deployment script for the Farmer Budget Optimizer.
Handles deployment to different environments with proper configuration.
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

class DeploymentManager:
    """Manages deployment process for different environments."""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent
        self.app_dir = self.project_root / "app"
        
    def validate_environment(self):
        """Validate the deployment environment."""
        valid_environments = ["development", "staging", "production"]
        if self.environment not in valid_environments:
            raise ValueError(f"Invalid environment: {self.environment}. Must be one of: {valid_environments}")
    
    def check_prerequisites(self) -> List[str]:
        """Check deployment prerequisites."""
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append("Python 3.8 or higher is required")
        
        # Check required files
        required_files = [
            "requirements.txt",
            f".env.{self.environment}",
            "app/main.py"
        ]
        
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                issues.append(f"Required file missing: {file_path}")
        
        # Check AWS credentials for production
        if self.environment == "production":
            aws_vars = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
            for var in aws_vars:
                if not os.getenv(var):
                    issues.append(f"AWS credential missing: {var}")
        
        return issues
    
    def install_dependencies(self):
        """Install Python dependencies."""
        print("Installing dependencies...")
        
        # Create virtual environment if it doesn't exist
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Determine pip path
        if os.name == "nt":  # Windows
            pip_path = venv_path / "Scripts" / "pip.exe"
            python_path = venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
        
        # Upgrade pip
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([
            str(pip_path), "install", "-r", "requirements.txt"
        ], check=True, cwd=self.project_root)
        
        print("Dependencies installed successfully")
    
    def setup_directories(self):
        """Set up necessary directories."""
        print("Setting up directories...")
        
        directories = [
            "logs",
            "data", 
            "cache",
            "backups"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(exist_ok=True)
            print(f"Created directory: {dir_path}")
    
    def setup_environment(self):
        """Set up environment configuration."""
        print(f"Setting up {self.environment} environment...")
        
        # Copy environment-specific config
        env_source = self.project_root / f".env.{self.environment}"
        env_target = self.project_root / ".env"
        
        if env_source.exists():
            import shutil
            shutil.copy2(env_source, env_target)
            print(f"Copied {env_source} to {env_target}")
        else:
            print(f"Warning: {env_source} not found")
    
    def validate_configuration(self):
        """Validate the application configuration."""
        print("Validating configuration...")
        
        try:
            # Import and validate settings
            sys.path.insert(0, str(self.project_root))
            from config import get_settings
            
            settings = get_settings()
            print(f"Configuration valid for environment: {settings.environment}")
            
            # Test AWS configuration if not using mock data
            if not settings.use_mock_data and self.environment != "development":
                try:
                    import boto3
                    session = boto3.Session(**settings.get_aws_config())
                    sts = session.client('sts')
                    identity = sts.get_caller_identity()
                    print(f"AWS credentials valid for account: {identity.get('Account', 'Unknown')}")
                except Exception as e:
                    print(f"Warning: AWS credentials validation failed: {e}")
            
        except Exception as e:
            raise RuntimeError(f"Configuration validation failed: {e}")
    
    def create_systemd_service(self):
        """Create systemd service file for production deployment."""
        if self.environment not in ["production", "staging"]:
            return
        
        print(f"Creating systemd service file for {self.environment}...")
        
        # Determine service configuration based on environment
        workers = 4 if self.environment == "production" else 2
        service_name = f"farmer-budget-optimizer-{self.environment}"
        
        service_content = f"""[Unit]
Description=Farmer Budget Optimizer API ({self.environment})
After=network.target
Wants=network-online.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/venv/bin
Environment=ENVIRONMENT={self.environment}
Environment=PYTHONPATH={self.project_root}
ExecStart={self.project_root}/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers {workers}
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier={service_name}

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={self.project_root}/logs {self.project_root}/data {self.project_root}/cache {self.project_root}/backups

# Resource limits
LimitNOFILE=65536
MemoryMax=2G

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path(f"/etc/systemd/system/{service_name}.service")
        try:
            with open(service_file, "w") as f:
                f.write(service_content)
            print(f"Created systemd service: {service_file}")
            
            # Reload systemd and enable service
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            subprocess.run(["systemctl", "enable", service_name], check=True)
            print(f"Systemd service {service_name} enabled")
            
        except PermissionError:
            print("Warning: Could not create systemd service (requires root privileges)")
            service_filename = f"{service_name}.service"
            print(f"Service file content saved to: {service_filename}")
            with open(service_filename, "w") as f:
                f.write(service_content)
    
    def create_nginx_config(self):
        """Create nginx configuration for production."""
        if self.environment not in ["production", "staging"]:
            return
        
        print(f"Creating nginx configuration for {self.environment}...")
        
        # Environment-specific configuration
        if self.environment == "production":
            server_name = "your-domain.com www.your-domain.com"
            ssl_cert_path = "/etc/ssl/certs/farmer-budget-optimizer.crt"
            ssl_key_path = "/etc/ssl/private/farmer-budget-optimizer.key"
        else:  # staging
            server_name = "staging.your-domain.com"
            ssl_cert_path = "/etc/ssl/certs/farmer-budget-optimizer-staging.crt"
            ssl_key_path = "/etc/ssl/private/farmer-budget-optimizer-staging.key"
        
        nginx_content = f"""# Farmer Budget Optimizer - {self.environment.title()} Configuration

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_{self.environment}:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=health_{self.environment}:10m rate=1r/s;

# Upstream backend
upstream farmer_budget_api_{self.environment} {{
    server 127.0.0.1:8000;
    keepalive 32;
}}

# HTTP server (redirect to HTTPS)
server {{
    listen 80;
    server_name {server_name};
    
    # Health check endpoint (allow HTTP for load balancers)
    location /api/health {{
        limit_req zone=health_{self.environment} burst=5 nodelay;
        proxy_pass http://farmer_budget_api_{self.environment};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }}
    
    # Redirect all other traffic to HTTPS
    location / {{
        return 301 https://$server_name$request_uri;
    }}
}}

# HTTPS server
server {{
    listen 443 ssl http2;
    server_name {server_name};
    
    # SSL configuration
    ssl_certificate {ssl_cert_path};
    ssl_certificate_key {ssl_key_path};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-RC4-SHA:ECDHE-RSA-AES256-SHA:AES256-GCM-SHA384:AES256-SHA256:AES256-SHA:AES128-GCM-SHA256:AES128-SHA256:AES128-SHA:RC4-SHA;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https:; frame-ancestors 'none';" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # API endpoints
    location /api/ {{
        limit_req zone=api_{self.environment} burst=20 nodelay;
        
        proxy_pass http://farmer_budget_api_{self.environment};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        proxy_buffering off;
        
        # CORS headers for API
        add_header 'Access-Control-Allow-Origin' '$http_origin' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-API-Key' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range,X-Request-ID' always;
        
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {{
            add_header 'Access-Control-Allow-Origin' '$http_origin';
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS, PUT, DELETE';
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization,X-API-Key';
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }}
    }}
    
    # Health check endpoint
    location /api/health {{
        limit_req zone=health_{self.environment} burst=5 nodelay;
        proxy_pass http://farmer_budget_api_{self.environment};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        access_log off;
    }}
    
    # Static files (if serving frontend from same server)
    location / {{
        root /var/www/farmer-budget-optimizer-{self.environment};
        try_files $uri $uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Security headers for static files
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;
    }}
    
    # Deny access to sensitive files
    location ~ /\\.(?!well-known) {{
        deny all;
    }}
    
    location ~ ^/(logs|data|cache|backups)/ {{
        deny all;
    }}
    
    # Logging
    access_log /var/log/nginx/farmer-budget-optimizer-{self.environment}.access.log;
    error_log /var/log/nginx/farmer-budget-optimizer-{self.environment}.error.log;
}}
"""
        
        config_filename = f"nginx-farmer-budget-optimizer-{self.environment}.conf"
        with open(config_filename, "w") as f:
            f.write(nginx_content)
        print(f"Nginx configuration saved to: {config_filename}")
        print(f"Copy this file to /etc/nginx/sites-available/ and create a symlink in /etc/nginx/sites-enabled/")
        print(f"Then run: sudo nginx -t && sudo systemctl reload nginx")
    
    def run_health_check(self, max_retries: int = 5, retry_delay: int = 10):
        """Run comprehensive health check to verify deployment."""
        print("Running comprehensive health check...")
        
        try:
            import requests
            import time
            
            # Wait for service to start
            print("Waiting for service to start...")
            time.sleep(5)
            
            for attempt in range(max_retries):
                try:
                    print(f"Health check attempt {attempt + 1}/{max_retries}...")
                    
                    # Check health endpoint
                    response = requests.get("http://127.0.0.1:8000/api/health", timeout=30)
                    
                    if response.status_code == 200:
                        health_data = response.json()
                        print(f"✓ Health check passed: {health_data['status']}")
                        
                        # Check service details if available
                        if 'details' in health_data:
                            services = health_data['details'].get('services', {})
                            for service, status in services.items():
                                status_icon = "✓" if status == "AVAILABLE" else "⚠" if status == "DEGRADED" else "✗"
                                print(f"  {status_icon} {service}: {status}")
                        
                        # Test API endpoints
                        print("Testing API endpoints...")
                        
                        # Test root endpoint
                        try:
                            root_response = requests.get("http://127.0.0.1:8000/", timeout=10)
                            if root_response.status_code == 200:
                                print("✓ Root endpoint accessible")
                            else:
                                print(f"⚠ Root endpoint returned {root_response.status_code}")
                        except Exception as e:
                            print(f"✗ Root endpoint failed: {e}")
                        
                        # Test docs endpoint
                        try:
                            docs_response = requests.get("http://127.0.0.1:8000/docs", timeout=10)
                            if docs_response.status_code == 200:
                                print("✓ API documentation accessible")
                            else:
                                print(f"⚠ API docs returned {docs_response.status_code}")
                        except Exception as e:
                            print(f"✗ API docs failed: {e}")
                        
                        return True
                    else:
                        print(f"Health check failed: HTTP {response.status_code}")
                        if attempt < max_retries - 1:
                            print(f"Retrying in {retry_delay} seconds...")
                            time.sleep(retry_delay)
                        
                except requests.exceptions.ConnectionError:
                    print(f"Connection failed (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                except Exception as e:
                    print(f"Health check error: {e}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
            
            print("✗ Health check failed after all retries")
            return False
                
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def setup_monitoring(self):
        """Set up basic monitoring and logging."""
        print("Setting up monitoring and logging...")
        
        # Create log rotation configuration
        logrotate_config = f"""# Farmer Budget Optimizer log rotation
/app/logs/*.log {{
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload farmer-budget-optimizer-{self.environment} > /dev/null 2>&1 || true
    endscript
}}
"""
        
        try:
            logrotate_file = f"/etc/logrotate.d/farmer-budget-optimizer-{self.environment}"
            with open(logrotate_file, "w") as f:
                f.write(logrotate_config)
            print(f"✓ Log rotation configured: {logrotate_file}")
        except PermissionError:
            print("⚠ Could not create logrotate config (requires root privileges)")
            with open(f"logrotate-farmer-budget-optimizer-{self.environment}", "w") as f:
                f.write(logrotate_config)
            print(f"Log rotation config saved to: logrotate-farmer-budget-optimizer-{self.environment}")
        
        # Create monitoring script
        monitoring_script = f"""#!/bin/bash
# Farmer Budget Optimizer monitoring script

SERVICE_NAME="farmer-budget-optimizer-{self.environment}"
HEALTH_URL="http://127.0.0.1:8000/api/health"
LOG_FILE="/var/log/farmer-budget-optimizer-monitor.log"

# Function to log with timestamp
log_message() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}}

# Check service status
if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    log_message "ERROR: Service $SERVICE_NAME is not running"
    systemctl restart "$SERVICE_NAME"
    log_message "INFO: Attempted to restart $SERVICE_NAME"
    exit 1
fi

# Check health endpoint
if ! curl -f -s "$HEALTH_URL" > /dev/null; then
    log_message "ERROR: Health check failed for $SERVICE_NAME"
    systemctl restart "$SERVICE_NAME"
    log_message "INFO: Attempted to restart $SERVICE_NAME due to health check failure"
    exit 1
fi

log_message "INFO: Service $SERVICE_NAME is healthy"
exit 0
"""
        
        monitor_script_path = f"monitor-farmer-budget-optimizer-{self.environment}.sh"
        with open(monitor_script_path, "w") as f:
            f.write(monitoring_script)
        
        # Make script executable
        import stat
        os.chmod(monitor_script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        
        print(f"✓ Monitoring script created: {monitor_script_path}")
        print(f"Add to crontab: */5 * * * * /path/to/{monitor_script_path}")
        
        # Create backup script
        backup_script = f"""#!/bin/bash
# Farmer Budget Optimizer backup script

BACKUP_DIR="/app/backups"
DATA_DIR="/app/data"
CACHE_DIR="/app/cache"
LOGS_DIR="/app/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/farmer-budget-optimizer-{self.environment}-$TIMESTAMP.tar.gz"

# Create backup
tar -czf "$BACKUP_FILE" -C / app/data app/cache app/logs 2>/dev/null

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "farmer-budget-optimizer-{self.environment}-*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
"""
        
        backup_script_path = f"backup-farmer-budget-optimizer-{self.environment}.sh"
        with open(backup_script_path, "w") as f:
            f.write(backup_script)
        
        os.chmod(backup_script_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IROTH)
        
        print(f"✓ Backup script created: {backup_script_path}")
        print(f"Add to crontab: 0 2 * * * /path/to/{backup_script_path}")
    
    def create_deployment_summary(self):
        """Create deployment summary and next steps."""
        print("\n" + "="*60)
        print(f"DEPLOYMENT SUMMARY - {self.environment.upper()}")
        print("="*60)
        
        print(f"\n✓ Environment: {self.environment}")
        print(f"✓ Application directory: {self.project_root}")
        print(f"✓ Virtual environment: {self.project_root}/venv")
        print(f"✓ Configuration: .env.{self.environment}")
        
        print(f"\nGenerated files:")
        if self.environment in ["production", "staging"]:
            print(f"  - farmer-budget-optimizer-{self.environment}.service")
            print(f"  - nginx-farmer-budget-optimizer-{self.environment}.conf")
            print(f"  - monitor-farmer-budget-optimizer-{self.environment}.sh")
            print(f"  - backup-farmer-budget-optimizer-{self.environment}.sh")
            print(f"  - logrotate-farmer-budget-optimizer-{self.environment}")
        
        print(f"\nNext steps:")
        if self.environment == "development":
            print("  1. Start the application:")
            print("     python deploy.py --environment development --start")
            print("  2. Access the API at: http://127.0.0.1:8000")
            print("  3. View API docs at: http://127.0.0.1:8000/docs")
        else:
            service_name = f"farmer-budget-optimizer-{self.environment}"
            print("  1. Copy systemd service file (requires root):")
            print(f"     sudo cp {service_name}.service /etc/systemd/system/")
            print("     sudo systemctl daemon-reload")
            print(f"     sudo systemctl enable {service_name}")
            
            print("  2. Copy nginx configuration (requires root):")
            print(f"     sudo cp nginx-farmer-budget-optimizer-{self.environment}.conf /etc/nginx/sites-available/")
            print(f"     sudo ln -s /etc/nginx/sites-available/nginx-farmer-budget-optimizer-{self.environment}.conf /etc/nginx/sites-enabled/")
            print("     sudo nginx -t && sudo systemctl reload nginx")
            
            print("  3. Set up SSL certificates:")
            print("     - Obtain SSL certificates for your domain")
            print("     - Update certificate paths in nginx configuration")
            
            print("  4. Configure AWS credentials:")
            print(f"     - Update .env.{self.environment} with real AWS credentials")
            print("     - Ensure IAM permissions are properly configured")
            
            print("  5. Start the service:")
            print(f"     sudo systemctl start {service_name}")
            print(f"     sudo systemctl status {service_name}")
            
            print("  6. Set up monitoring (optional):")
            print(f"     - Add monitoring script to crontab")
            print(f"     - Add backup script to crontab")
            print(f"     - Configure log rotation")
        
        print(f"\nHealth check:")
        print("  curl http://127.0.0.1:8000/api/health")
        
        print(f"\nLogs location:")
        if self.environment == "development":
            print(f"  {self.project_root}/logs/app.log")
        else:
            print(f"  sudo journalctl -u {service_name} -f")
            print(f"  /var/log/nginx/farmer-budget-optimizer-{self.environment}.access.log")
        
        print("\n" + "="*60)
    
    def start_application(self):
        """Start the application."""
        print(f"Starting application in {self.environment} mode...")
        
        if self.environment == "development":
            # Development mode with auto-reload
            cmd = [
                str(self.project_root / "venv" / ("Scripts" if os.name == "nt" else "bin") / "uvicorn"),
                "app.main:app",
                "--host", "127.0.0.1",
                "--port", "8000",
                "--reload"
            ]
        elif self.environment == "production":
            # Production mode
            cmd = [
                str(self.project_root / "venv" / ("Scripts" if os.name == "nt" else "bin") / "uvicorn"),
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--workers", "4"
            ]
        else:
            # Staging mode
            cmd = [
                str(self.project_root / "venv" / ("Scripts" if os.name == "nt" else "bin") / "uvicorn"),
                "app.main:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--workers", "2"
            ]
        
        print(f"Running command: {' '.join(cmd)}")
        
        if self.environment == "development":
            # Run in foreground for development
            subprocess.run(cmd, cwd=self.project_root)
        else:
            # For production, recommend using systemd
            print("For production deployment, use systemd service:")
            print("sudo systemctl start farmer-budget-optimizer")
            print("sudo systemctl status farmer-budget-optimizer")
    
    def deploy(self):
        """Run full deployment process."""
        print(f"Starting deployment for {self.environment} environment...")
        
        try:
            # Validate environment
            self.validate_environment()
            
            # Check prerequisites
            issues = self.check_prerequisites()
            if issues:
                print("Deployment prerequisites not met:")
                for issue in issues:
                    print(f"  - {issue}")
                return False
            
            # Run deployment steps
            self.install_dependencies()
            self.setup_directories()
            self.setup_environment()
            self.validate_configuration()
            
            if self.environment in ["production", "staging"]:
                self.create_systemd_service()
                self.create_nginx_config()
                self.setup_monitoring()
            
            # Create deployment summary
            self.create_deployment_summary()
            
            print(f"\n✓ Deployment completed successfully for {self.environment} environment!")
            
            return True
            
        except Exception as e:
            print(f"✗ Deployment failed: {e}")
            return False

def main():
    """Main deployment script entry point."""
    parser = argparse.ArgumentParser(description="Deploy Farmer Budget Optimizer")
    parser.add_argument(
        "--environment", "-e",
        choices=["development", "staging", "production"],
        default="development",
        help="Deployment environment"
    )
    parser.add_argument(
        "--start", "-s",
        action="store_true",
        help="Start the application after deployment"
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Run health check only"
    )
    
    args = parser.parse_args()
    
    deployer = DeploymentManager(args.environment)
    
    if args.health_check:
        success = deployer.run_health_check()
        sys.exit(0 if success else 1)
    
    if args.start:
        deployer.start_application()
    else:
        success = deployer.deploy()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()