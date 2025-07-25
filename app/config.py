from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os

class Settings(BaseSettings):
    # Required settings with defaults for development
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./foodxchange.db")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Optional settings with defaults
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    use_https: bool = os.getenv("USE_HTTPS", "False").lower() == "true"
    
    # Azure settings (optional)
    azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_storage_connection_string: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    azure_email_connection_string: Optional[str] = os.getenv("AZURE_EMAIL_CONNECTION_STRING")
    
    # Email settings (optional)
    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    # Redis (optional)
    redis_url: Optional[str] = os.getenv("REDIS_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings():
    try:
        return Settings()
    except Exception as e:
        # Return settings with defaults if .env file is missing
        import logging
        logging.warning(f"Using default settings: {e}")
        return Settings(
            _env_file=None,
            database_url=os.getenv("DATABASE_URL", "sqlite:///./foodxchange.db"),
            secret_key=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
        ) 