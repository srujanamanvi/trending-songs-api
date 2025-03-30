import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import json

from app.models.song import Genre
from app.services.database import DatabaseService
from app.constants import EXPIRY_TIME

# Configure logging
logger = logging.getLogger(__name__)


class TrendingScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        """
        Start the scheduler with a 60-minute interval job
        """
        self.scheduler.add_job(
            self._run_update,
            trigger=IntervalTrigger(minutes=60),
            id='trending_update_job',
            max_instances=1,  # Prevent concurrent executions
            replace_existing=True
        )

        self.scheduler.start()
        logger.info("Trending data update scheduler started")

    @staticmethod
    async def _run_update():
        """
        Wrapper method to run update_trending_data with error handling
        """
        from app.api.endpoints import update_trending_data

        try:
            logger.info("Starting scheduled trending data update")
            await update_trending_data()
            logger.info("Trending data update completed successfully")
        except Exception as e:
            logger.error(f"Error in scheduled trending data update: {e}")


async def refresh_trending_cache(db_service: DatabaseService, redis_cache):
    """
    Background task to pre-compute and cache trending songs data.
    Runs independently after trending updates.
    """

    logger.info("Starting background refresh of trending songs cache")
    genres = [None] + list(Genre)  # Include 'all' and each genre
    limits = [100]  # Common limit values
    offsets = [0]  # First page is most commonly accessed

    for genre in genres:
        for limit in limits:
            for offset in offsets:
                try:
                    cache_key = f"trending_songs:{genre or 'all'}:{limit}:{offset}"

                    # Fetch fresh data
                    songs = await db_service.get_top_trending_songs(limit, offset, genre)

                    if songs:
                        serialized = json.dumps([song.model_dump() for song in songs], default=str)
                        # Set with longer expiry for background-refreshed data
                        await redis_cache.set(cache_key, serialized, expiration=EXPIRY_TIME)

                    logger.debug(f"Refreshed cache for {cache_key}")

                except Exception as e:
                    logger.error(
                        f"Failed to refresh cache for {genre or 'all'}, limit={limit}, offset={offset}: {str(e)}")

                # Small delay to prevent overwhelming the database
                await asyncio.sleep(0.1)

    logger.info("Completed background refresh of trending songs cache")


# Create scheduler instance
trending_scheduler = TrendingScheduler()
