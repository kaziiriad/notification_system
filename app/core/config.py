from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Get the project root directory (where .env should be)
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

# Load .env file if it exists
if env_file.exists():
    load_dotenv(env_file)
    logger.info("Loaded .env file", env_file=str(env_file))
else:
    logger.warning("No .env file found, using default configuration")

class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application Info
    app_name: str = "Notification Service"
    app_version: str = "1.0.0"
    
    # Environment and Debug
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str
    
    # Celery Configuration
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    CELERY_RESULT_BACKEND: str = "rpc://guest:guest@rabbitmq:5672//"

    # RabbitMQ Configuration
    RABBITMQ_URL: Optional[str] = "amqp://guest:guest@rabbitmq:5672//"
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Notification System API"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production-min-32-chars"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8080"]
    ALLOWED_HOSTS: list = ["localhost", "127.0.0.1"]
    
    # Email Configuration (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # SendGrid Configuration
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: Optional[str] = None

    # SMS Configuration (optional - Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Push Notification Configuration (optional - Firebase)
    FCM_SERVER_KEY: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        # Allow extra fields that might be in environment
        "extra": "allow"
    }

# Create settings instance
settings = Settings()

# Debug output (only in development)
if settings.DEBUG:
    logger.info("Configuration loaded",
        DATABASE_URL=settings.DATABASE_URL,
        DEBUG=settings.DEBUG,
        ENVIRONMENT=settings.ENVIRONMENT)

    # Determine database type
    if settings.DATABASE_URL:
        if "sqlite" in settings.DATABASE_URL.lower():
            logger.info("Database: SQLite (Local Development)")
        elif "postgresql" in settings.DATABASE_URL.lower():
            logger.info("Database: PostgreSQL")
        else:
            logger.info("Database: Unknown type")