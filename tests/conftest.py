from __future__ import annotations

from datetime import date

import mongomock
import pytest
import secrets
from mongoengine import connect, disconnect

from songs_api import create_app
from songs_api.infrastructure import UnitOfWork
from songs_api.models.documents import Song, User
from songs_api.security.jwt_auth import create_access_token
from songs_api.settings import Environment, Settings


@pytest.fixture(scope="function")
def test_db():
    """Create a test database connection using mongomock."""
    disconnect(alias="default")
    connect(
        "mongoenginetest",
        host="mongodb://localhost",
        mongo_client_class=mongomock.MongoClient,
        alias="default",
    )
    yield
    disconnect(alias="default")


@pytest.fixture
def password_factory():
    """Generate a non-hardcoded password value for tests (avoids committed credential-like literals)."""

    def _make(nbytes: int = 18) -> str:
        return secrets.token_urlsafe(nbytes)

    return _make


@pytest.fixture
def test_user_credentials(password_factory):
    """Credentials for the default test user (password generated at runtime)."""
    return {"username": "testuser", "password": password_factory()}


@pytest.fixture
def app(test_db, test_user_credentials):
    """Create Flask app with test configuration."""
    settings = Settings(
        mongo_uri="mongodb://localhost:27017",
        mongo_db_name="songs_test_db",
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=60,
        environment=Environment.LOCAL,
        log_level="ERROR",
        rate_limit_enabled=False,
    )

    app = create_app(settings=settings)
    app.config["TESTING"] = True

    with app.app_context():
        with UnitOfWork() as uow:
            existing_user = uow.users_repository.get_by_username(test_user_credentials["username"])
            if not existing_user:
                uow.users_repository.create_user(
                    username=test_user_credentials["username"],
                    password=test_user_credentials["password"],
                )

    yield app

    Song.drop_collection()
    User.drop_collection()


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def auth_token(app, test_user_credentials):
    """Generate a JWT token for tests."""
    with app.app_context():
        return create_access_token(username=test_user_credentials["username"])


@pytest.fixture
def auth_headers(auth_token):
    """Generate JWT auth headers for tests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_songs(test_db):
    """Create sample songs for testing."""
    songs = [
        Song(
            artist="The Yousicians",
            title="Lycanthropic Metamorphosis",
            difficulty=14.6,
            level=13,
            released=date(2016, 10, 26),
        ),
        Song(
            artist="The Yousicians",
            title="A New Kennel",
            difficulty=9.1,
            level=9,
            released=date(2010, 2, 3),
        ),
        Song(
            artist="Mr Fastfinger",
            title="Awaki-Waki",
            difficulty=15.0,
            level=13,
            released=date(2012, 5, 11),
        ),
    ]
    Song.objects.insert(songs)
    return songs
