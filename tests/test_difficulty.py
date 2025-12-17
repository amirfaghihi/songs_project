def test_average_difficulty_all(client, auth_headers, sample_songs):
    """Test average difficulty for all songs."""
    response = client.get("/api/v1/songs/difficulty/average", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    expected_avg = (14.6 + 9.1 + 15.0) / 3
    assert abs(data["average_difficulty"] - expected_avg) < 0.01
    assert data["level"] is None


def test_average_difficulty_by_level(client, auth_headers, sample_songs):
    """Test average difficulty filtered by level."""
    response = client.get("/api/v1/songs/difficulty/average?level=13", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    expected_avg = (14.6 + 15.0) / 2
    assert abs(data["average_difficulty"] - expected_avg) < 0.01
    assert data["level"] == 13


def test_average_difficulty_requires_auth(client):
    """Test that average difficulty requires authentication."""
    response = client.get("/api/v1/songs/difficulty/average")
    assert response.status_code == 401


