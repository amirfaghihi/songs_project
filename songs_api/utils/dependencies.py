"""Dependency injection utilities for Flask routes."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def inject(*service_classes: type) -> Callable[[F], F]:
    """Decorator that injects service instances into route handlers."""

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            services = [cls() for cls in service_classes]
            return f(*args, *services, **kwargs)

        return wrapper  # type: ignore

    return decorator
