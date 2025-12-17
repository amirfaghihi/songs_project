def test_add_rating(client, auth_headers, sample_songs):
    """Test adding a rating to a song."""
    song_id = str(sample_songs[0].id)
    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id, "rating": 5},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["song_id"] == song_id
    assert data["average"] == 5.0
    assert data["lowest"] == 5
    assert data["highest"] == 5
    assert data["count"] == 1


def test_add_rating_invalid_range(client, auth_headers, sample_songs):
    """Test adding a rating outside valid range."""
    song_id = str(sample_songs[0].id)
    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id, "rating": 6},
    )
    assert response.status_code == 422


def test_add_rating_song_not_found(client, auth_headers):
    """Test adding a rating to a non-existent song."""
    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": "507f1f77bcf86cd799439011", "rating": 5},
    )
    assert response.status_code == 404


def test_get_rating_stats(client, auth_headers, sample_songs):
    """Test getting rating statistics for a song."""
    song_id = str(sample_songs[0].id)
    client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id, "rating": 3},
    )
    client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id, "rating": 5},
    )

    response = client.get(f"/api/v1/songs/{song_id}/ratings", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["song_id"] == song_id
    assert data["average"] == 4.0
    assert data["lowest"] == 3
    assert data["highest"] == 5
    assert data["count"] == 2


def test_get_rating_stats_no_ratings(client, auth_headers, sample_songs):
    """Test getting rating stats for a song with no ratings."""
    song_id = str(sample_songs[0].id)
    response = client.get(f"/api/v1/songs/{song_id}/ratings", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["song_id"] == song_id
    assert data["average"] is None
    assert data["count"] == 0


def test_ratings_require_auth(client, sample_songs):
    """Test that rating endpoints require authentication."""
    song_id = str(sample_songs[0].id)
    response = client.post(
        "/api/v1/songs/ratings",
        json={"song_id": song_id, "rating": 5},
    )
    assert response.status_code == 401

    response = client.get(f"/api/v1/songs/{song_id}/ratings")
    assert response.status_code == 401
