import math
from datetime import datetime

from typing import List, Optional, Dict

from app.models.song import Song, Genre


class TrendingAlgorithm:

    # Adjustable weight factors
    WEIGHTS: Dict[str, float] = {
        'recency': 0.4,
        'play_count': 0.2,
        'user_rating': 0.15,
        'social_media_shares': 0.15,
        'geographic_popularity': 0.1
    }

    @staticmethod
    def calculate_trending_score(song: Song, current_time: datetime = None) -> float:
        """
        Calculate a trending score of the song.

        Args:
            song (Song): The song to calculate the trending score for
            current_time (datetime, optional): Reference time for calculations
            weights (dict, optional): Customizable weights for different factors

        Returns:
            float: Calculated trending score
        """
        weights = TrendingAlgorithm.WEIGHTS

        current_time = current_time or datetime.utcnow()

        # Recency Score
        time_since_play = (current_time - song["last_played_timestamp"]).total_seconds() / 3600  # hours

        # Half-life decay calculation with exponential amplification
        recency_score = (2 ** (-time_since_play / 24)) * 100 * weights['recency']

        # Play Count Score (logarithmic scaling with reduced impact)
        play_count_score = math.log(song["play_count"] + 1) * weights['play_count'] * 100

        # User Rating Score (normalized to 100)
        rating_score = song["user_rating"] * weights['user_rating'] * 100

        # Social Media Shares Score (logarithmic with cap)
        social_score = math.log(song["social_media_shares"] + 1) * weights['social_media_shares'] * 100

        max_geo_value = max(song["geographic_popularity"].values())
        geo_score = sum(
            (popularity / max_geo_value) * weights['geographic_popularity'] * 100
            for popularity in song["geographic_popularity"].values()
        ) / max(len(song["geographic_popularity"]), 1)

        # Combine scores with normalization
        trending_score = (
                recency_score +
                play_count_score +
                rating_score +
                social_score +
                geo_score
        )
        return trending_score

    @staticmethod
    def get_top_trending_songs(
            songs: List[Song],
            limit: int = 100,
            genre: Optional[Genre] = None
    ) -> List[Song]:
        """
        Retrieve top trending songs, optionally filtered by genre
        """
        # Filter by genre if specified
        filtered_songs = [
            song for song in songs
            if genre is None or song.genre == genre
        ]

        # Calculate trending scores
        for song in filtered_songs:
            song.trending_score = TrendingAlgorithm.calculate_trending_score(song)

        # Sort and return top songs
        return sorted(
            filtered_songs,
            key=lambda x: x.trending_score,
            reverse=True
        )[:limit]
