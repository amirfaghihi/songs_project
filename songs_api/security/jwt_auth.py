from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
from typing import Any

import jwt
from flask import current_app, request

from songs_api.api.errors import UnauthorizedError
from songs_api.constants import JWTClaim


def create_access_token(username: str) -> str:
    """Create a JWT access token for a user."""
    secret_key = str(current_app.config.get("JWT_SECRET_KEY", ""))
    algorithm = str(current_app.config.get("JWT_ALGORITHM", "HS256"))
    expire_minutes = int(current_app.config.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60))

    expire = datetime.now(UTC) + timedelta(minutes=expire_minutes)
    payload = {
        JWTClaim.SUBJECT.value: username,
        JWTClaim.EXPIRATION.value: expire,
        JWTClaim.ISSUED_AT.value: datetime.now(UTC),
    }
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return token


def verify_access_token(token: str) -> str:
    """Verify a JWT access token and return the username."""
    secret_key = str(current_app.config.get("JWT_SECRET_KEY", ""))
    algorithm = str(current_app.config.get("JWT_ALGORITHM", "HS256"))

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get(JWTClaim.SUBJECT.value, "")
        if not username:
            raise UnauthorizedError(message="Invalid token")
        return username
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError(message="Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError(message="Invalid token") from exc


def requires_jwt_auth[F: Callable[..., Any]](fn: F) -> F:
    """Require JWT authentication for a route."""

    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any):
        auth_header = request.headers.get("Authorization", "").strip()

        if not auth_header:
            raise UnauthorizedError(
                message="Missing authorization header. Expected format: 'Authorization: Bearer <token>'"
            )

        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise UnauthorizedError(message="Invalid authorization header format. Expected: 'Bearer <token>'")

        token = parts[1].strip()
        if not token:
            raise UnauthorizedError(message="Missing token in authorization header")

        username = verify_access_token(token)
        request.jwt_username = username

        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
