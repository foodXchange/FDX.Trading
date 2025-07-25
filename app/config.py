from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    openai_api_key: str
    azure_storage_connection_string: str
    azure_email_connection_string: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    redis_url: str
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings() 