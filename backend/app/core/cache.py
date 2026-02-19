from redis.asyncio import Redis
from app.core.config import settings
import logging

class RedisCache:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(RedisCache, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self.redis = Redis(
            host=settings.redis_host,
            port=int(settings.redis_port),
            db=int(settings.redis_cache_database),
            username=settings.redis_username,
            password=settings.redis_password,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
        self._initialized = True
    
    async def get(self, key: str) -> str | None:
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, expiration: int = 60) -> bool:
        return await self.redis.set(key, value, ex=expiration)
    
    async def check_health(self):
        """Check Redis connection health"""
        try:
            await self.redis.ping()
            logging.getLogger("uvicorn.info").info("Successfully connected to Redis")
            return True
        except Exception as ex:
            logging.getLogger("uvicorn.error").error(f"Failed to connect to Redis: {ex}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if hasattr(self, 'redis') and self.redis:
            await self.redis.aclose()
            self._initialized = False
        