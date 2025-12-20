"""Tests for Unit of Work and Repository pattern."""

from __future__ import annotations

from songs_api.infrastructure import SystemResources, UnitOfWork
from songs_api.repositories import RatingsRepository, SongsRepository, UsersRepository


def test_uow_initializes_with_resources(test_db):
    """Test that UnitOfWork initializes correctly with SystemResources."""
    resources = SystemResources.create_default()
    uow = UnitOfWork(resources)

    assert uow._resources is resources
    assert isinstance(uow.songs_repository, SongsRepository)
    assert isinstance(uow.ratings_repository, RatingsRepository)
    assert isinstance(uow.users_repository, UsersRepository)


def test_uow_initializes_with_default_resources(test_db):
    """Test that UnitOfWork can initialize with default resources."""
    uow = UnitOfWork()

    assert uow._resources is not None
    assert isinstance(uow.songs_repository, SongsRepository)
    assert isinstance(uow.ratings_repository, RatingsRepository)
    assert isinstance(uow.users_repository, UsersRepository)


def test_uow_context_manager(test_db):
    """Test that UnitOfWork works as a context manager."""
    with UnitOfWork() as uow:
        assert uow._is_active is True
        assert uow.songs_repository is not None

    assert uow._is_active is False


def test_uow_provides_songs_repository(test_db, sample_songs):
    """Test that UnitOfWork provides SongsRepository."""
    with UnitOfWork() as uow:
        songs, total = uow.songs_repository.list_songs(skip=0, limit=10)

        assert len(songs) == 3
        assert total == 3
        # Verify it's using the repository
        assert isinstance(uow.songs_repository, SongsRepository)


def test_uow_provides_ratings_repository(test_db, sample_songs):
    """Test that UnitOfWork provides RatingsRepository."""
    song_id = str(sample_songs[0].id)

    with UnitOfWork() as uow:
        stats = uow.ratings_repository.add_rating(song_id=song_id, rating=5)

        assert stats is not None
        assert stats.count == 1
        assert stats.sum == 5
        # Verify it's using the repository
        assert isinstance(uow.ratings_repository, RatingsRepository)


def test_uow_provides_users_repository(test_db):
    """Test that UnitOfWork provides UsersRepository."""
    with UnitOfWork() as uow:
        user = uow.users_repository.create_user(username="testuser123", password="testpass")

        assert user is not None
        assert user.username == "testuser123"
        # Verify it's using the repository
        assert isinstance(uow.users_repository, UsersRepository)


def test_repositories_receive_cache_service():
    """Test that repositories receive cache service from resources."""
    from songs_api.infrastructure.cache import Cache
    from songs_api.settings import Settings

    settings = Settings()
    cache = Cache(settings)
    resources = SystemResources(cache_service=cache)

    with UnitOfWork(resources) as uow:
        assert uow.songs_repository.cache is cache
        assert uow.ratings_repository.cache is cache
        assert uow.users_repository.cache is cache


def test_songs_repository_list_songs(test_db, sample_songs):
    """Test SongsRepository.list_songs method directly."""
    repo = SongsRepository()
    songs, total = repo.list_songs(skip=0, limit=2)

    assert len(songs) == 2
    assert total == 3


def test_songs_repository_search(test_db, sample_songs):
    """Test SongsRepository.search_songs method directly."""
    repo = SongsRepository()
    songs, total = repo.search_songs(query="Fastfinger", skip=0, limit=10)

    assert len(songs) >= 1
    assert any("Fastfinger" in song.artist for song in songs)


def test_songs_repository_average_difficulty(test_db, sample_songs):
    """Test SongsRepository.get_average_difficulty method directly."""
    repo = SongsRepository()
    avg = repo.get_average_difficulty(level=None)

    assert avg is not None
    assert isinstance(avg, float)


def test_ratings_repository_add_rating(test_db, sample_songs):
    """Test RatingsRepository.add_rating method directly."""
    repo = RatingsRepository()
    song_id = str(sample_songs[0].id)

    stats = repo.add_rating(song_id=song_id, rating=4)

    assert stats is not None
    assert stats.count == 1
    assert stats.sum == 4
    assert stats.min == 4
    assert stats.max == 4


def test_ratings_repository_get_stats(test_db, sample_songs):
    """Test RatingsRepository.get_rating_stats method directly."""
    repo = RatingsRepository()
    song_id = str(sample_songs[0].id)

    # Add a rating first
    repo.add_rating(song_id=song_id, rating=3)

    # Get stats
    stats = repo.get_rating_stats(song_id=song_id)

    assert stats is not None
    assert stats.count == 1
    assert stats.sum == 3


def test_users_repository_create_and_get(test_db):
    """Test UsersRepository create and get methods directly."""
    repo = UsersRepository()

    # Create user
    user = repo.create_user(username="newuser", password="password123")
    assert user is not None
    assert user.username == "newuser"

    # Get user
    found_user = repo.get_by_username("newuser")
    assert found_user is not None
    assert found_user.username == "newuser"
    assert found_user.check_password("password123")
