from __future__ import annotations

from dataclasses import dataclass

from flask import request

from songs_api.api.errors import UnauthorizedError
from songs_api.security.jwt_auth import verify_access_token


@dataclass
class AuthUser:
    username: str

    @classmethod
    def from_request(cls) -> AuthUser:
        """Extract and validate JWT token from Authorization header."""
        auth_header = request.headers.get("Authorization", "").strip()

        if not auth_header:
            raise UnauthorizedError(message="Missing authorization header")

        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise UnauthorizedError(message="Invalid authorization header")

        token = parts[1].strip()
        if not token:
            raise UnauthorizedError(message="Missing token")

        username = verify_access_token(token)
        return cls(username=username)

