from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    REDIS_URL: str = "redis://default:nyhT41MFkNX5ExruSlP6DhyAkBCgkoIC@redis-15261.c93.us-east-1-3.ec2.redns.redis-cloud.com:15261"
    CACHE_TTL: int = 3600  # 1 hora en segundos
    TEMP_DOMAINS_URL: str = "https://example.com/temp_domains.json"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()