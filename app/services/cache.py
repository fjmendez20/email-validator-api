from redis.asyncio import Redis
import json
from app.config import settings

class CacheManager:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> dict:
        cached = await self.redis.get(f"email:{key}")
        return json.loads(cached) if cached else None

    async def set(self, key: str, value: dict) -> None:
        await self.redis.set(f"email:{key}", json.dumps(value), ex=3600)

    async def ping(self) -> bool:
        try:
            return await self.redis.ping()
        except:
            return False

    async def close(self):
        await self.redis.close()