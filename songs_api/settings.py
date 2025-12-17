from __future__ import annotations

from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application runtime environment."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Field names are automatically mapped to uppercase environment variables.
    For example: mongo_uri -> MONGO_URI, jwt_secret_key -> JWT_SECRET_KEY
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment
    environment: Environment = Environment.LOCAL

    # MongoDB Configuration
    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "songs_db"

    # Songs Data
    songs_json_path: str = "songs.json"

    # Pagination
    max_page_size: int = 100

    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Admin Credentials
    admin_username: str = "admin"
    admin_password: str = "admin"

    # API Metadata
    api_title: str = "Songs API"
    api_version: str = "1.0.0"

    # Logging
    log_level: str = "INFO"
    log_format: str = "text"  # "text" or "json"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_default: str = "100 per minute"
    rate_limit_storage_uri: str = "memory://"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_local(self) -> bool:
        """Check if running in local environment."""
        return self.environment == Environment.LOCAL
