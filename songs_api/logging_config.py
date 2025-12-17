"""Logging configuration using loguru."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from flask import g, has_request_context, request
from loguru import logger

if TYPE_CHECKING:
    from songs_api.settings import Settings


def serialize_record(record: dict) -> dict:
    """
    Serialize log record for JSON output.

    Adds request-specific information when available.
    """
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }

    # Add request context if available
    if has_request_context():
        subset["request"] = {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", ""),
        }

        # Add user info if authenticated
        if hasattr(g, "jwt_username"):
            subset["user"] = g.jwt_username

    # Add exception info if present
    if record["exception"]:
        subset["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
        }

    return subset


def configure_logging(settings: Settings) -> None:
    """
    Configure loguru logging based on environment.

    In PRODUCTION: JSON format with structured logging
    In DEVELOPMENT/LOCAL: Human-readable text format with colors
    """
    # Remove default handler
    logger.remove()

    # Configure based on environment
    if settings.is_production:
        # Production: JSON structured logging
        import json

        def json_sink(message):
            """Custom sink that formats logs as JSON."""
            record = message.record
            json_data = serialize_record(record)
            sys.stdout.write(json.dumps(json_data) + "\n")
            sys.stdout.flush()

        logger.add(
            json_sink,
            level=settings.log_level,
            backtrace=False,
            diagnose=False,
        )
    else:
        # Development/Local: Human-readable format with colors
        logger.add(
            sys.stdout,
            level=settings.log_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    logger.info(f"Logging configured for {settings.environment.value} environment")
