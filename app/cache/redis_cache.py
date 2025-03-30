import json
import redis.asyncio as redis
from typing import Optional, Any
from app.settings.config import settings


class RedisCache:
    """
    Async Redis Caching Service with JSON serialization
    """

    def __init__(self):
        self._redis = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

    async def connect(self):
        """Establish Redis connection"""
        return self._redis

    async def close(self):
        """Close Redis connection"""
        await self._redis.close()

    async def set(
            self,
            key: str,
            value: Any,
            expiration: Optional[int] = None
    ) -> None:
        """
        Cache a value with optional expiration

        Args:
            key (str): Cache key
            value (Any): Value to cache (will be JSON serialized)
            expiration (int, optional): Expiration in seconds. Defaults to settings value.
        """
        # Use default expiration if not provided
        if expiration is None:
            expiration = settings.CACHE_EXPIRATION

        # Serialize complex objects to JSON
        serialized_value = json.dumps(value)

        await self._redis.setex(key, expiration, serialized_value)

    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value

        Args:
            key (str): Cache key to retrieve

        Returns:
            Optional deserialized value
        """
        cached_value = await self._redis.get(key)

        if cached_value:
            try:
                return json.loads(cached_value)
            except json.JSONDecodeError:
                return cached_value

        return None

    async def delete(self, key: str) -> None:
        """
        Delete a specific cache key

        Args:
            key (str): Cache key to delete
        """
        await self._redis.delete(key)

    async def clear(self) -> None:
        """
        Clear entire Redis cache
        """
        await self._redis.flushdb()


# Create a singleton Redis cache instance
redis_cache = RedisCache()
