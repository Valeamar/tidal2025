# Farmer Budget Optimizer - Deployment Guide

This guide covers deployment of the Farmer Budget Optimizer API in different environments.

## Quick Start

### Development Environment

1. **Clone and setup:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Validate environment:**
   ```bash
   python validate-environment.py --environment development
   ```

3. **Configure environment:**
   ```bash
   cp .env.development .env
   # Edit .env with your settings
   ```

4. **Start the application:**
   ```bash
   # Using startup script
   ./start.sh  # On Windows: start.bat
   
   # Or directly
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   
   # Or using deployment script
   python deploy.py --environment development --start
   ```

5. **Verify deployment:**
   ```bash
   curl http://127.0.0.1:8000/api/health
   curl http://127.0.0.1:8000/api/ready
   ```

### Staging Environment

1. **Validate environment:**
   ```bash
   python validate-environment.py --environment staging
   ```

2. **Automated deployment:**
   ```bash
   python deploy.py --environment staging
   ```

3. **Start service:**
   ```bash
   sudo systemctl start farmer-budget-optimizer-staging
   sudo systemctl status farmer-budget-optimizer-staging
   ```

### Production Environment

1. **Pre-deployment validation:**
   ```bash
   python validate-environment.py --environment production
   ```

2. **Production setup (first time only):**
   ```bash
   # Run production setup script
   python production-setup.py --all --domain your-domain.com --email your-email@domain.com
   
   # Or run individual components
   python production-setup.py --user --firewall --monitoring
   python production-setup.py --ssl --domain your-domain.com --email your-email@domain.com
   ```

3. **Automated deployment:**
   ```bash
   python deploy.py --environment production
   ```

4. **Manual deployment (if needed):**
   ```bash
   # Install dependencies
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.production .env
   # Edit .env with your production settings
   
   # Create directories
   mkdir -p logs data cache backups
   
   # Start with systemd (recommended)
   sudo systemctl start farmer-budget-optimizer-production
   ```

5. **Post-deployment verification:**
   ```bash
   # Check service status
   sudo systemctl status farmer-budget-optimizer-production
   
   # Check health endpoints
   curl https://your-domain.com/api/health
   curl https://your-domain.com/api/ready
   curl https://your-domain.com/api/live
   
   # Run security audit
   python production-setup.py --security-audit
   ```

## Environment Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `development` | No |
| `HOST` | Server host | `127.0.0.1` | No |
| `PORT` | Server port | `8000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `AWS_REGION` | AWS region | `us-east-1` | No |
| `AWS_ACCESS_KEY_ID` | AWS access key | - | Yes (prod) |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | - | Yes (prod) |

### Environment Files

- `.env.development` - Development settings
- `.env.staging` - Staging settings  
- `.env.production` - Production settings

Copy the appropriate file to `.env` or set `ENVIRONMENT` variable.

## Deployment Methods

### 1. Direct Deployment

**Development:**
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Using Deployment Script

```bash
# Deploy to development
python deploy.py --environment development

# Deploy to production
python deploy.py --environment production

# Deploy and start
python deploy.py --environment development --start

# Health check only
python deploy.py --health-check
```

### 3. Docker Deployment

```bash
# Build and run with Docker Compose
cd docker
docker-compose up -d

# Or build manually
docker build -f docker/Dockerfile -t farmer-budget-optimizer .
docker run -p 8000:8000 farmer-budget-optimizer
```

### 4. Systemd Service (Linux Production)

The deployment script creates a systemd service file:

```bash
# Enable and start service
sudo systemctl enable farmer-budget-optimizer
sudo systemctl start farmer-budget-optimizer

# Check status
sudo systemctl status farmer-budget-optimizer

# View logs
sudo journalctl -u farmer-budget-optimizer -f
```

## AWS Configuration

### Required AWS Services

- **Amazon Forecast** - Price prediction
- **AWS QuickSight** - Data visualization and insights
- **AWS Comprehend** - Sentiment analysis
- **Amazon S3** - Data storage

### IAM Permissions

Create an IAM role/user with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "forecast:*",
                "quicksight:*",
                "comprehend:*",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": "*"
        }
    ]
}
```

### AWS Configuration Options

1. **Environment Variables:**
   ```bash
   export AWS_ACCESS_KEY_ID=your_key
   export AWS_SECRET_ACCESS_KEY=your_secret
   export AWS_REGION=us-east-1
   ```

2. **AWS Credentials File:**
   ```bash
   aws configure
   ```

3. **IAM Roles (EC2):**
   Attach IAM role to EC2 instance

## Monitoring and Logging

### Log Configuration

Logs are written to:
- Console (stdout)
- File: `logs/app.log` (if configured)

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Health Checks

- **Endpoint:** `GET /api/health`
- **Response:** JSON with service status
- **Monitoring:** Checks AWS service availability

### Metrics (Optional)

Enable Prometheus metrics:
```bash
# In environment file
ENABLE_METRICS=true
METRICS_PORT=9090
```

Access metrics at: `http://localhost:9090/metrics`

## Security Considerations

### Production Security

1. **HTTPS:** Use SSL/TLS certificates
2. **Firewall:** Restrict access to necessary ports
3. **API Keys:** Secure AWS credentials
4. **CORS:** Configure allowed origins
5. **Rate Limiting:** Nginx configuration included

### Environment Security

- Never commit `.env` files with secrets
- Use environment-specific configurations
- Rotate AWS credentials regularly
- Monitor access logs

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port
   lsof -i :8000
   # Kill process
   kill -9 <PID>
   ```

2. **AWS credentials not found:**
   ```bash
   # Check AWS configuration
   aws sts get-caller-identity
   ```

3. **Module not found:**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Permission denied:**
   ```bash
   # Make scripts executable
   chmod +x start.sh deploy.py
   ```

### Log Analysis

```bash
# View application logs
tail -f logs/app.log

# View systemd logs
sudo journalctl -u farmer-budget-optimizer -f

# View nginx logs (if using)
sudo tail -f /var/log/nginx/farmer-budget-optimizer.access.log
```

### Health Check

```bash
# Check API health
curl http://localhost:8000/api/health

# Check with verbose output
curl -v http://localhost:8000/api/health
```

## Performance Tuning

### Production Optimization

1. **Workers:** Set based on CPU cores
   ```bash
   WORKERS=$((2 * $(nproc) + 1))
   ```

2. **Memory:** Monitor memory usage
   ```bash
   # Check memory usage
   ps aux | grep uvicorn
   ```

3. **Database:** Optimize file I/O
   ```bash
   # Use SSD storage for data directory
   # Regular cleanup of cache files
   ```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 http://localhost:8000/api/health
```

## Backup and Recovery

### Data Backup

```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/ cache/ logs/

# Automated backup script
0 2 * * * /path/to/backup-script.sh
```

### Recovery

```bash
# Restore from backup
tar -xzf backup-20231201.tar.gz
```

## Scaling

### Horizontal Scaling

1. **Load Balancer:** Use nginx or AWS ALB
2. **Multiple Instances:** Run on different ports/servers
3. **Shared Storage:** Use network storage for data

### Vertical Scaling

1. **Increase Workers:** More CPU cores
2. **Memory:** Increase available RAM
3. **Storage:** Faster disk I/O

## Support

For deployment issues:

1. Check logs: `logs/app.log`
2. Verify configuration: `python -c "from config import get_settings; print(get_settings())"`
3. Test health endpoint: `curl http://localhost:8000/api/health`
4. Review this deployment guide
5. Check AWS service status if using AWS services