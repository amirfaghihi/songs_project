from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pymongo.client_session import ClientSession

    from songs_api.infrastructure.cache import Cache


class BaseRepository:
    def __init__(self, cache_service: Cache | None = None, mongo_session: ClientSession | None = None):
        self.cache = cache_service
        self.mongo_session = mongo_session
