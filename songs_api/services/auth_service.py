from __future__ import annotations

from songs_api.api.errors import ApiError
from songs_api.security.jwt_auth import create_access_token


class AuthService:
    """Service layer for authentication operations."""

    def __init__(self, admin_username: str, admin_password: str):
        self.admin_username = admin_username
        self.admin_password = admin_password

    def login(self, username: str, password: str) -> str:
        """
        Authenticate user and return JWT token.
        
        Raises:
            ApiError: If credentials are invalid
        """
        if username != self.admin_username or password != self.admin_password:
            raise ApiError(message="Invalid credentials", status_code=401)

        return create_access_token(username=username)



