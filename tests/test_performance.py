"""Performance tests for large datasets to verify scalability."""

from __future__ import annotations

import time
from datetime import date

import pytest

from songs_api.infrastructure import UnitOfWork
from songs_api.models.documents import Rating, Song


@pytest.fixture
def large_song_dataset(test_db):
    """Create a large dataset of songs for performance testing."""
    songs = []
    for i in range(1000):
        song = Song(
            artist=f"Artist {i % 100}",
            title=f"Song {i}",
            difficulty=float(i % 20),
            level=(i % 13) + 1,
            released=date(2020 + (i % 5), (i % 12) + 1, 1),
        )
        songs.append(song)

    with UnitOfWork() as uow:
        uow.songs_repository.bulk_insert(songs, load_bulk=False)
    return songs


def test_pagination_performance_large_dataset(large_song_dataset):
    """Test pagination performance with 1000 songs."""
    start_time = time.time()

    with UnitOfWork() as uow:
        songs, total = uow.songs_repository.list_songs(skip=0, limit=20)

    elapsed = time.time() - start_time

    assert len(songs) == 20
    assert total == 1000
    assert elapsed < 0.1


def test_pagination_deep_pages(large_song_dataset):
    """Test pagination performance on deep pages."""
    start_time = time.time()

    with UnitOfWork() as uow:
        songs, total = uow.songs_repository.list_songs(skip=980, limit=20)

    elapsed = time.time() - start_time

    assert len(songs) == 20
    assert total == 1000
    assert elapsed < 0.15


def test_search_performance_large_dataset(large_song_dataset):
    """Test search performance with large dataset."""
    start_time = time.time()

    with UnitOfWork() as uow:
        songs, _ = uow.songs_repository.search_songs(query="Artist 42", skip=0, limit=20)

    elapsed = time.time() - start_time

    assert len(songs) >= 1
    assert elapsed < 0.2


def test_average_difficulty_performance_large_dataset(large_song_dataset):
    """Test average difficulty calculation performance."""
    start_time = time.time()

    with UnitOfWork() as uow:
        avg = uow.songs_repository.get_average_difficulty(level=None)

    elapsed = time.time() - start_time

    assert avg is not None
    assert elapsed < 0.1


def test_average_difficulty_filtered_performance(large_song_dataset):
    """Test filtered average difficulty performance."""
    start_time = time.time()

    with UnitOfWork() as uow:
        avg = uow.songs_repository.get_average_difficulty(level=5)

    elapsed = time.time() - start_time

    assert avg is not None
    assert elapsed < 0.1


def test_rating_stats_retrieval_performance(test_db, sample_songs):
    """Test that rating stats retrieval is O(1) even with many ratings."""
    song_id = str(sample_songs[0].id)

    for i in range(100):
        Rating(song_id=song_id, rating=(i % 5) + 1).save()

    with UnitOfWork() as uow:
        for i in range(100):
            uow.ratings_repository.add_rating(song_id=song_id, rating=(i % 5) + 1)

    start_time = time.time()

    with UnitOfWork() as uow:
        stats = uow.ratings_repository.get_rating_stats(song_id=song_id)

    elapsed = time.time() - start_time

    assert stats is not None
    assert elapsed < 0.05


def test_multiple_songs_rating_stats_performance(test_db, sample_songs):
    """Test retrieving rating stats for multiple songs."""
    for song in sample_songs:
        song_id = str(song.id)
        with UnitOfWork() as uow:
            for i in range(10):
                uow.ratings_repository.add_rating(song_id=song_id, rating=(i % 5) + 1)

    start_time = time.time()

    stats_list = []
    for song in sample_songs:
        song_id = str(song.id)
        with UnitOfWork() as uow:
            stats = uow.ratings_repository.get_rating_stats(song_id=song_id)
            stats_list.append(stats)

    elapsed = time.time() - start_time

    assert len(stats_list) == len(sample_songs)
    assert all(s is not None for s in stats_list)
    assert elapsed < 0.1


def test_search_with_pagination_performance(large_song_dataset):
    """Test search with pagination on large dataset."""
    start_time = time.time()

    with UnitOfWork() as uow:
        songs, _ = uow.songs_repository.search_songs(query="Song", skip=100, limit=50)

    elapsed = time.time() - start_time

    assert len(songs) <= 50
    assert elapsed < 0.3


def test_compound_index_performance(large_song_dataset):
    """Test that compound indexes improve filtered query performance."""
    start_time = time.time()

    songs = list(Song.objects(level=5).order_by("difficulty").limit(20))

    elapsed = time.time() - start_time

    assert len(songs) <= 20
    assert elapsed < 0.1


def test_artist_released_compound_index(large_song_dataset):
    """Test that (artist, released) compound index improves performance."""
    start_time = time.time()

    songs = list(Song.objects(artist="Artist 10").order_by("-released").limit(20))

    elapsed = time.time() - start_time

    assert len(songs) <= 20
    assert elapsed < 0.1
