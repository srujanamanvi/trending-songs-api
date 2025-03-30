import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.settings.config import settings
from app.services.database import db_service, create_indexes
from app.cache.redis_cache import redis_cache
from app.api.endpoints import router as api_router
from app.tasks import trending_scheduler

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown lifecycle"""
    try:
        logger.info("🚀 Starting application...")

        # Connect to database and cache
        await db_service.connect()
        await create_indexes(db_service)
        await redis_cache.connect()

        # Start the trending songs scheduler
        await trending_scheduler.start()

        yield  # Allows FastAPI to run

    finally:
        logger.info("🛑 Shutting down application...")

        # Close connections gracefully
        await db_service.close()
        await redis_cache.close()


# Initialize FastAPI with lifespan
app = FastAPI(
    title=settings.APP_NAME,
    description="Trending Songs Streaming Service",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Replace with actual allowed hosts in production
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Health Check Endpoint
@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy"}


# Run FastAPI with Uvicorn
def main():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)


if __name__ == "__main__":
    main()
