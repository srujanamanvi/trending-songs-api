import pytest
from httpx import AsyncClient
from app.main import app
from app.services.database import db_service
from app.cache.redis_cache import redis_cache
import asyncio


@pytest.fixture(scope="session")
def event_loop():
    """Ensure a single event loop is used for all tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)  # Ensure this loop is set globally
    yield loop
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()


@pytest.fixture(scope="function")
async def test_client():
    """Provides an isolated test client for each test."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function", autouse=True)
async def clear_redis_cache():
    """Ensures Redis cache is cleared before each test."""
    await redis_cache.clear()


@pytest.fixture(scope="function", autouse=True)
async def reset_database():
    """Ensures database is reset before each test."""
    await db_service.connect()
    await db_service.songs_collection.delete_many({})


@pytest.mark.asyncio
async def test_health_check(test_client):
    """Test health check endpoint"""
    response = await test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_get_trending_songs(test_client):
    """Test retrieving trending songs endpoint"""
    response = await test_client.get("/api/v1/trending/songs")
    assert response.status_code == 200

    songs = response.json()
    assert isinstance(songs, list)
    assert len(songs) <= 100

    response = await test_client.get("/api/v1/trending/songs?genre=Pop")
    assert response.status_code == 200

    genre_songs = response.json()
    assert all(song['genre'] == 'Pop' for song in genre_songs)


@pytest.mark.asyncio
async def test_trending_update(test_client):
    """Test trending data update endpoint"""
    response = await test_client.post("/api/v1/trending/update")
    assert response.status_code == 200

    result = response.json()
    assert result["content"]["message"] == "Trending data updated successfully"


@pytest.mark.asyncio
async def test_endpoint_query_parameters(test_client):
    """Test various query parameter combinations"""
    response = await test_client.get("/api/v1/trending/songs?limit=50")
    assert response.status_code == 200
    assert len(response.json()) <= 50

    response = await test_client.get("/api/v1/trending/songs?limit=600")
    assert response.status_code == 422  # Validation error
