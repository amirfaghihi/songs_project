from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import date, datetime
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar

from bson import ObjectId
from loguru import logger

if TYPE_CHECKING:
    from songs_api.settings import Settings

F = TypeVar("F", bound=Callable[..., Any])


class Cache:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.enabled = settings.is_production and settings.cache_enabled
        self.redis_client = None

        if self.enabled:
            try:
                import redis

                self.redis_client = redis.from_url(
                    settings.cache_redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}. Caching disabled.")
                self.enabled = False
                self.redis_client = None

    def get(self, key: str) -> Any | None:
        if not self.enabled or not self.redis_client:
            return None

        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")

        return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Serialize value to JSON and cache with TTL. Handles Pydantic models, dates, and ObjectIds."""
        if not self.enabled or not self.redis_client:
            return False

        try:
            if hasattr(value, "model_dump"):
                value = value.model_dump()
            elif hasattr(value, "dict") and not isinstance(value, dict):
                value = value.dict()
            def json_encoder(obj):
                if isinstance(obj, (date, datetime)):
                    return obj.isoformat()
                if isinstance(obj, ObjectId):
                    return str(obj)
                raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

            serialized = json.dumps(value, default=json_encoder)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Delete all cache keys matching pattern (e.g., 'songs:*')."""
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache invalidate pattern failed for {pattern}: {e}")
            return 0


_cache_instance: Cache | None = None


def init_cache(settings: Settings) -> Cache:
    global _cache_instance
    _cache_instance = Cache(settings)
    return _cache_instance


def get_cache() -> Cache | None:
    return _cache_instance


def cache_key(*args: Any, prefix: str = "") -> str:
    """Generate cache key from args. Hashes keys longer than 100 chars."""
    key_parts = [str(arg) for arg in args]
    key_string = ":".join(key_parts)

    if len(key_string) > 100:
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        key_string = f"{prefix}:hash:{key_hash}"
    elif prefix:
        key_string = f"{prefix}:{key_string}"

    return key_string


def cached(ttl: int = 300, key_prefix: str = "") -> Callable[[F], F]:
    """Cache function results using function name, args, and kwargs as key."""
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()
            if not cache or not cache.enabled:
                return func(*args, **kwargs)

            key_args = [func.__name__] + list(args) + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            key = cache_key(*key_args, prefix=key_prefix)

            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {key}")
                return cached_value

            logger.debug(f"Cache miss for key: {key}")
            result = func(*args, **kwargs)

            cache.set(key, result, ttl=ttl)

            return result

        return wrapper  # type: ignore

    return decorator
