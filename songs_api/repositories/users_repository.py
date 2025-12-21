from __future__ import annotations

from typing import TYPE_CHECKING

from songs_api.models.documents import User
from songs_api.repositories.base_repository import BaseRepository

if TYPE_CHECKING:
    from songs_api.infrastructure.cache import Cache


class UsersRepository(BaseRepository):
    def __init__(self, cache_service: Cache | None = None):
        super().__init__(cache_service)

    def get_by_username(self, username: str) -> User | None:
        return User.objects(username=username).first()

    def create_user(self, username: str, password: str) -> User:
        user = User(username=username)
        user.set_password(password)
        user.save()
        return user
