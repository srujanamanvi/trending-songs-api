from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING, UpdateOne
from typing import List, Optional
import logging

from app.settings.config import settings
from app.models.song import Song, Genre
from fastapi import FastAPI

app = FastAPI()
logger = logging.getLogger(__name__)


class DatabaseService:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
            cls._instance.songs_collection = None
        return cls._instance

    async def connect(self):
        """ Establish a connection to the MongoDB database (only once). """
        if self.client is None:  # Prevent unnecessary reconnections
            try:
                self.client = AsyncIOMotorClient(settings.MONGODB_URL)
                self.db = self.client[settings.MONGODB_DB]
                self.songs_collection = self.db.get_collection("songs")

                # Verify connection by pinging the database
                await self.db.command('ping')
                logger.info(f"Connected to MongoDB: {settings.MONGODB_DB}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise

    async def close(self):
        """ Close the MongoDB connection. """
        if self.client:
            self.client.close()
            self.client = None  # Reset the connection
            logger.info("MongoDB connection closed")

    async def insert_songs(self, songs: List[Song]):
        """ Insert multiple songs into the database. """
        if self.songs_collection is None:
            raise RuntimeError("Database not connected. Call connect() first.")

        song_documents = [song.model_dump() for song in songs]
        await self.songs_collection.insert_many(song_documents)

    async def get_top_trending_songs(self, limit: int = 100, offset: int = 0, genre: Optional[Genre] = None) -> List[Song]:
        """
        Retrieve top trending songs from database with optimized query performance.
        """
        # Build query with genre filter if provided
        query = {"genre": genre} if genre else {}

        # Execute optimized query with pagination
        cursor = self.songs_collection.find(
            query
        ).sort(
            "trending_score", DESCENDING
        ).skip(offset).limit(limit)

        # Convert cursor to list of Song objects
        songs = await cursor.to_list(length=limit)
        return [Song(**song) for song in songs]

    async def update_simulation_data(self, songs: List[Song]):
        """ Bulk update simulation data for songs. """
        if self.songs_collection is None:
            raise RuntimeError("Database not connected. Call connect() first.")

        bulk_operations = [
            UpdateOne({"song_id": song.song_id}, {"$set": {
                                                           "last_played_timestamp": song.last_played_timestamp,
                                                           "play_count": song.play_count,
                                                           "social_media_shares": song.play_count
                                                    }
                                                  })
            for song in songs
        ]

        if bulk_operations:
            await self.songs_collection.bulk_write(bulk_operations)


# Singleton instance
db_service = DatabaseService()


# Dependency function for FastAPI
async def get_db_service():
    """ Ensure a single DB connection is used in all FastAPI routes. """
    await db_service.connect()
    return db_service


async def create_indexes(db):
    await db.songs_collection.create_index(
        [("genre", 1), ("trending_score", -1)],
        name="genre_trending_index"
    )

