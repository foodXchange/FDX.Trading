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
    # Required settings with validation
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./foodxchange.db")
    secret_key: str = os.getenv("SECRET_KEY")
    
    # Optional settings with defaults
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"  # Default to False for security
    use_https: bool = os.getenv("USE_HTTPS", "False").lower() == "true"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_secret_key()
        self._validate_production_settings()
    
    def _validate_secret_key(self):
        """Validate SECRET_KEY meets security requirements"""
        if not self.secret_key:
            if self.environment == "production":
                raise ValueError("SECRET_KEY is required in production environment")
            else:
                # Generate a development key if not provided
                import secrets
                self.secret_key = secrets.token_urlsafe(32)
                print(f"WARNING: Using generated SECRET_KEY for development: {self.secret_key}")
        
        if len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
    
    def _validate_production_settings(self):
        """Validate settings for production environment"""
        if self.environment == "production":
            if self.debug:
                raise ValueError("DEBUG must be False in production")
            if not self.use_https:
                print("WARNING: HTTPS is recommended for production")
            if "sqlite" in self.database_url.lower():
                print("WARNING: SQLite is not recommended for production")
    
    # Azure OpenAI settings (optional)
    azure_openai_api_key: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: Optional[str] = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # Azure Computer Vision settings (optional)
    azure_vision_endpoint: Optional[str] = os.getenv("AZURE_VISION_ENDPOINT")
    azure_vision_key: Optional[str] = os.getenv("AZURE_VISION_KEY")
    
    # Azure Cognitive Search settings (optional)
    azure_search_endpoint: Optional[str] = os.getenv("AZURE_SEARCH_ENDPOINT")
    azure_search_key: Optional[str] = os.getenv("AZURE_SEARCH_KEY")
    azure_search_index: Optional[str] = os.getenv("AZURE_SEARCH_INDEX", "products")
    
    # Azure Storage settings (optional)
    azure_storage_connection_string: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    azure_storage_container: Optional[str] = os.getenv("AZURE_STORAGE_CONTAINER", "product-images")
    
    # Azure Communication Services (optional)
    azure_email_connection_string: Optional[str] = os.getenv("AZURE_EMAIL_CONNECTION_STRING")
    
    # Email settings (optional)
    smtp_host: Optional[str] = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    
    # Redis (optional - not required for development)
    redis_url: Optional[str] = os.getenv("REDIS_URL", "redis://localhost:6379" if os.getenv("ENVIRONMENT") == "production" else None)
    
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
        settings = Settings()
        # Validate required settings
        if not settings.secret_key:
            raise ValueError("SECRET_KEY environment variable is required")
        return settings
    except Exception as e:
        # Log error and re-raise for critical configuration issues
        import logging
        logging.error(f"Critical configuration error: {e}")
        raise

settings = get_settings() 