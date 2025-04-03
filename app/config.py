from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hora en segundos
    TEMP_DOMAINS_URL: str = "https://example.com/temp_domains.json"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()