"""Dependency injection utilities for Flask routes."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def inject(*dependency_classes: type) -> Callable[[F], F]:
    """
    Decorator that injects dependencies into route handlers.
    
    Supports both service classes (instantiated with no args) and special
    dependency classes like AuthUser (instantiated with from_request()).
    
    Example:
        @inject(AuthUser, SongsService)
        def my_route(auth: AuthUser, songs_service: SongsService):
            return {"user": auth.username}
    """

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            dependencies = []
            for cls in dependency_classes:
                if hasattr(cls, "from_request"):
                    dependencies.append(cls.from_request())
                else:
                    dependencies.append(cls())
            return f(*args, *dependencies, **kwargs)

        return wrapper  # type: ignore

    return decorator
