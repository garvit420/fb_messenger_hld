"""Tests for user profile endpoints."""

from fastapi.testclient import TestClient


class TestGetCurrentUser:
    """Tests for getting current user profile."""

    def test_get_current_user_success(self, client: TestClient, auth_headers, test_user):
        """Test getting current user profile."""
        response = client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert data["display_name"] == test_user.display_name

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without auth fails."""
        response = client.get("/api/users/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token fails."""
        response = client.get("/api/users/me", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401


class TestUpdateCurrentUser:
    """Tests for updating current user profile."""

    def test_update_display_name(self, client: TestClient, auth_headers, test_user):
        """Test updating display name."""
        response = client.put(
            "/api/users/me", headers=auth_headers, json={"display_name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated Name"

    def test_update_avatar_url(self, client: TestClient, auth_headers, test_user):
        """Test updating avatar URL."""
        response = client.put(
            "/api/users/me",
            headers=auth_headers,
            json={"avatar_url": "https://example.com/avatar.png"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["avatar_url"] == "https://example.com/avatar.png"

    def test_update_both_fields(self, client: TestClient, auth_headers, test_user):
        """Test updating both display name and avatar URL."""
        response = client.put(
            "/api/users/me",
            headers=auth_headers,
            json={"display_name": "New Name", "avatar_url": "https://example.com/new-avatar.png"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "New Name"
        assert data["avatar_url"] == "https://example.com/new-avatar.png"

    def test_update_unauthorized(self, client: TestClient):
        """Test updating profile without auth fails."""
        response = client.put("/api/users/me", json={"display_name": "Hacker"})
        assert response.status_code == 401


class TestUpdateUserStatus:
    """Tests for updating user online status."""

    def test_set_online(self, client: TestClient, auth_headers, test_user):
        """Test setting user as online."""
        response = client.put(
            "/api/users/me/status", headers=auth_headers, json={"is_online": True}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_online"] is True
        assert data["last_seen_at"] is not None

    def test_set_offline(self, client: TestClient, auth_headers, test_user):
        """Test setting user as offline."""
        response = client.put(
            "/api/users/me/status", headers=auth_headers, json={"is_online": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_online"] is False

    def test_update_status_unauthorized(self, client: TestClient):
        """Test updating status without auth fails."""
        response = client.put("/api/users/me/status", json={"is_online": True})
        assert response.status_code == 401


class TestGetUserById:
    """Tests for getting user by ID."""

    def test_get_user_by_id_success(self, client: TestClient, auth_headers, test_user, test_user2):
        """Test getting another user by ID."""
        response = client.get(f"/api/users/{test_user2.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user2.id
        assert data["username"] == test_user2.username

    def test_get_user_by_id_not_found(self, client: TestClient, auth_headers):
        """Test getting nonexistent user fails."""
        response = client.get("/api/users/99999", headers=auth_headers)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    def test_get_user_by_id_unauthorized(self, client: TestClient, test_user2):
        """Test getting user without auth fails."""
        response = client.get(f"/api/users/{test_user2.id}")
        assert response.status_code == 401
