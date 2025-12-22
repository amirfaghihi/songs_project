def test_login_success(client, test_user_credentials):
    """Test successful login returns JWT token."""
    response = client.post(
        "/api/v1/auth/login",
        json=test_user_credentials,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client, password_factory):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "wrong", "password": password_factory()},
    )
    assert response.status_code == 401


def test_login_missing_fields(client):
    """Test login with missing fields."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser"},
    )
    assert response.status_code == 422


def test_protected_route_without_token(client):
    """Test that protected routes require JWT token."""
    response = client.get("/api/v1/songs")
    assert response.status_code == 401


def test_protected_route_with_invalid_token(client):
    """Test that protected routes reject invalid tokens."""
    response = client.get(
        "/api/v1/songs",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_protected_route_with_valid_token(client, auth_headers):
    """Test that protected routes accept valid tokens."""
    response = client.get("/api/v1/songs", headers=auth_headers)
    assert response.status_code == 200
