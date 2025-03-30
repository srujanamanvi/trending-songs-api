import pytest
from app.cache.redis_cache import redis_cache
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def clear_redis_cache():
    """Ensures Redis cache is cleared before each test."""
    await redis_cache.clear()


@pytest.mark.asyncio
async def test_redis_cache_basic_operations():
    """Test basic Redis cache operations"""
    # Test setting and getting a simple value
    key = "test_key"
    value = {"name": "Test Song", "plays": 1000}

    # Set value
    await redis_cache.set(key, value)

    # Get value
    retrieved_value = await redis_cache.get(key)

    # Assertions
    assert retrieved_value == value, "Retrieved value should match original"


@pytest.mark.asyncio
async def test_redis_cache_expiration():
    """Test cache expiration"""
    # Set value with short expiration
    key = "expiring_key"
    value = {"temporary": "data"}

    # Set with very short expiration (1 second)
    await redis_cache.set(key, value, expiration=1)

    # Immediately retrieve
    first_retrieve = await redis_cache.get(key)
    assert first_retrieve == value, "Should retrieve value immediately"

    # Wait for expiration (pytest-asyncio handles this)
    import asyncio
    await asyncio.sleep(2)

    # Retrieve after expiration
    expired_retrieve = await redis_cache.get(key)
    assert expired_retrieve is None, "Should not retrieve expired key"

