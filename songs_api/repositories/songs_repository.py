from __future__ import annotations

from typing import TYPE_CHECKING

from mongoengine import Q

from songs_api.models.documents import Song
from songs_api.repositories.base_repository import BaseRepository

if TYPE_CHECKING:
    from pymongo.client_session import ClientSession

    from songs_api.infrastructure.cache import Cache


class SongsRepository(BaseRepository):
    def __init__(self, cache_service: Cache | None = None, mongo_session: ClientSession | None = None):
        super().__init__(cache_service, mongo_session=mongo_session)

    def bulk_insert(self, songs: list[Song], *, load_bulk: bool = False) -> None:
        if not songs:
            return
        # Not all mongoengine versions support `session=` for QuerySet.insert().
        if self.mongo_session is None:
            Song.objects.insert(songs, load_bulk=load_bulk)
            return
        try:
            Song.objects.insert(songs, load_bulk=load_bulk, session=self.mongo_session)
        except TypeError:
            Song.objects.insert(songs, load_bulk=load_bulk)

    def list_songs(self, skip: int, limit: int) -> tuple[list[Song], int]:
        total = Song.objects.count()
        songs = list(Song.objects.skip(skip).limit(limit).order_by("id"))
        return songs, total

    def search_songs(self, query: str, skip: int, limit: int) -> tuple[list[Song], int]:
        q_filter = Q(artist__icontains=query) | Q(title__icontains=query)
        total = Song.objects(q_filter).count()
        songs = list(Song.objects(q_filter).skip(skip).limit(limit).order_by("id"))
        return songs, total

    def get_average_difficulty(self, level: int | None = None) -> float | None:
        queryset = Song.objects
        if level is not None:
            queryset = queryset.filter(level=level)

        result = queryset.average("difficulty")
        return float(result) if result is not None else None

    def get_by_id(self, song_id: str) -> Song | None:
        try:
            return Song.objects(id=song_id).first()
        except Exception:
            return None
