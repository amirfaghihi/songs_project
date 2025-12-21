from __future__ import annotations

from enum import Enum

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from songs_api.constants import LogFormat, LogLevel, PaginationDefaults


class Environment(str, Enum):
    """Application runtime environment."""

    LOCAL = "local"
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: Environment = Environment.LOCAL

    mongo_db_name: str = "songs_db"
    mongo_uri: str | None = Field(default=None, description="MongoDB URI (built from components if not provided)")
    mongo_root_username: str = "root"
    mongo_root_password: str = "adminpassword"
    mongo_host: str = "localhost"
    mongo_port: int = 27017
    mongo_replica_set_name: str | None = Field(default=None, description="MongoDB replica set name (e.g., 'rs0')")

    songs_json_path: str = "songs.json"

    max_page_size: int = PaginationDefaults.MAX_PAGE_SIZE

    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    @model_validator(mode="after")
    def build_mongo_uri(self) -> Settings:
        """Build mongo_uri from components if not explicitly provided."""
        if self.mongo_uri is None:
            # Build query parameters
            query_params = []
            if self.mongo_root_username and self.mongo_root_password:
                query_params.append("authSource=admin")
            if self.mongo_replica_set_name:
                query_params.append(f"replicaSet={self.mongo_replica_set_name}")

            query_string = "&".join(query_params) if query_params else ""
            query_prefix = "?" if query_string else ""

            if self.mongo_root_username and self.mongo_root_password:
                self.mongo_uri = (
                    f"mongodb://{self.mongo_root_username}:{self.mongo_root_password}"
                    f"@{self.mongo_host}:{self.mongo_port}/{self.mongo_db_name}{query_prefix}{query_string}"
                )
            else:
                self.mongo_uri = f"mongodb://{self.mongo_host}:{self.mongo_port}{query_prefix}{query_string}"
        return self

    api_title: str = "Songs API"
    api_version: str = "1.0.0"

    log_level: str = LogLevel.INFO.value
    log_format: str = LogFormat.TEXT.value

    rate_limit_enabled: bool = True
    rate_limit_default: str = "100 per minute"
    rate_limit_redis_url: str = "redis://localhost:6379/1"
    rate_limit_storage_uri: str | None = None

    cache_enabled: bool = True
    cache_redis_url: str = "redis://localhost:6379/0"
    cache_default_ttl: int = 300

    gunicorn_workers: int = Field(default=4, description="Number of gunicorn worker processes")

    @model_validator(mode="after")
    def configure_rate_limit_storage(self) -> Settings:
        """Configure rate limit storage based on environment."""
        if self.rate_limit_storage_uri is None:
            if self.environment == Environment.PRODUCTION:
                self.rate_limit_storage_uri = self.rate_limit_redis_url
            else:
                self.rate_limit_storage_uri = "memory://"
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_local(self) -> bool:
        return self.environment == Environment.LOCAL
