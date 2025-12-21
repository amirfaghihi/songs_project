from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import request

from songs_api.infrastructure import cache_key, get_cache


def cached_response(prefix: str, ttl: int = 300):
    """Cache route responses using request args and kwargs as cache key."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()

            if not cache or not cache.enabled:
                return func(*args, **kwargs)

            cache_args = [func.__name__]

            if request.args:
                cache_args.extend([f"{k}={v}" for k, v in sorted(request.args.items())])

            if kwargs:
                cache_args.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])

            key = cache_key(*cache_args, prefix=prefix)

            cached_value = cache.get(key)
            if cached_value is not None:
                from flask import jsonify

                return jsonify(cached_value)

            result = func(*args, **kwargs)

            if hasattr(result, "get_json"):
                json_data = result.get_json()
                if json_data is not None:
                    cache.set(key, json_data, ttl=ttl)

            return result

        return wrapper

    return decorator
