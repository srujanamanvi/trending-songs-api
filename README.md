# Music Trending API

A high-performance REST API for tracking and retrieving trending music data. Built with FastAPI, MongoDB, and Redis.

## Features

- Retrieve trending songs with optional genre filtering
- Fast response times with Redis caching
- Real-time trending score calculations
- Efficient MongoDB storage for song data
- RESTful API with comprehensive documentation

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database for storing song data
- **Motor**: Asynchronous MongoDB driver for Python
- **Redis**: In-memory data store used for caching
- **Pydantic**: Data validation and settings management

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Redis 6.0+

### Installation

1. Clone the repository
```bash
git clone https://github.com/srujanamanvi/trending-songs-api.git
cd trending-songs-api
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```


### Running Locally

1. Start Redis 
```bash
redis-server
```

2. Run migrations (if needed):
```
migrate-mongo up
```

3. Start the application
```bash
uvicorn app.main:app --reload
```

4. Visit API documentation at http://localhost:8000/docs

## API Endpoints

### Trending Songs

- `GET /api/v1/trending/songs`: Get top trending songs
  - Query Parameters:
    - `limit`: Maximum number of songs to return (default: 100)
    - `genre`: Filter by genre (optional)

### Trending Score Update

- `POST /api/v1/trending/update`: Trending score update based on updates in song data

### Data Generation (Development)

- `GET /api/v1/simulation/generate_data`: Generate seed data for testing


### Data Updation Simulation (Development)

- `GET /api/v1/simulation/simulate_streaming_data`: Update seed data to change changes in trending score


## Test Conditions via /docs (Locally)

- Step 1: Generate seed data
  - `GET /api/v1/simulation/generate_data`
  
- Step 2: Get top 100 songs
  - `GET /api/v1/trending/songs`
  
- Step 3: Get top 100 songs to verify caching
  - `GET /api/v1/trending/songs`
  
- Step 4: Make changes to the songs data vis simulate streaming data
  - `GET /api/v1/simulation/simulate_streaming_data` - updates trending score and caches the new top 100 songs

- Step 5: Get top 100 songs again
  - `GET /api/v1/trending/songs` - returns updated cached data

- Step 6: Pass genre to the GET songs API to see results per genre
  - `GET /api/v1/trending/songs?genre=POP` - returns cache data per genre


## Data Model

### Song

```python
class Song(BaseModel):
    song_id: str
    title: str
    artist: str
    genre: Genre
    trending_score: float
    album: Optional[str]
    release_date: Optional[datetime]
    duration: Optional[int]
    spotify_url: Optional[str]
    tags: Optional[List[str]]
```

## Running Tests

✅ Run a Specific Test File
```
pytest pytest app/tests/test_api_endpoints.py
```

## Database Management

### Connecting to MongoDB

```bash
# Connect to MongoDB shell
mongosh

# Select database
use your_database_name

# Show collections
show collections

# Query songs
db.songs.find().limit(5)
```

### Deleting Data

```bash
# Delete a specific song
db.songs.deleteOne({ song_id: "specific_song_id" })

# Delete all songs in a genre
db.songs.deleteMany({ genre: "pop" })

# Delete all songs
db.songs.deleteMany({})
```

## Development

### Project Structure

```
app/
├── settings/
│   └── config.py              # Application configuration
├── models/
│   └── song.py                # Pydantic data models
├── cache/
│   └── redis_cache.py
├── services/
│   ├── database.py            # MongoDB service
│   ├── data_generator.py      # data generator
│   └── trending_alogorithm.py # Trending calculation service
├── api/
│   └── endpoints.py           # API endpoints
├── tasks.py
├── constants.py
└── main.py                    # Application entry point
```

## Performance Considerations

- Redis caching is used to minimize database load
- Bulk operations for database updates
- Asynchronous request handling with FastAPI
