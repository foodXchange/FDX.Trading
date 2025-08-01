"""
Application settings configuration
"""
import os
from pathlib import Path
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "FoodXchange"
    debug: bool = Field(False, env="DEBUG")
    environment: str = Field("development", env="ENVIRONMENT")
    
    # Server settings
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(9000, env="PORT")
    workers: int = Field(1, env="WORKERS")
    
    # Security settings
    secret_key: str = Field("your-secret-key-here", env="SECRET_KEY")
    allowed_hosts: list = Field(["*"], env="ALLOWED_HOSTS")
    cors_origins: list = Field(["*"], env="CORS_ORIGINS")
    
    # Database settings
    database_url: str = Field("sqlite:///./foodxchange.db", env="DATABASE_URL")
    
    # Azure OpenAI settings
    azure_openai_api_key: Optional[str] = Field(None, env="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(None, env="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: Optional[str] = Field(None, env="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_openai_api_version: str = Field("2024-02-15-preview", env="AZURE_OPENAI_API_VERSION")
    
    # Redis settings (for rate limiting)
    redis_url: Optional[str] = Field(None, env="REDIS_URL")
    
    # Rate limiting settings
    rate_limit_enabled: bool = Field(True, env="RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(100, env="RATE_LIMIT_REQUESTS")
    rate_limit_period: int = Field(60, env="RATE_LIMIT_PERIOD")  # seconds
    
    # Security headers
    security_headers_enabled: bool = Field(True, env="SECURITY_HEADERS_ENABLED")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Static files
    static_url: str = "/static"
    static_dir: str = "foodxchange/static"
    
    # Templates
    templates_dir: str = "foodxchange/templates"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env file


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Convenience functions
def is_production() -> bool:
    """Check if running in production"""
    settings = get_settings()
    return settings.environment.lower() == "production"


def is_development() -> bool:
    """Check if running in development"""
    settings = get_settings()
    return settings.environment.lower() == "development"


def get_database_url() -> str:
    """Get database URL with proper path handling"""
    settings = get_settings()
    if settings.database_url.startswith("sqlite"):
        # Ensure SQLite path is absolute
        db_path = settings.database_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            base_dir = Path(__file__).resolve().parent.parent.parent
            db_path = base_dir / db_path
            return f"sqlite:///{db_path}"
    return settings.database_url