from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os
from pathlib import Path

# Get the project root directory (where .env should be)
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

# Load .env file if it exists
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded .env file from: {env_file}")
else:
    print(f"⚠️  No .env file found at: {env_file}")
    print("Using default configuration values")

class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Application Info
    app_name: str = "Notification Service"
    app_version: str = "1.0.0"
    
    # Environment and Debug
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: Optional[str] = None
    
    # PostgreSQL specific settings
    POSTGRES_DB: str = "notification_system"
    POSTGRES_USER: str = "myuser"
    POSTGRES_PASSWORD: str = "mypassword"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    
    # Redis Configuration
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
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
    
    # SMS Configuration (optional - Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # Push Notification Configuration (optional - Firebase)
    FCM_SERVER_KEY: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # If DATABASE_URL is not set, construct it from PostgreSQL components
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow extra fields that might be in environment
        extra = "allow"

# Create settings instance
settings = Settings()

# Debug output (only in development)
if settings.DEBUG:
    print(f"🔧 Configuration loaded:")
    print(f"   DATABASE_URL: {settings.DATABASE_URL}")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   ENVIRONMENT: {settings.ENVIRONMENT}")
    print(f"   POSTGRES_HOST: {settings.POSTGRES_HOST}")
    print(f"   POSTGRES_USER: {settings.POSTGRES_USER}")
    print(f"   POSTGRES_DB: {settings.POSTGRES_DB}")
    
    # Determine database type
    if settings.DATABASE_URL:
        if "sqlite" in settings.DATABASE_URL.lower():
            print(f"   Database: SQLite (Local Development)")
        elif "postgresql" in settings.DATABASE_URL.lower():
            print(f"   Database: PostgreSQL")
        else:
            print(f"   Database: Unknown type")