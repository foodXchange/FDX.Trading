"""
Optimized Configuration for FoodXchange
"""
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = Field(
        default="postgresql://postgres:Ud30078123@aws-0-eu-west-3.pooler.supabase.com:5432/postgres?sslmode=require",
        env="DATABASE_URL"
    )
    
    # Supabase Configuration
    supabase_url: Optional[str] = Field(
        default="https://hlugyivdpcwzihvhgjji.supabase.co",
        env="SUPABASE_URL"
    )
    supabase_anon_key: Optional[str] = Field(
        default="",
        env="SUPABASE_ANON_KEY"
    )
    supabase_service_role_key: Optional[str] = Field(
        default="",
        env="SUPABASE_SERVICE_ROLE_KEY"
    )
    
    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-here-change-this-in-production",
        env="SECRET_KEY"
    )
    algorithm: str = Field(
        default="HS256",
        env="ALGORITHM"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Feature Flags
    emails_enabled: bool = Field(
        default=False,
        env="EMAILS_ENABLED"
    )
    azure_storage_enabled: bool = Field(
        default=False,
        env="AZURE_STORAGE_ENABLED"
    )
    
    # AI Configuration
    openai_api_key: Optional[str] = Field(
        default="",
        env="OPENAI_API_KEY"
    )
    
    # Monitoring Configuration
    sentry_dsn: Optional[str] = Field(
        default="https://fdf092923fb6dd5351274f42e8a4dee9@4509734929104896.ingest.de.sentry.io/4509734959775824",
        env="SENTRY_DSN"
    )
    sentry_environment: str = Field(
        default="production",
        env="SENTRY_ENVIRONMENT"
    )
    sentry_traces_sample_rate: float = Field(
        default=0.1,
        env="SENTRY_TRACES_SAMPLE_RATE"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # This fixes the "extra_forbidden" errors

# Global settings instance
settings = Settings()
