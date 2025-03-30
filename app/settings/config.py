from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application Settings
    APP_NAME: str = "Trending Songs Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # MongoDB Configuration
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_USER: str = ""
    MONGODB_PASSWORD: str = ""
    MONGODB_DB: str = "trending_songs_db"

    # Construct MongoDB Connection String
    @property
    def MONGODB_URL(self) -> str:
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            return f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"

    # Redis Caching Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Construct Redis Connection String
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Caching Settings
    CACHE_EXPIRATION: int = 300  # 5 minutes

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    # Performance Tuning
    MAX_CONNECTIONS_COUNT: int = 10
    MIN_CONNECTIONS_COUNT: int = 2

    class Config:
        # Allows reading from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Allows environment variables to override .env
        env_nested_delimiter = "__"


# Create a singleton settings instance
settings = Settings()
