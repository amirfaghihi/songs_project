from __future__ import annotations

from typing import TYPE_CHECKING

from songs_api.models.documents import Rating, RatingStats
from songs_api.repositories.base_repository import BaseRepository

if TYPE_CHECKING:
    from songs_api.infrastructure.cache import Cache


class RatingsRepository(BaseRepository):
    def __init__(self, cache_service: Cache | None = None):
        super().__init__(cache_service)

    def add_rating(self, song_id: str, rating: int) -> RatingStats:
        Rating(song_id=song_id, rating=rating).save()

        RatingStats.objects(song_id=song_id).update_one(
            inc__count=1,
            inc__sum=rating,
            min__min=rating,
            max__max=rating,
            set_on_insert__song_id=song_id,
            upsert=True,
        )

        stats = RatingStats.objects(song_id=song_id).first()
        return stats

    def get_rating_stats(self, song_id: str) -> RatingStats | None:
        return RatingStats.objects(song_id=song_id).first()
