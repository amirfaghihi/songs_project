from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from songs_api.infrastructure.cache import Cache


class BaseRepository:
    def __init__(self, cache_service: Cache | None = None):
        self.cache = cache_service
