from __future__ import annotations

from typing import Protocol

from mongoengine.connection import get_connection
from pymongo.errors import OperationFailure

from songs_api.infrastructure.resources import SystemResources
from songs_api.repositories import RatingsRepository, SongsRepository, UsersRepository


class IUnitOfWork(Protocol):
    def __enter__(self) -> IUnitOfWork: ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...


class UnitOfWork:
    def __init__(self, resources: SystemResources | None = None, *, use_transactions: bool = False):
        self._resources = resources or SystemResources.create_default()
        self._is_active = False
        self._use_transactions = use_transactions

        self._mongo_session = None
        self._tx_active = False

        self.songs_repository = SongsRepository(self._resources.cache_service)
        self.ratings_repository = RatingsRepository(self._resources.cache_service)
        self.users_repository = UsersRepository(self._resources.cache_service)

    @staticmethod
    def _server_supports_transactions(client) -> bool:
        """
        Return True if the connected MongoDB deployment supports multi-document transactions.

        Transactions require:
        - replica set member (including single-node replica set) OR mongos (sharded cluster)
        - logical sessions enabled
        """
        try:
            try:
                hello = client.admin.command("hello")
            except Exception:
                # Older servers/drivers may use isMaster
                hello = client.admin.command("ismaster")
            is_replset_or_mongos = bool(hello.get("setName")) or hello.get("msg") == "isdbgrid"
            has_sessions = hello.get("logicalSessionTimeoutMinutes") is not None

            return is_replset_or_mongos and has_sessions
        except Exception:
            return False

    def _try_begin_transaction(self) -> None:
        client = get_connection(alias="default")
        if not self._server_supports_transactions(client):
            return

        session = None
        try:
            session = client.start_session()
            session.start_transaction()

            # Validate that the server accepts transaction semantics.
            # On standalone, the first command with a txnNumber will fail with IllegalOperation.
            client.admin.command("ping", session=session)

            self._mongo_session = session
            self._tx_active = True
        except OperationFailure:
            if session is not None:
                try:
                    session.abort_transaction()
                except Exception:
                    pass
                try:
                    session.end_session()
                except Exception:
                    pass
        except Exception:
            if session is not None:
                try:
                    session.end_session()
                except Exception:
                    pass

    def __enter__(self) -> UnitOfWork:
        self._is_active = True

        if self._use_transactions:
            # MongoDB transactions require a replica set (or sharded cluster).
            self._try_begin_transaction()

            if self._tx_active and self._mongo_session is not None:
                self.songs_repository.mongo_session = self._mongo_session
                self.ratings_repository.mongo_session = self._mongo_session
                self.users_repository.mongo_session = self._mongo_session

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            if self._tx_active and self._mongo_session is not None:
                if exc_type is None:
                    self._mongo_session.commit_transaction()
                else:
                    self._mongo_session.abort_transaction()
        finally:
            if self._mongo_session is not None:
                self._mongo_session.end_session()

            # Clean up repository session pointers
            self.songs_repository.mongo_session = None
            self.ratings_repository.mongo_session = None
            self.users_repository.mongo_session = None

            self._mongo_session = None
            self._tx_active = False
            self._is_active = False
