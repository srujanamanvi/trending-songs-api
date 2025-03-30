import asyncio

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import List, Optional

from app.models.song import Song, Genre
from app.services.database import get_db_service, DatabaseService
from app.services.trending_algorithm import TrendingAlgorithm
from app.services.data_generator import DataGenerator
from app.cache.redis_cache import redis_cache
from pymongo import UpdateOne
import logging
import json

from app.constants import EXPIRY_TIME
from app.tasks import refresh_trending_cache

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/trending/songs", response_model=List[Song], tags=["Trending Songs"])
async def get_top_trending_songs(
        limit: int = Query(default=100, le=500),
        offset: int = Query(default=0, ge=0),
        genre: Optional[Genre] = None,
        db_service: DatabaseService = Depends(get_db_service)
):
    """
    Retrieve top trending songs with Redis caching
    """
    # Create a unique cache key based on parameters
    cache_key = f"trending_songs:{genre or 'all'}:{limit}:{offset}"

    # Try to get cached result with error handling
    try:
        cached_result = await redis_cache.get(cache_key)
        if cached_result:
            cached_result = json.loads(cached_result)  # Convert back from JSON
            return [Song(**song) for song in cached_result]
    except Exception as e:
        # Redis error, log and continue to database query
        logger.warning(f"Redis error when fetching {cache_key}: {str(e)}")

    try:
        # Fetch songs from database
        songs = await db_service.get_top_trending_songs(limit, offset, genre)

        # Only cache if we have results
        if songs:
            try:
                serialized_songs = json.dumps(
                    [song.model_dump() for song in songs],
                    default=str
                )
                # Cache the result with expiry
                await redis_cache.set(
                    cache_key,
                    serialized_songs,
                    expiration=EXPIRY_TIME
                )
            except Exception as e:
                # Log caching error but don't fail the request
                logger.error(f"Failed to cache results for {cache_key}: {str(e)}")

        return songs

    except Exception as e:
        logger.error(f"Database error in get_top_trending_songs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trending songs")


@router.post("/trending/update", response_model=dict, tags=["Trending Songs"])
async def update_trending_data(
    db_service: DatabaseService = Depends(get_db_service)
):
    """
    Update trending data and invalidate cache

    NOTE: This doesn't have to be an endpoint as we have a cron setup to run every 60 mins.
    Creating it so that validating results will be easier from /docs for assignment validation POV
    """
    logger.info("Starting trending score update process")

    try:
        # Update trending scores
        # Fetch only required fields for all songs
        songs_cursor = db_service.songs_collection.find({}, {
            "song_id": 1, "last_played_timestamp": 1, "play_count": 1,
            "user_rating": 1, "social_media_shares": 1, "geographic_popularity": 1
        })

        bulk_operations = []
        batch_size = 1000  # Process in batches

        # Iterate through cursor asynchronously
        async for song in songs_cursor:
            trending_score = TrendingAlgorithm.calculate_trending_score(song)  # Compute score
            bulk_operations.append(
                UpdateOne({"song_id": song["song_id"]}, {"$set": {"trending_score": trending_score}})
            )

            # Execute batch update when batch_size is reached
            if len(bulk_operations) >= batch_size:
                await db_service.songs_collection.bulk_write(bulk_operations)
                bulk_operations = []  # Reset for next batch

        # Process any remaining operations
        if bulk_operations:
            await db_service.songs_collection.bulk_write(bulk_operations)

        logger.info("Trending score update completed")

        # Refresh cache with the pre-existing refresh function
        background_task = asyncio.create_task(refresh_trending_cache(db_service, redis_cache))

        logger.info(f"Cache refresh task started in background with task {background_task}")

        return {
            "status_code": 200,
            "content": {
                "status": "success",
                "message": "Trending data updated successfully",
                "details": "Scores are being updated and cache will be refreshed automatically"
            }
        }

    except Exception as e:
        logger.error(f"Error in trending update process: {str(e)}")


@router.get("/simulation/generate_data", response_model=dict, tags=["Simulation"])
async def generate_seed_data(num: int, db_service: DatabaseService = Depends(get_db_service)):
    """
    Retrieve top trending songs with Redis caching
    """
    try:
        songs = DataGenerator.generate_songs(num)
        # Fetch songs from database
        await db_service.insert_songs(songs)

        await update_trending_data(db_service)

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/simulation/simulate_streaming_data", response_model=dict, tags=["Simulation"])
async def simulate_streaming_data(db_service: DatabaseService = Depends(get_db_service)):
    """
    This method is changing data for first 5 records only for the purpose of simulation.
    """
    try:
        songs = await db_service.get_top_trending_songs(100)

        songs = DataGenerator.simulate_streaming_data(songs[:5]) # Fetching only first 5 top songs to manipulate and see changes if any

        await db_service.update_simulation_data(songs)

        await update_trending_data(db_service)

        return {"success": True}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
