from __future__ import annotations

from songs_api.api.errors import NotFoundError
from songs_api.infrastructure import UnitOfWork, get_cache
from songs_api.schemas import RatingStatsResponse


class RatingsService:
    """Service layer for ratings-related business logic."""

    def add_rating(self, song_id: str, rating: int) -> RatingStatsResponse:
        """Add a rating for a song and return updated statistics."""
        with UnitOfWork() as uow:
            song = uow.songs_repository.get_by_id(song_id)
            if not song:
                raise NotFoundError(message="Song not found")

            stats = uow.ratings_repository.add_rating(song_id=song_id, rating=rating)

        cache = get_cache()
        if cache:
            cache.delete(f"ratings:stats:{song_id}")

        average = stats.sum / stats.count if stats.count > 0 else None

        return RatingStatsResponse(
            song_id=song_id,
            average=average,
            lowest=stats.min,
            highest=stats.max,
            count=stats.count,
        )

    def get_rating_stats(self, song_id: str) -> RatingStatsResponse:
        """Get rating statistics for a song."""
        with UnitOfWork() as uow:
            song = uow.songs_repository.get_by_id(song_id)
            if not song:
                raise NotFoundError(message="Song not found")

            stats = uow.ratings_repository.get_rating_stats(song_id=song_id)

        if not stats:
            return RatingStatsResponse(
                song_id=song_id,
                average=None,
                lowest=None,
                highest=None,
                count=0,
            )

        average = stats.sum / stats.count if stats.count > 0 else None

        return RatingStatsResponse(
            song_id=song_id,
            average=average,
            lowest=stats.min,
            highest=stats.max,
            count=stats.count,
        )
