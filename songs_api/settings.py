from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "songs_db"
    songs_json_path: str = "songs.json"
    max_page_size: int = 100

    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    
    admin_username: str = "admin"
    admin_password: str = "admin"

    api_title: str = "Songs API"
    api_version: str = "1.0.0"


