from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def inject(*dependency_classes: type) -> Callable[[F], F]:
    """Inject dependencies into route handler. Instantiates classes or calls from_request() if available."""

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
