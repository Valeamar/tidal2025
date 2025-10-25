#!/usr/bin/env python3
"""
Production setup script for Farmer Budget Optimizer.
Handles production-specific configuration and security setup.
"""

import os
import sys
import subprocess
import argparse
import json
import secrets
from pathlib import Path
from typing import Dict, List, Optional

class ProductionSetup:
    """Handles production-specific setup tasks."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        
    def generate_secrets(self) -> Dict[str, str]:
        """Generate secure secrets for production."""
        print("Generating secure secrets...")
        
        secrets_dict = {
            "SECRET_KEY": secrets.token_urlsafe(32),
            "API_SECRET": secrets.token_urlsafe(24),
            "SESSION_SECRET": secrets.token_urlsafe(32),
            "ENCRYPTION_KEY": secrets.token_urlsafe(32)
        }
        
        print("✓ Generated secure secrets")
        return secrets_dict
    
    def setup_ssl_certificates(self, domain: str, email: str):
        """Set up SSL certificates using Let's Encrypt."""
        print(f"Setting up SSL certificates for {domain}...")
        
        try:
            # Install certbot if not present
            subprocess.run(["which", "certbot"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("Installing certbot...")
            subprocess.run([
                "sudo", "apt-get", "update"
            ], check=True)
            subprocess.run([
                "sudo", "apt-get", "install", "-y", "certbot", "python3-certbot-nginx"
            ], check=True)
        
        # Obtain certificate
        try:
            subprocess.run([
                "sudo", "certbot", "--nginx",
                "-d", domain,
                "--email", email,
                "--agree-tos",
                "--non-interactive"
            ], check=True)
            print(f"✓ SSL certificate obtained for {domain}")
            
            # Set up auto-renewal
            subprocess.run([
                "sudo", "systemctl", "enable", "certbot.timer"
            ], check=True)
            print("✓ SSL certificate auto-renewal enabled")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ SSL certificate setup failed: {e}")
            return False
        
        return True
    
    def setup_firewall(self):
        """Configure UFW firewall for production."""
        print("Configuring firewall...")
        
        try:
            # Enable UFW
            subprocess.run(["sudo", "ufw", "--force", "enable"], check=True)
            
            # Default policies
            subprocess.run(["sudo", "ufw", "default", "deny", "incoming"], check=True)
            subprocess.run(["sudo", "ufw", "default", "allow", "outgoing"], check=True)
            
            # Allow SSH
            subprocess.run(["sudo", "ufw", "allow", "ssh"], check=True)
            
            # Allow HTTP and HTTPS
            subprocess.run(["sudo", "ufw", "allow", "80"], check=True)
            subprocess.run(["sudo", "ufw", "allow", "443"], check=True)
            
            # Allow application port (only from localhost)
            subprocess.run(["sudo", "ufw", "allow", "from", "127.0.0.1", "to", "any", "port", "8000"], check=True)
            
            print("✓ Firewall configured")
            
            # Show status
            result = subprocess.run(["sudo", "ufw", "status"], capture_output=True, text=True)
            print("Firewall status:")
            print(result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Firewall setup failed: {e}")
            return False
        
        return True
    
    def setup_system_user(self):
        """Create dedicated system user for the application."""
        print("Setting up system user...")
        
        try:
            # Check if user exists
            result = subprocess.run(["id", "farmer-budget"], capture_output=True)
            if result.returncode == 0:
                print("✓ User 'farmer-budget' already exists")
                return True
            
            # Create system user
            subprocess.run([
                "sudo", "useradd",
                "--system",
                "--shell", "/bin/false",
                "--home", "/var/lib/farmer-budget",
                "--create-home",
                "farmer-budget"
            ], check=True)
            
            # Create application directories
            app_dirs = [
                "/var/lib/farmer-budget/app",
                "/var/lib/farmer-budget/logs",
                "/var/lib/farmer-budget/data",
                "/var/lib/farmer-budget/cache",
                "/var/lib/farmer-budget/backups"
            ]
            
            for directory in app_dirs:
                subprocess.run(["sudo", "mkdir", "-p", directory], check=True)
                subprocess.run(["sudo", "chown", "farmer-budget:farmer-budget", directory], check=True)
            
            print("✓ System user 'farmer-budget' created")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ System user setup failed: {e}")
            return False
        
        return True
    
    def setup_database_security(self):
        """Set up database security (for future database integration)."""
        print("Setting up database security...")
        
        # For now, just secure file permissions for JSON storage
        try:
            data_dir = self.project_root / "data"
            if data_dir.exists():
                subprocess.run(["sudo", "chmod", "750", str(data_dir)], check=True)
                subprocess.run(["sudo", "chown", "-R", "farmer-budget:farmer-budget", str(data_dir)], check=True)
            
            cache_dir = self.project_root / "cache"
            if cache_dir.exists():
                subprocess.run(["sudo", "chmod", "750", str(cache_dir)], check=True)
                subprocess.run(["sudo", "chown", "-R", "farmer-budget:farmer-budget", str(cache_dir)], check=True)
            
            print("✓ File storage security configured")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Database security setup failed: {e}")
            return False
        
        return True
    
    def setup_log_monitoring(self):
        """Set up log monitoring and alerting."""
        print("Setting up log monitoring...")
        
        # Create rsyslog configuration for application logs
        rsyslog_config = """# Farmer Budget Optimizer logging
if $programname == 'farmer-budget-optimizer' then /var/log/farmer-budget-optimizer/app.log
& stop
"""
        
        try:
            with open("/tmp/farmer-budget-rsyslog.conf", "w") as f:
                f.write(rsyslog_config)
            
            subprocess.run([
                "sudo", "mv", "/tmp/farmer-budget-rsyslog.conf",
                "/etc/rsyslog.d/50-farmer-budget-optimizer.conf"
            ], check=True)
            
            # Create log directory
            subprocess.run(["sudo", "mkdir", "-p", "/var/log/farmer-budget-optimizer"], check=True)
            subprocess.run(["sudo", "chown", "syslog:adm", "/var/log/farmer-budget-optimizer"], check=True)
            
            # Restart rsyslog
            subprocess.run(["sudo", "systemctl", "restart", "rsyslog"], check=True)
            
            print("✓ Log monitoring configured")
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Log monitoring setup failed: {e}")
            return False
        
        return True
    
    def setup_performance_monitoring(self):
        """Set up basic performance monitoring."""
        print("Setting up performance monitoring...")
        
        # Create performance monitoring script
        monitor_script = """#!/bin/bash
# Performance monitoring script for Farmer Budget Optimizer

LOG_FILE="/var/log/farmer-budget-optimizer/performance.log"
SERVICE_NAME="farmer-budget-optimizer-production"

# Function to log with timestamp
log_metric() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | awk -F'%' '{print $1}')
log_metric "CPU_USAGE: ${CPU_USAGE}%"

# Memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", ($3/$2) * 100.0)}')
log_metric "MEMORY_USAGE: ${MEMORY_USAGE}%"

# Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
log_metric "DISK_USAGE: ${DISK_USAGE}%"

# Service status
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log_metric "SERVICE_STATUS: RUNNING"
else
    log_metric "SERVICE_STATUS: STOPPED"
fi

# Application response time
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' http://127.0.0.1:8000/api/health 2>/dev/null || echo "ERROR")
log_metric "RESPONSE_TIME: ${RESPONSE_TIME}s"

# Log file size
LOG_SIZE=$(du -sh /var/log/farmer-budget-optimizer/ 2>/dev/null | awk '{print $1}' || echo "0")
log_metric "LOG_SIZE: ${LOG_SIZE}"
"""
        
        try:
            with open("performance-monitor.sh", "w") as f:
                f.write(monitor_script)
            
            os.chmod("performance-monitor.sh", 0o755)
            
            print("✓ Performance monitoring script created")
            print("Add to crontab: */5 * * * * /path/to/performance-monitor.sh")
            
        except Exception as e:
            print(f"✗ Performance monitoring setup failed: {e}")
            return False
        
        return True
    
    def create_production_checklist(self):
        """Create production deployment checklist."""
        checklist = """
# Production Deployment Checklist

## Pre-deployment
- [ ] AWS credentials configured and tested
- [ ] Domain name configured and DNS pointing to server
- [ ] SSL certificates obtained and configured
- [ ] Firewall rules configured
- [ ] System user created with proper permissions
- [ ] Environment variables set in .env.production
- [ ] Database/storage permissions configured
- [ ] Log monitoring configured

## Deployment
- [ ] Application deployed using deploy.py
- [ ] Systemd service created and enabled
- [ ] Nginx configuration deployed and tested
- [ ] Health checks passing
- [ ] SSL certificate working
- [ ] API endpoints accessible via HTTPS

## Post-deployment
- [ ] Monitoring scripts configured in crontab
- [ ] Log rotation configured
- [ ] Backup scripts scheduled
- [ ] Performance monitoring enabled
- [ ] Error alerting configured
- [ ] Documentation updated

## Security
- [ ] Firewall configured and enabled
- [ ] SSH key-based authentication only
- [ ] Application running as non-root user
- [ ] File permissions properly set
- [ ] Secrets properly secured
- [ ] HTTPS enforced
- [ ] Security headers configured

## Monitoring
- [ ] Health check endpoint monitored
- [ ] Application logs monitored
- [ ] System resource usage monitored
- [ ] Error rates monitored
- [ ] Response time monitored
- [ ] Backup verification scheduled

## Testing
- [ ] API endpoints tested
- [ ] Health checks tested
- [ ] SSL certificate tested
- [ ] Load testing performed
- [ ] Backup/restore tested
- [ ] Monitoring alerts tested
"""
        
        with open("production-checklist.md", "w") as f:
            f.write(checklist)
        
        print("✓ Production checklist created: production-checklist.md")
    
    def run_security_audit(self):
        """Run basic security audit."""
        print("Running security audit...")
        
        issues = []
        
        # Check file permissions
        sensitive_files = [".env.production", "config.py"]
        for file_path in sensitive_files:
            if os.path.exists(file_path):
                stat_info = os.stat(file_path)
                if stat_info.st_mode & 0o077:  # Check if group/other have any permissions
                    issues.append(f"File {file_path} has overly permissive permissions")
        
        # Check for default passwords/keys
        env_file = ".env.production"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                content = f.read()
                if "your_" in content.lower() or "change_me" in content.lower():
                    issues.append("Default values found in .env.production")
        
        # Check service user
        try:
            result = subprocess.run(["id", "farmer-budget"], capture_output=True, text=True)
            if result.returncode != 0:
                issues.append("Dedicated service user not configured")
        except:
            issues.append("Cannot verify service user configuration")
        
        # Check firewall
        try:
            result = subprocess.run(["sudo", "ufw", "status"], capture_output=True, text=True)
            if "Status: inactive" in result.stdout:
                issues.append("Firewall is not enabled")
        except:
            issues.append("Cannot verify firewall status")
        
        if issues:
            print("⚠ Security issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("✓ Basic security audit passed")
            return True

def main():
    """Main production setup entry point."""
    parser = argparse.ArgumentParser(description="Production setup for Farmer Budget Optimizer")
    parser.add_argument("--domain", help="Domain name for SSL certificate")
    parser.add_argument("--email", help="Email for SSL certificate")
    parser.add_argument("--ssl", action="store_true", help="Set up SSL certificates")
    parser.add_argument("--firewall", action="store_true", help="Configure firewall")
    parser.add_argument("--user", action="store_true", help="Set up system user")
    parser.add_argument("--monitoring", action="store_true", help="Set up monitoring")
    parser.add_argument("--security-audit", action="store_true", help="Run security audit")
    parser.add_argument("--all", action="store_true", help="Run all setup tasks")
    
    args = parser.parse_args()
    
    setup = ProductionSetup()
    
    if args.all or not any([args.ssl, args.firewall, args.user, args.monitoring, args.security_audit]):
        print("Running full production setup...")
        
        # Generate secrets
        secrets = setup.generate_secrets()
        print("Generated secrets (save these securely):")
        for key, value in secrets.items():
            print(f"  {key}={value}")
        
        # Run all setup tasks
        setup.setup_system_user()
        setup.setup_firewall()
        setup.setup_database_security()
        setup.setup_log_monitoring()
        setup.setup_performance_monitoring()
        setup.create_production_checklist()
        
        if args.domain and args.email:
            setup.setup_ssl_certificates(args.domain, args.email)
        
        setup.run_security_audit()
        
    else:
        if args.ssl:
            if not args.domain or not args.email:
                print("Error: --domain and --email required for SSL setup")
                sys.exit(1)
            setup.setup_ssl_certificates(args.domain, args.email)
        
        if args.firewall:
            setup.setup_firewall()
        
        if args.user:
            setup.setup_system_user()
        
        if args.monitoring:
            setup.setup_log_monitoring()
            setup.setup_performance_monitoring()
        
        if args.security_audit:
            setup.run_security_audit()

if __name__ == "__main__":
    main()