"""Rate limiting configuration and utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from loguru import logger

if TYPE_CHECKING:
    from flask import Flask

    from songs_api.settings import Settings


def get_user_identifier() -> str:
    """Get identifier for rate limiting."""
    if hasattr(request, "jwt_username") and request.jwt_username:
        return f"user:{request.jwt_username}"

    return f"ip:{get_remote_address()}"


def create_limiter(app: Flask, settings: Settings) -> Limiter:
    """Create and configure rate limiter."""
    if not settings.rate_limit_enabled:
        logger.info("Rate limiting is disabled")
        limiter = Limiter(
            key_func=get_user_identifier,
            app=app,
            storage_uri=settings.rate_limit_storage_uri,
            default_limits=[],
            enabled=False,
        )
        return limiter

    storage_type = "Redis" if settings.rate_limit_storage_uri.startswith("redis://") else "in-memory"
    logger.info(f"Rate limiting enabled with {storage_type} storage (default: {settings.rate_limit_default})")

    limiter = Limiter(
        key_func=get_user_identifier,
        app=app,
        storage_uri=settings.rate_limit_storage_uri,
        default_limits=[settings.rate_limit_default],
        storage_options={"socket_connect_timeout": 30},
        strategy="fixed-window",
        headers_enabled=True,
    )

    @app.errorhandler(429)
    def rate_limit_handler(e):
        logger.warning(
            f"Rate limit exceeded for {get_user_identifier()} on {request.method} {request.path}",
            extra={"identifier": get_user_identifier(), "endpoint": request.endpoint},
        )
        return {"error": "Rate limit exceeded", "message": str(e.description)}, 429

    return limiter
