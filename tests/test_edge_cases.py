"""Edge case tests for improved coverage."""

from __future__ import annotations


def test_list_songs_max_page_size(client, auth_headers, sample_songs):
    """Test pagination with maximum page size."""
    response = client.get("/api/v1/songs?page=1&page_size=100", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) <= 100


def test_list_songs_exceeds_max_page_size(client, auth_headers, sample_songs):
    """Test that page size exceeding maximum is rejected."""
    response = client.get("/api/v1/songs?page=1&page_size=101", headers=auth_headers)
    assert response.status_code == 422


def test_list_songs_invalid_page(client, auth_headers, sample_songs):
    """Test pagination with invalid page number."""
    response = client.get("/api/v1/songs?page=0&page_size=20", headers=auth_headers)
    assert response.status_code == 422


def test_list_songs_negative_page_size(client, auth_headers, sample_songs):
    """Test pagination with negative page size."""
    response = client.get("/api/v1/songs?page=1&page_size=-1", headers=auth_headers)
    assert response.status_code == 422


def test_list_songs_beyond_last_page(client, auth_headers, sample_songs):
    """Test requesting page beyond available data."""
    response = client.get("/api/v1/songs?page=999&page_size=20", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 0
    assert data["pagination"]["page"] == 999


def test_search_songs_empty_result(client, auth_headers, sample_songs):
    """Test search with no matching results."""
    response = client.get("/api/v1/songs/search?message=nonexistentartist", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 0
    assert data["pagination"]["total"] == 0


def test_search_songs_special_characters(client, auth_headers, sample_songs):
    """Test search with special characters."""
    response = client.get("/api/v1/songs/search?message=Mr%20Fastfinger", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) >= 1


def test_search_songs_case_insensitive(client, auth_headers, sample_songs):
    """Test that search is case insensitive."""
    response1 = client.get("/api/v1/songs/search?message=YOUSICIANS", headers=auth_headers)
    response2 = client.get("/api/v1/songs/search?message=yousicians", headers=auth_headers)

    assert response1.status_code == 200
    assert response2.status_code == 200

    data1 = response1.get_json()
    data2 = response2.get_json()

    assert len(data1["data"]) == len(data2["data"])


def test_average_difficulty_nonexistent_level(client, auth_headers, sample_songs):
    """Test average difficulty for level with no songs."""
    response = client.get("/api/v1/songs/difficulty/average?level=999", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["average_difficulty"] in [None, 0.0]
    assert data["level"] == 999


def test_average_difficulty_invalid_level(client, auth_headers):
    """Test average difficulty with invalid level parameter."""
    response = client.get("/api/v1/songs/difficulty/average?level=invalid", headers=auth_headers)
    assert response.status_code == 400


def test_add_rating_invalid_song_id_format(client, auth_headers):
    """Test adding rating with malformed song ID."""
    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": "invalid-id", "rating": 5},
    )
    assert response.status_code == 404


def test_add_rating_boundary_values(client, auth_headers, sample_songs):
    """Test adding ratings with boundary values (1 and 5)."""
    song_id = str(sample_songs[0].id)

    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id, "rating": 1},
    )
    assert response.status_code == 201

    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id, "rating": 5},
    )
    assert response.status_code == 201


def test_add_rating_below_minimum(client, auth_headers, sample_songs):
    """Test adding rating below minimum value."""
    song_id = str(sample_songs[0].id)
    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id, "rating": 0},
    )
    assert response.status_code == 422


def test_add_rating_above_maximum(client, auth_headers, sample_songs):
    """Test adding rating above maximum value."""
    song_id = str(sample_songs[0].id)
    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id, "rating": 6},
    )
    assert response.status_code == 422


def test_add_rating_missing_song_id(client, auth_headers):
    """Test adding rating without song_id."""
    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"rating": 5},
    )
    assert response.status_code == 422


def test_add_rating_missing_rating(client, auth_headers, sample_songs):
    """Test adding rating without rating value."""
    song_id = str(sample_songs[0].id)
    response = client.post(
        "/api/v1/songs/ratings",
        headers=auth_headers,
        json={"song_id": song_id},
    )
    assert response.status_code == 422


def test_get_rating_stats_invalid_song_id(client, auth_headers):
    """Test getting rating stats with invalid song ID."""
    response = client.get("/api/v1/songs/invalid-id/ratings", headers=auth_headers)
    assert response.status_code == 404


def test_search_pagination_edge_cases(client, auth_headers, sample_songs):
    """Test search with pagination edge cases."""
    response = client.get("/api/v1/songs/search?message=Yousicians&page=1&page_size=1", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) <= 1

    response = client.get("/api/v1/songs/search?message=Yousicians&page=999&page_size=20", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 0


def test_login_empty_username(client, password_factory):
    """Test login with empty username."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "", "password": password_factory()},
    )
    assert response.status_code in [400, 401, 422]


def test_login_empty_password(client):
    """Test login with empty password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": ""},
    )
    assert response.status_code in [400, 401]


def test_register_duplicate_username(client, app):
    """Test registering with existing username."""
    response1 = client.post(
        "/api/v1/auth/register",
        json={"username": "newuser123", "password": "password123"},
    )
    assert response1.status_code == 201

    response2 = client.post(
        "/api/v1/auth/register",
        json={"username": "newuser123", "password": "password456"},
    )
    assert response2.status_code == 409


def test_register_short_password(client):
    """Test registration with password too short."""
    short_password = "x" * 5
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "password": short_password},
    )
    assert response.status_code == 422


def test_register_short_username(client, password_factory):
    """Test registration with username too short."""
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "ab", "password": password_factory()},
    )
    assert response.status_code == 422
