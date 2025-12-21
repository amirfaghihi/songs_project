from __future__ import annotations

from typing import TYPE_CHECKING

from songs_api.models.documents import Rating, RatingStats
from songs_api.repositories.base_repository import BaseRepository

if TYPE_CHECKING:
    from pymongo.client_session import ClientSession

    from songs_api.infrastructure.cache import Cache


class RatingsRepository(BaseRepository):
    def __init__(self, cache_service: Cache | None = None, mongo_session: ClientSession | None = None):
        super().__init__(cache_service, mongo_session=mongo_session)

    def add_rating(self, song_id: str, rating: int) -> RatingStats:
        # MongoEngine session support is not consistent across APIs/versions.
        # In particular, QuerySet.update_one() does not accept `session=` in many versions.
        # When a transaction session is active, we use the underlying PyMongo collections directly.
        if self.mongo_session is None:
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

        ratings_coll = Rating._get_collection()
        stats_coll = RatingStats._get_collection()

        ratings_coll.insert_one({"song_id": song_id, "rating": rating}, session=self.mongo_session)
        stats_coll.update_one(
            {"song_id": song_id},
            {
                "$inc": {"count": 1, "sum": rating},
                "$min": {"min": rating},
                "$max": {"max": rating},
                "$setOnInsert": {"song_id": song_id},
            },
            upsert=True,
            session=self.mongo_session,
        )

        doc = stats_coll.find_one({"song_id": song_id}, session=self.mongo_session)
        return RatingStats(
            id=doc["_id"],
            song_id=doc["song_id"],
            count=doc.get("count", 0),
            sum=doc.get("sum", 0),
            min=doc.get("min", 5),
            max=doc.get("max", 1),
        )

    def get_rating_stats(self, song_id: str) -> RatingStats | None:
        return RatingStats.objects(song_id=song_id).first()
