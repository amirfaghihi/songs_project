from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from songs_api.infrastructure.cache import Cache


class SystemResources:
    def __init__(self, cache_service: Cache | None = None):
        self.cache_service = cache_service

    @classmethod
    def create_default(cls) -> SystemResources:
        from songs_api.infrastructure.cache import get_cache

        cache = get_cache()
        return cls(cache_service=cache)
