import pytest
from unittest.mock import AsyncMock, patch
from app.core.cache import RedisCache

@pytest.fixture
def redis_cache_mock():
    with patch("app.core.cache.Redis") as RedisMock:
        RedisCache._instance = None # reset the singleton instance
        redis_instance = RedisMock.return_value
        # Patch async methods
        redis_instance.get = AsyncMock()
        redis_instance.set = AsyncMock()
        yield RedisCache()

@pytest.mark.asyncio
async def test_get_returns_value(redis_cache_mock):
    redis_cache_mock.redis.get.return_value = "value"
    result = await redis_cache_mock.get("key")
    assert result == "value"
    redis_cache_mock.redis.get.assert_awaited_once_with("key")

@pytest.mark.asyncio
async def test_get_returns_none(redis_cache_mock):
    redis_cache_mock.redis.get.return_value = None
    result = await redis_cache_mock.get("missing_key")
    assert result is None
    redis_cache_mock.redis.get.assert_awaited_once_with("missing_key")

@pytest.mark.asyncio
async def test_set_success(redis_cache_mock):
    redis_cache_mock.redis.set.return_value = True
    result = await redis_cache_mock.set("key", "value")
    assert result is True
    redis_cache_mock.redis.set.assert_awaited_once_with("key", "value", ex=60)

@pytest.mark.asyncio
async def test_set_failure(redis_cache_mock):
    redis_cache_mock.redis.set.return_value = False
    result = await redis_cache_mock.set("key", "value")
    assert result is False
    redis_cache_mock.redis.set.assert_awaited_once_with("key", "value", ex=60)