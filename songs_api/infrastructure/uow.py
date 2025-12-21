from __future__ import annotations

from typing import Protocol

from songs_api.infrastructure.resources import SystemResources
from songs_api.repositories import RatingsRepository, SongsRepository, UsersRepository


class IUnitOfWork(Protocol):
    def __enter__(self) -> IUnitOfWork: ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...


class UnitOfWork:
    def __init__(self, resources: SystemResources | None = None):
        self._resources = resources or SystemResources.create_default()
        self._is_active = False

        self.songs_repository = SongsRepository(self._resources.cache_service)
        self.ratings_repository = RatingsRepository(self._resources.cache_service)
        self.users_repository = UsersRepository(self._resources.cache_service)

    def __enter__(self) -> UnitOfWork:
        self._is_active = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._is_active = False
