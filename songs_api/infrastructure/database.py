from __future__ import annotations

from mongoengine import connect, disconnect
from mongoengine.connection import get_connection


def init_db(mongo_uri: str, db_name: str) -> None:
    """Initialize MongoDB connection with connection pooling and retry settings."""
    try:
        get_connection(alias="default")
    except Exception:
        connect(
            host=mongo_uri,
            db=db_name,
            alias="default",
            maxPoolSize=100,
            minPoolSize=10,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=10000,
            socketTimeoutMS=45000,
            retryWrites=True,
            retryReads=True,
            maxIdleTimeMS=60000,
            waitQueueTimeoutMS=10000,
        )


def close_db() -> None:
    disconnect(alias="default")


def ensure_indexes() -> None:
    """Create database indexes for all document models."""
    from songs_api.models.documents import Rating, RatingStats, Song, User

    Song.ensure_indexes()
    Rating.ensure_indexes()
    RatingStats.ensure_indexes()
    User.ensure_indexes()
