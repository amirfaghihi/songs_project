from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any

import jwt
from flask import current_app, request

from songs_api.api.errors import ApiError


def create_access_token(username: str) -> str:
    """Create a JWT access token for a user."""
    secret_key = str(current_app.config.get("JWT_SECRET_KEY", ""))
    algorithm = str(current_app.config.get("JWT_ALGORITHM", "HS256"))
    expire_minutes = int(current_app.config.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    expire = datetime.now(UTC) + timedelta(minutes=expire_minutes)
    payload = {
        "sub": username,
        "exp": expire,
        "iat": datetime.now(UTC),
    }
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def verify_access_token(token: str) -> str:
    """Verify a JWT access token and return the username."""
    secret_key = str(current_app.config.get("JWT_SECRET_KEY", ""))
    algorithm = str(current_app.config.get("JWT_ALGORITHM", "HS256"))

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub", "")
        if not username:
            raise ApiError(message="Invalid token", status_code=401)
        return username
    except jwt.ExpiredSignatureError as exc:
        raise ApiError(message="Token has expired", status_code=401) from exc
    except jwt.InvalidTokenError as exc:
        raise ApiError(message="Invalid token", status_code=401) from exc


def requires_jwt_auth[F: Callable[..., Any]](fn: F) -> F:
    """Require JWT authentication for a route."""

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise ApiError(message="Missing or invalid authorization header", status_code=401)

        token = auth_header.split(" ", 1)[1] if " " in auth_header else ""
        if not token:
            raise ApiError(message="Missing token", status_code=401)

        username = verify_access_token(token)
        request.jwt_username = username

        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
