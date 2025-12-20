"""Route-level caching decorator for API responses."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from flask import request

from songs_api.infrastructure import cache_key, get_cache


def cached_response(prefix: str, ttl: int = 300):
    """
    Decorator to cache route responses.

    Caches the JSON response after model serialization.
    Automatically generates cache keys from request args.

    Args:
        prefix: Cache key prefix (e.g., "songs:list")
        ttl: Time to live in seconds (default: 300 = 5 minutes)

    Example:
        @bp.route("/songs")
        @requires_jwt_auth
        @cached_response("songs:list", ttl=300)
        def list_songs():
            response = service.list_songs(...)
            return jsonify(response.model_dump())
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()

            # If cache is disabled, just execute the function
            if not cache or not cache.enabled:
                return func(*args, **kwargs)

            # Generate cache key from route and query params
            cache_args = [func.__name__]

            # Include all query parameters in cache key
            if request.args:
                cache_args.extend([f"{k}={v}" for k, v in sorted(request.args.items())])

            # Include URL path parameters (e.g., song_id)
            if kwargs:
                cache_args.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])

            key = cache_key(*cache_args, prefix=prefix)

            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                # Return cached response (already serialized)
                from flask import jsonify

                return jsonify(cached_value)

            # Execute the function (it returns jsonify(...))
            result = func(*args, **kwargs)

            # Extract JSON data from the response to cache it
            if hasattr(result, "get_json"):
                json_data = result.get_json()
                if json_data is not None:
                    cache.set(key, json_data, ttl=ttl)

            return result

        return wrapper

    return decorator
