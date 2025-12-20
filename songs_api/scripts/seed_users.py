"""Seed users into the database."""

from __future__ import annotations

from loguru import logger

from songs_api.infrastructure import UnitOfWork, ensure_indexes, init_db
from songs_api.settings import Settings


def seed_users() -> None:
    """Seed default test user into MongoDB if it doesn't exist."""
    ensure_indexes()

    test_username = "testuser"
    test_password = "testpass"

    with UnitOfWork() as uow:
        existing_user = uow.users_repository.get_by_username(test_username)
        if existing_user:
            logger.info(f"User '{test_username}' already exists. Skipping seed.")
            return

        user = uow.users_repository.create_user(username=test_username, password=test_password)
        logger.info(f"Seeded test user '{user.username}' into the database.")


if __name__ == "__main__":
    settings = Settings()
    init_db(mongo_uri=settings.mongo_uri, db_name=settings.mongo_db_name)
    seed_users()
