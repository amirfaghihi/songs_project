from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from flask import current_app

from songs_api.api.errors import UnauthorizedError
from songs_api.constants import JWTClaim


def create_access_token(username: str) -> str:
    """Create JWT access token with expiration."""
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
    """Verify JWT token and return username. Raises UnauthorizedError if invalid."""
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
