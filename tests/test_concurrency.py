"""Concurrency tests to verify atomic operations and race condition handling."""

from __future__ import annotations

import concurrent.futures

from songs_api.infrastructure import UnitOfWork
from songs_api.models.documents import RatingStats


def test_concurrent_rating_updates(test_db, sample_songs):
    """Test that concurrent rating updates don't cause race conditions."""
    song_id = str(sample_songs[0].id)
    num_ratings = 50
    rating_value = 3

    def add_rating():
        with UnitOfWork() as uow:
            return uow.ratings_repository.add_rating(song_id=song_id, rating=rating_value)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(add_rating) for _ in range(num_ratings)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    assert all(result is not None for result in results)

    with UnitOfWork() as uow:
        final_stats = uow.ratings_repository.get_rating_stats(song_id=song_id)

    assert final_stats is not None
    assert final_stats.count == num_ratings
    assert final_stats.sum == num_ratings * rating_value
    assert final_stats.min == rating_value
    assert final_stats.max == rating_value
    assert final_stats.sum / final_stats.count == rating_value


def test_concurrent_mixed_ratings(test_db, sample_songs):
    """Test concurrent rating submissions with different values."""
    song_id = str(sample_songs[0].id)
    ratings = [1, 2, 3, 4, 5] * 10

    def add_rating(rating: int):
        with UnitOfWork() as uow:
            return uow.ratings_repository.add_rating(song_id=song_id, rating=rating)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(add_rating, r) for r in ratings]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    assert all(result is not None for result in results)

    with UnitOfWork() as uow:
        final_stats = uow.ratings_repository.get_rating_stats(song_id=song_id)

    assert final_stats.count == len(ratings)
    assert final_stats.sum == sum(ratings)
    assert final_stats.min == 1
    assert final_stats.max == 5
    expected_avg = sum(ratings) / len(ratings)
    assert abs(final_stats.sum / final_stats.count - expected_avg) < 0.01


def test_concurrent_ratings_multiple_songs(test_db, sample_songs):
    """Test concurrent ratings across multiple songs."""
    num_ratings_per_song = 20
    rating_value = 4

    def add_rating_to_song(song):
        song_id = str(song.id)
        with UnitOfWork() as uow:
            return uow.ratings_repository.add_rating(song_id=song_id, rating=rating_value)

    tasks = []
    for song in sample_songs:
        tasks.extend([(song, rating_value) for _ in range(num_ratings_per_song)])

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(add_rating_to_song, song) for song, _ in tasks]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    assert all(result is not None for result in results)

    for song in sample_songs:
        song_id = str(song.id)
        with UnitOfWork() as uow:
            stats = uow.ratings_repository.get_rating_stats(song_id=song_id)

        assert stats.count == num_ratings_per_song
        assert stats.sum == num_ratings_per_song * rating_value
        assert stats.min == rating_value
        assert stats.max == rating_value


def test_rating_stats_never_created_twice(test_db, sample_songs):
    """Test that RatingStats document is never duplicated even under concurrency."""
    song_id = str(sample_songs[0].id)
    num_concurrent_requests = 30

    def add_first_rating():
        with UnitOfWork() as uow:
            return uow.ratings_repository.add_rating(song_id=song_id, rating=5)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(add_first_rating) for _ in range(num_concurrent_requests)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    assert all(result is not None for result in results)

    stats_count = RatingStats.objects(song_id=song_id).count()
    assert stats_count == 1

    with UnitOfWork() as uow:
        stats = uow.ratings_repository.get_rating_stats(song_id=song_id)

    assert stats.count == num_concurrent_requests
