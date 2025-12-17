def test_health(client):
    """Test health check endpoint (no auth required)."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


