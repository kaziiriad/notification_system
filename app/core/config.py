from pydantic_settings import BaseSettings
from typing import Optional
from dotenv import load_dotenv
import os
load_dotenv()

class Settings(BaseSettings):

    """Application configuration settings."""
    app_name: str = "Notification Service"
    app_version: str = "1.0.0"
    debug: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/mydatabase")
    # REDIS_URL: Optional[str] = None
    # LOG_LEVEL: str = "INFO"
    # SECRET_KEY: Optional[str] = None
    # JWT_ALGORITHM: str = "HS256"
    # JWT_EXPIRATION_MINUTES: int = 60
    

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
settings = Settings()