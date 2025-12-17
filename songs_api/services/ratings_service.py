from __future__ import annotations

from songs_api.api.errors import ApiError
from songs_api.schemas import RatingStatsResponse
from songs_api.uow import UnitOfWork


class RatingsService:
    """Service layer for ratings-related business logic."""

    def add_rating(self, song_id: str, rating: int) -> RatingStatsResponse:
        """
        Add a rating for a song and return updated statistics.

        Args:
            song_id: MongoDB ObjectId of the song
            rating: Rating value (1-5)

        Returns:
            RatingStatsResponse with updated statistics

        Raises:
            ApiError: If song not found (404)
        """
        with UnitOfWork() as uow:
            song = uow.get_song_by_id(song_id)
            if not song:
                raise ApiError(message="Song not found", status_code=404)

            stats = uow.add_rating(song_id=song_id, rating=rating)

        average = stats.sum / stats.count if stats.count > 0 else None

        return RatingStatsResponse(
            song_id=song_id,
            average=average,
            lowest=stats.min,
            highest=stats.max,
            count=stats.count,
        )

    def get_rating_stats(self, song_id: str) -> RatingStatsResponse:
        """
        Get rating statistics for a song.

        Args:
            song_id: MongoDB ObjectId of the song

        Returns:
            RatingStatsResponse with statistics or zeros if no ratings exist

        Raises:
            ApiError: If song not found (404)
        """
        with UnitOfWork() as uow:
            song = uow.get_song_by_id(song_id)
            if not song:
                raise ApiError(message="Song not found", status_code=404)

            stats = uow.get_rating_stats(song_id=song_id)

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
