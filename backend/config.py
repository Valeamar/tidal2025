"""
Configuration management for the Farmer Budget Optimizer.
Handles environment-specific settings and validation.
"""

import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Application Settings
    app_name: str = Field(default="farmer-budget-optimizer", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    reload: bool = Field(default=False, env="RELOAD")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="standard", env="LOG_FORMAT")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    log_json: bool = Field(default=False, env="LOG_JSON")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    cors_credentials: bool = Field(default=True, env="CORS_CREDENTIALS")
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_endpoint_url: Optional[str] = Field(default=None, env="AWS_ENDPOINT_URL")
    
    # AWS Service Configuration
    aws_forecast_role_arn: Optional[str] = Field(default=None, env="AWS_FORECAST_ROLE_ARN")
    aws_quicksight_account_id: Optional[str] = Field(default=None, env="AWS_QUICKSIGHT_ACCOUNT_ID")
    aws_quicksight_namespace: str = Field(default="default", env="AWS_QUICKSIGHT_NAMESPACE")
    aws_s3_bucket: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Database/Storage Configuration
    data_dir: str = Field(default="./data", env="DATA_DIR")
    cache_dir: str = Field(default="./cache", env="CACHE_DIR")
    backup_dir: str = Field(default="./backups", env="BACKUP_DIR")
    
    # External API Configuration
    market_data_api_key: Optional[str] = Field(default=None, env="MARKET_DATA_API_KEY")
    market_data_base_url: Optional[str] = Field(default=None, env="MARKET_DATA_BASE_URL")
    use_mock_data: bool = Field(default=True, env="USE_MOCK_DATA")
    
    # Performance Configuration
    request_timeout: int = Field(default=60, env="REQUEST_TIMEOUT")
    max_concurrent_requests: int = Field(default=10, env="MAX_CONCURRENT_REQUESTS")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    
    # Security Configuration
    api_key_header: str = Field(default="X-API-Key", env="API_KEY_HEADER")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # Health Check Configuration
    health_check_timeout: int = Field(default=30, env="HEALTH_CHECK_TIMEOUT")
    service_check_interval: int = Field(default=300, env="SERVICE_CHECK_INTERVAL")
    
    # Monitoring Configuration
    enable_metrics: bool = Field(default=False, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        """Validate environment."""
        valid_environments = ["development", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    def create_directories(self):
        """Create necessary directories."""
        directories = [self.data_dir, self.cache_dir, self.backup_dir]
        
        # Add log directory if log_file is specified
        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir:
                directories.append(log_dir)
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    def get_aws_config(self) -> dict:
        """Get AWS configuration dictionary."""
        config = {
            "region_name": self.aws_region
        }
        
        if self.aws_access_key_id and self.aws_secret_access_key:
            config.update({
                "aws_access_key_id": self.aws_access_key_id,
                "aws_secret_access_key": self.aws_secret_access_key
            })
        
        if self.aws_endpoint_url:
            config["endpoint_url"] = self.aws_endpoint_url
        
        return config
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    # Determine which env file to load based on ENVIRONMENT variable
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    env_files = {
        "development": ".env.development",
        "staging": ".env.staging", 
        "production": ".env.production"
    }
    
    env_file = env_files.get(environment, ".env")
    
    # Check if environment-specific file exists, fallback to .env
    if not os.path.exists(env_file):
        env_file = ".env"
    
    settings = Settings(_env_file=env_file)
    
    # Create necessary directories
    settings.create_directories()
    
    return settings

# Global settings instance
settings = get_settings()