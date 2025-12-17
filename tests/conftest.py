from __future__ import annotations

from datetime import date

import mongomock
import pytest
from mongoengine import connect, disconnect

from songs_api import create_app
from songs_api.models.documents import Song
from songs_api.security.jwt_auth import create_access_token
from songs_api.settings import Settings


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
def app(test_db):
    """Create Flask app with test configuration."""
    settings = Settings(
        mongo_uri="mongodb://localhost:27017",
        mongo_db_name="songs_test_db",
        jwt_secret_key="test-secret-key",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=60,
        admin_username="testuser",
        admin_password="testpass",
        environment="local",
        log_level="ERROR",  # Suppress logs during tests
        rate_limit_enabled=False,  # Disable rate limiting for tests
    )

    app = create_app(settings=settings)
    app.config["TESTING"] = True

    yield app

    Song.drop_collection()


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def auth_token(app):
    """Generate a JWT token for tests."""
    with app.app_context():
        return create_access_token(username="testuser")


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
