from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env and .env.blob
# First load .env, then .env.blob (which will override any duplicate keys)
if os.path.exists('.env'):
    load_dotenv('.env', override=False)
if os.path.exists('.env.blob'):
    load_dotenv('.env.blob', override=True)

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
    
    # Sentry settings (optional)
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    sentry_environment: Optional[str] = os.getenv("SENTRY_ENVIRONMENT", "development")
    sentry_traces_sample_rate: Optional[float] = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    sentry_profiles_sample_rate: Optional[float] = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))
    
    # Supabase settings (optional)
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_anon_key: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    supabase_service_role_key: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "allow"  # This allows extra fields from environment variables

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