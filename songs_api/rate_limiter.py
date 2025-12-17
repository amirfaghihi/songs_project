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
    """
    Get identifier for rate limiting.

    Uses authenticated user if available, otherwise falls back to IP address.
    """
    # Check if user is authenticated via JWT
    if hasattr(request, "jwt_username") and request.jwt_username:
        return f"user:{request.jwt_username}"

    # Fall back to IP address
    return f"ip:{get_remote_address()}"


def create_limiter(app: Flask, settings: Settings) -> Limiter:
    """
    Create and configure rate limiter.

    Args:
        app: Flask application instance
        settings: Application settings

    Returns:
        Configured Limiter instance
    """
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

    logger.info(f"Rate limiting enabled with default: {settings.rate_limit_default}")

    limiter = Limiter(
        key_func=get_user_identifier,
        app=app,
        storage_uri=settings.rate_limit_storage_uri,
        default_limits=[settings.rate_limit_default],
        storage_options={"socket_connect_timeout": 30},
        strategy="fixed-window",
        headers_enabled=True,
    )

    # Log rate limit exceeded events
    @app.errorhandler(429)
    def rate_limit_handler(e):
        logger.warning(
            f"Rate limit exceeded for {get_user_identifier()} on {request.method} {request.path}",
            extra={"identifier": get_user_identifier(), "endpoint": request.endpoint},
        )
        return {"error": "Rate limit exceeded", "message": str(e.description)}, 429

    return limiter
