def test_list_songs_empty(client, auth_headers):
    """Test listing songs when database is empty."""
    response = client.get("/api/v1/songs", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["data"] == []
    assert data["pagination"]["total"] == 0


def test_list_songs_with_data(client, auth_headers, sample_songs):
    """Test listing songs with pagination."""
    response = client.get("/api/v1/songs?page=1&page_size=2", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 2
    assert data["pagination"]["total"] == 3


def test_list_songs_requires_auth(client):
    """Test that listing songs requires authentication."""
    response = client.get("/api/v1/songs")
    assert response.status_code == 401
