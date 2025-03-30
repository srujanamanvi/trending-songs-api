import random
import uuid
from datetime import datetime, timedelta
from typing import List

from app.models.song import Song, Genre
from fastapi import Query


class DataGenerator:

    @staticmethod
    def generate_songs(num_songs: int = Query(default=100)) -> List[Song]:
        """
        Generate a large number of simulated songs with realistic data
        """
        songs = []
        genres = list(Genre)
        artists = [
            "Taylor Swift", "Drake", "Ed Sheeran", "Ariana Grande",
            "The Weeknd", "Billie Eilish", "Post Malone", "Bruno Mars"
        ]

        for _ in range(num_songs):
            song = Song(
                song_id=str(uuid.uuid4()),
                title=f"Song {random.randint(1, 10000)}",
                artist=random.choice(artists),
                album=f"Album {random.randint(1, 500)}",
                genre=random.choice(genres),
                play_count=random.randint(1000, 1000000),
                user_rating=round(random.uniform(1.0, 5.0), 1),
                social_media_shares=random.randint(100, 100000),
                geographic_popularity={
                    "IN": random.randint(1000, 100000),
                    "US": random.randint(1000, 100000),
                    "UK": random.randint(1000, 100000),
                    "Others": random.randint(1000, 100000)
                },
                last_played_timestamp=datetime.utcnow() - timedelta(
                    days=random.randint(0, 30)  # Up to 30 days ago
                )
            )
            songs.append(song)

        return songs

    @staticmethod
    def simulate_streaming_data(songs: List[Song]) -> List[Song]:
        """
        Simulate ongoing streaming data updates
        """
        for song in songs:
            # Randomly update play counts and timestamps
            song.play_count += random.randint(10000, 50000)
            song.last_played_timestamp = song.last_played_timestamp - timedelta(
                days=random.randint(1, 5)
            )
            song.social_media_shares += random.randint(10000, 50000)

        return songs
