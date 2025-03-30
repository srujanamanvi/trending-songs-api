# Trending Songs API: Architecture & Design Documentation

## System Overview

The Trending Songs API is a high-performance, scalable service designed to track, analyze, and deliver trending music data. This document outlines the architecture decisions, component interactions, and technical specifications.

## Architecture

### High-Level Architecture
                        ┌───────────────────────────┐
                        │        Clients            │
                        │  (Mobile/Web Apps)        │
                        └──────────▲──────────────-─┘
                                   │
                    ┌──────────────┴──────────────┐
                    │      Load Balancer (LB)     │
                    │ (Nginx, HAProxy, AWS ALB)   │
                    └───────▲────────-▲───────────┘
                            │         │
                ┌───────────┴───┐ ┌───┴───────────┐
                │  FastAPI App  │ │  FastAPI App  │
                │   Instance 1  │ │   Instance 2  │
                └────────▲──────┘ └──────▲────────┘
                         │               │
                 ┌───────┴───────┐ ┌─────┴────────┐
                 │   Redis Cache │ │   Logger     │
                 │  (For Caching)│ │ (For Logs)   │
                 └───────────────┘ └──────────────┘
                            │
       ┌────────────────────┴──────────────────┐
       │          MongoDB Replica Set          │
       │ (Ensuring High Availability & Reads)  │
       └─────────────────────────────────────-─┘
            │            │            │
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │ Primary  │  │Secondary │  │Secondary │
    │ MongoDB  │  │ MongoDB  │  │ MongoDB  │
    └──────────┘  └──────────┘  └──────────┘


### Component Architecture

1. **Client Layer**
   - Web browsers
   - Mobile applications
   - External API consumers

2. **API Layer (FastAPI)**
   - Request routing and validation
   - Response serialization
   - API documentation (OpenAPI/Swagger)

3. **Service Layer**
   - DatabaseService: MongoDB interaction
   - RedisCache: Caching implementation
   - TrendingService: Trend calculation

4. **Data Layer**
   - MongoDB: Primary data storage
   - Redis: Caching layer


## Future Enhancements

1. Use Elastic search has it offers more benefits wrt speed, search and scale


## Database Architecture

### MongoDB Selection Rationale

MongoDB was chosen as the primary database for the following reasons:

1. **Document-Oriented Storage**:
   - Songs naturally fit a document model with varied attributes
   - Support for nested data structures (e.g., artist details, tags)

2. **Scalability**:
   - Horizontal scaling via sharding
   - High write throughput for trend updates
   - Efficient indexing for query performance

3. **Query Capabilities**:
   - Powerful aggregation framework for trend analysis
   - Rich query language for filtering (genre, artist, etc.)

4. **Performance**:
   - In-memory storage capabilities
   - Optimized for read-heavy workloads
   - Efficient for large datasets

### Collection Design

#### Songs Collection

```javascript
{
  "_id": ObjectId("..."),
  "song_id": "unique_identifier",
  "title": "Song Title",
  "artist": "Artist Name",
  "genre": "pop",
  "trending_score": 85.7,
  "album": "Album Name",
  "release_date": ISODate("2023-03-15"),
  "duration": 237,
  "spotify_url": "https://spotify.com/...",
  "tags": ["summer", "upbeat"],
  "last_updated": ISODate("2023-08-10T14:23:11.123Z")
}
```

**Indexes**:
- Primary: `{ song_id: 1 }` (unique)
- Secondary: `{ genre: 1, trending_score: -1 }`

## Caching Architecture

### Redis Implementation

Redis is used as an in-memory caching layer to:
1. Reduce database load
2. Improve response times
3. Handle traffic spikes efficiently

**Caching Strategy**:
- **Time-Based Expiration**: Cache entries expire after a configurable TTL
- **Key Structure**: `trending:{genre}:limit:{limit}`
- **Value Format**: Serialized JSON array of song objects

```python
# Example Redis key-value structure
"trending_songs:pop:limit:10" -> "[{song1}, {song2}, ...]"
"trending_songs:all:limit:100" -> "[{song1}, {song2}, ...]"
```

## API Design

### RESTful Endpoints

| Endpoint                         | Method | Description | Query Parameters |
|----------------------------------|--------|-------------|-----------------|
| `/api/v1/trending/songs`         | GET | Get trending songs | `limit`, `genre` |
| `/api/v1/trending/generate_data` | GET | Generate test data | None |

### Response Format

```json
{
  "songs": [
    {
      "song_id": "s123456",
      "title": "Example Song",
      "artist": "Example Artist",
      "genre": "pop",
      "trending_score": 95.7,
      "album": "Example Album",
      "release_date": "2023-03-15T00:00:00",
      "duration": 237,
      "spotify_url": "https://spotify.com/track/example",
      "tags": ["summer", "upbeat"]
    }
  ],
  "meta": {
    "count": 10,
    "genre": "pop",
    "cached": true,
    "cache_time": "2023-08-10T14:23:11.123Z"
  }
}
```

## Performance Optimizations

1. **Bulk Operations**
2. **Indexing Strategy**
3. **Caching Strategy**
4. **Asynchronous Processing**

## Scalability Considerations

1. **Horizontal Scaling**
2. **Vertical Scaling**
3. **Load Balancing**

## Monitoring and Logging

1. **Application Logging**
2. **Database Monitoring**
3. **Cache Monitoring**

