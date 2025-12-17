from __future__ import annotations

from typing import Protocol

from mongoengine import Q

from songs_api.models.documents import Rating, RatingStats, Song


class IUnitOfWork(Protocol):
    """Unit of Work interface for database operations."""

    def __enter__(self) -> IUnitOfWork: ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...


class UnitOfWork:
    """Unit of Work implementation for repository pattern with MongoEngine."""

    def __enter__(self) -> UnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def list_songs(self, skip: int, limit: int) -> tuple[list[Song], int]:
        """List songs with pagination."""
        total = Song.objects.count()
        songs = list(Song.objects.skip(skip).limit(limit).order_by("id"))
        return songs, total

    def search_songs(self, query: str, skip: int, limit: int) -> tuple[list[Song], int]:
        """Search songs by artist or title with text search, falling back to regex."""
        try:
            songs = list(Song.objects.search_text(query).order_by("$text_score").skip(skip).limit(limit))
            total = Song.objects.search_text(query).count()
            if songs:
                return songs, total
        except Exception:
            pass

        q_filter = Q(artist__icontains=query) | Q(title__icontains=query)
        total = Song.objects(q_filter).count()
        songs = list(Song.objects(q_filter).skip(skip).limit(limit).order_by("id"))
        return songs, total

    def get_average_difficulty(self, level: int | None = None) -> float | None:
        """Get average difficulty, optionally filtered by level."""
        queryset = Song.objects
        if level is not None:
            queryset = queryset.filter(level=level)

        result = queryset.average("difficulty")
        return float(result) if result is not None else None

    def get_song_by_id(self, song_id: str) -> Song | None:
        """Get a song by ID."""
        try:
            return Song.objects(id=song_id).first()
        except Exception:
            return None

    def add_rating(self, song_id: str, rating: int) -> RatingStats:
        """Add a rating and update rating stats atomically."""
        Rating(song_id=song_id, rating=rating).save()

        stats = RatingStats.objects(song_id=song_id).first()
        if stats:
            stats.count += 1
            stats.sum += rating
            stats.min = min(stats.min, rating)
            stats.max = max(stats.max, rating)
            stats.save()
            return stats
        else:
            stats = RatingStats(
                song_id=song_id,
                count=1,
                sum=rating,
                min=rating,
                max=rating,
            )
            stats.save()
            return stats

    def get_rating_stats(self, song_id: str) -> RatingStats | None:
        """Get rating statistics for a song."""
        return RatingStats.objects(song_id=song_id).first()
