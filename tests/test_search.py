def test_search_songs_by_artist(client, auth_headers, sample_songs):
    """Test searching songs by artist name."""
    response = client.get("/api/v1/songs/search?message=Fastfinger", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 1
    assert data["data"][0]["artist"] == "Mr Fastfinger"
    assert data["message"] == "Fastfinger"


def test_search_songs_by_title(client, auth_headers, sample_songs):
    """Test searching songs by title."""
    response = client.get("/api/v1/songs/search?message=kennel", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["data"]) == 1
    assert "Kennel" in data["data"][0]["title"]


def test_search_songs_missing_message(client, auth_headers):
    """Test search without message parameter."""
    response = client.get("/api/v1/songs/search", headers=auth_headers)
    assert response.status_code == 400


def test_search_songs_requires_auth(client):
    """Test that search requires authentication."""
    response = client.get("/api/v1/songs/search?message=test")
    assert response.status_code == 401


