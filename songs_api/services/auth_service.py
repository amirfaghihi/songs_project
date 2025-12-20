from __future__ import annotations

from songs_api.api.errors import ConflictError, UnauthorizedError
from songs_api.infrastructure import UnitOfWork
from songs_api.security.jwt_auth import create_access_token


class AuthService:
    """Service layer for authentication operations."""

    def login(self, username: str, password: str) -> str:
        """Authenticate user and return JWT token."""
        with UnitOfWork() as uow:
            user = uow.users_repository.get_by_username(username)

            if not user:
                raise UnauthorizedError(message="Invalid credentials")

            if not user.check_password(password):
                raise UnauthorizedError(message="Invalid credentials")

        return create_access_token(username=username)

    def register(self, username: str, password: str) -> dict[str, str]:
        """Register a new user."""
        with UnitOfWork() as uow:
            existing_user = uow.users_repository.get_by_username(username)
            if existing_user:
                raise ConflictError(message="Username already exists")

            user = uow.users_repository.create_user(username=username, password=password)

        return {"message": "User registered successfully", "username": user.username}
