"""Song repository for data access."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mongoengine import Q

from songs_api.models.documents import Song
from songs_api.repositories.base_repository import BaseRepository

if TYPE_CHECKING:
    from songs_api.infrastructure.cache import Cache


class SongsRepository(BaseRepository):
    """Repository for Song entity operations."""

    def __init__(self, cache_service: Cache | None = None):
        super().__init__(cache_service)

    def list_songs(self, skip: int, limit: int) -> tuple[list[Song], int]:
        """List songs with pagination."""
        total = Song.objects.count()
        songs = list(Song.objects.skip(skip).limit(limit).order_by("id"))
        return songs, total

    def search_songs(self, query: str, skip: int, limit: int) -> tuple[list[Song], int]:
        """Search songs by artist or title using case-insensitive substring matching."""
        q_filter = Q(artist__icontains=query) | Q(title__icontains=query)
        total = Song.objects(q_filter).count()
        songs = list(Song.objects(q_filter).skip(skip).limit(limit).order_by("id"))
        return songs, total

    def get_average_difficulty(self, level: int | None = None) -> float | None:
        """Calculate average difficulty, optionally filtered by level."""
        queryset = Song.objects
        if level is not None:
            queryset = queryset.filter(level=level)

        result = queryset.average("difficulty")
        return float(result) if result is not None else None

    def get_by_id(self, song_id: str) -> Song | None:
        """Get a song by ID."""
        try:
            return Song.objects(id=song_id).first()
        except Exception:
            return None
