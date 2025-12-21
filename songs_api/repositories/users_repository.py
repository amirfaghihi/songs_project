from __future__ import annotations

from typing import TYPE_CHECKING

from songs_api.models.documents import User
from songs_api.repositories.base_repository import BaseRepository

if TYPE_CHECKING:
    from pymongo.client_session import ClientSession

    from songs_api.infrastructure.cache import Cache


class UsersRepository(BaseRepository):
    def __init__(self, cache_service: Cache | None = None, mongo_session: ClientSession | None = None):
        super().__init__(cache_service, mongo_session=mongo_session)

    def get_by_username(self, username: str) -> User | None:
        return User.objects(username=username).first()

    def create_user(self, username: str, password: str) -> User:
        user = User(username=username)
        user.set_password(password)
        user.save(session=self.mongo_session)
        return user
