from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime
from enum import Enum
import uuid


class Genre(str, Enum):
    POP = "Pop"
    ROCK = "Rock"
    HIP_HOP = "Hip Hop"
    ELECTRONIC = "Electronic"
    CLASSICAL = "Classical"
    JAZZ = "Jazz"


class Song(BaseModel):
    song_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    artist: str
    album: str
    genre: Genre
    play_count: int = 0
    user_rating: float = Field(default=0.0, ge=0.0, le=5.0)
    social_media_shares: int = 0
    geographic_popularity: Dict[str, float] = {}
    last_played_timestamp: datetime = Field(default_factory=datetime.utcnow)
    trending_score: float = 0.0
    is_active: bool = True

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "title": "Uptown Funk",
                "artist": "Mark Ronson ft. Bruno Mars",
                "album": "Uptown Special",
                "genre": "Pop",
                "play_count": 1000000,
                "user_rating": 4.5,
                "social_media_shares": 50000
            }
        }
