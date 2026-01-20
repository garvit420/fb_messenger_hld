"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient


class TestRegistration:
    """Tests for user registration."""

    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "password123",
                "display_name": "New User"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["display_name"] == "New User"
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "testuser@example.com",  # Same as test_user
                "username": "differentuser",
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client: TestClient, test_user):
        """Test registration with duplicate username fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "different@example.com",
                "username": "testuser",  # Same as test_user
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "username": "validuser",
                "password": "password123"
            }
        )
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Test registration with short password fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "valid@example.com",
                "username": "validuser",
                "password": "short"
            }
        )
        assert response.status_code == 422

    def test_register_short_username(self, client: TestClient):
        """Test registration with short username fails."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "valid@example.com",
                "username": "ab",  # Less than 3 chars
                "password": "password123"
            }
        )
        assert response.status_code == 422


class TestLogin:
    """Tests for user login."""

    def test_login_success(self, client: TestClient, test_user):
        """Test successful login."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_user):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user fails."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_updates_online_status(self, client: TestClient, db_session, test_user):
        """Test that login updates user's online status."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200

        # Refresh the user from database
        db_session.refresh(test_user)
        assert test_user.is_online is True
        assert test_user.last_seen_at is not None
