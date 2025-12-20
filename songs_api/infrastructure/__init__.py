"""Infrastructure module for application setup and configuration."""

from __future__ import annotations

from songs_api.infrastructure.cache import Cache, cache_key, cached, get_cache, init_cache
from songs_api.infrastructure.database import close_db, ensure_indexes, init_db
from songs_api.infrastructure.logging_config import configure_logging
from songs_api.infrastructure.rate_limiter import create_limiter
from songs_api.infrastructure.resources import SystemResources
from songs_api.infrastructure.uow import UnitOfWork

__all__ = [
    "Cache",
    "cache_key",
    "cached",
    "get_cache",
    "init_cache",
    "close_db",
    "ensure_indexes",
    "init_db",
    "configure_logging",
    "create_limiter",
    "SystemResources",
    "UnitOfWork",
]
