from datetime import datetime, timedelta
from app.services.trending_algorithm import TrendingAlgorithm
from app.services.data_generator import DataGenerator
from app.models.song import Song, Genre


def test_trending_score_calculation():
    """Test trending score calculation"""
    # Generate a test song
    songs = DataGenerator.generate_songs(num_songs=1)
    song = songs[0]

    # Calculate trending score
    score = TrendingAlgorithm.calculate_trending_score(song)

    # Assertions
    assert isinstance(score, float), "Trending score should be a float"
    assert score >= 0, "Trending score should be non-negative"


def test_trending_score_recency():
    """Test that more recent songs get higher scores"""
    # Create two songs with different timestamps
    recent_song = Song(
        title="Recent Hit",
        artist="New Artist",
        album="Latest Album",
        genre=Genre.POP,
        play_count=50000,
        last_played_timestamp=datetime.utcnow(),
        geographic_popularity={"US": 15000, "IND": 20000, "Others": 50000},
        user_rating=4.5
    )

    old_song = Song(
        title="Old Hit",
        artist="Veteran Artist",
        album="Classic Album",
        genre=Genre.POP,
        play_count=50000,
        last_played_timestamp=datetime.utcnow() - timedelta(days=30),
        geographic_popularity={"US": 5000, "IND": 25000, "Others": 10000},
        user_rating=4.5
    )

    # Calculate trending scores
    recent_score = TrendingAlgorithm.calculate_trending_score(recent_song)
    old_score = TrendingAlgorithm.calculate_trending_score(old_song)

    # Assert that recent song has higher score
    assert recent_score > old_score, "More recent song should have higher trending score"


def test_top_trending_songs():
    """Test retrieving top trending songs"""
    # Generate a large number of songs
    songs = DataGenerator.generate_songs(num_songs=200)

    # Get top trending songs (default 100)
    top_songs = TrendingAlgorithm.get_top_trending_songs(songs)

    # Assertions
    assert len(top_songs) <= 100, "Should return max 100 songs"

    # Verify sorting (descending order of trending score)
    for i in range(1, len(top_songs)):
        assert top_songs[i - 1].trending_score >= top_songs[
            i].trending_score, "Songs should be sorted by trending score"


def test_genre_filtering():
    """Test genre-specific trending songs"""
    # Generate songs with mixed genres
    songs = DataGenerator.generate_songs(num_songs=200)

    # Get top Pop songs
    pop_songs = TrendingAlgorithm.get_top_trending_songs(songs, genre=Genre.POP)

    # Assertions
    assert all(song.genre == Genre.POP for song in pop_songs), "Should only return Pop songs"
    assert len(pop_songs) <= 100, "Should return max 100 songs"


