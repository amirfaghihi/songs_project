from __future__ import annotations

import sys
from enum import Enum
from typing import TYPE_CHECKING

from flask import g, has_request_context, request
from loguru import logger

if TYPE_CHECKING:
    from songs_api.settings import Settings


def serialize_record(record: dict) -> dict:
    """Extract relevant fields from loguru record for JSON serialization."""
    subset = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["name"],
        "function": record["function"],
        "line": record["line"],
    }

    if has_request_context():
        subset["request"] = {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.remote_addr,
            "user_agent": request.headers.get("User-Agent", ""),
        }

        if hasattr(g, "jwt_username"):
            subset["user"] = g.jwt_username

    if record["exception"]:
        subset["exception"] = {
            "type": record["exception"].type.__name__ if record["exception"].type else None,
            "value": str(record["exception"].value) if record["exception"].value else None,
        }

    return subset


def configure_logging(settings: Settings) -> None:
    """Configure loguru logging based on environment."""
    logger.remove()

    if settings.is_production:
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

    env_value = settings.environment.value if isinstance(settings.environment, Enum) else str(settings.environment)
    logger.info(f"Logging configured for {env_value} environment")
