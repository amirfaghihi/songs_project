from __future__ import annotations

from mongoengine import connect, disconnect
from mongoengine.connection import get_connection


def init_db(mongo_uri: str, db_name: str) -> None:
    """Initialize MongoEngine connection."""
    try:
        # Check if connection already exists (e.g., in tests)
        get_connection(alias="default")
    except Exception:
        # Connection doesn't exist, create it
        connect(host=mongo_uri, db=db_name, alias="default")


def close_db() -> None:
    """Close MongoEngine connection."""
    disconnect(alias="default")


def ensure_indexes() -> None:
    """Ensure all document indexes are created."""
    from songs_api.models.documents import Rating, RatingStats, Song

    Song.ensure_indexes()
    Rating.ensure_indexes()
    RatingStats.ensure_indexes()
