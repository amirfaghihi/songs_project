"""Initialize database and create indexes."""

from __future__ import annotations

from songs_api.infrastructure import ensure_indexes, init_db
from songs_api.settings import Settings


def main() -> None:
    """Initialize database connection and create indexes."""
    settings = Settings()
    init_db(mongo_uri=settings.mongo_uri, db_name=settings.mongo_db_name)
    ensure_indexes()
    print("Database initialized and indexes created.")


if __name__ == "__main__":
    main()
