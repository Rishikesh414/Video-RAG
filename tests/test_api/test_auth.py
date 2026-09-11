"""
Tests for authentication endpoints (login, register).
"""

import pytest


class TestAuthEndpoints:
    """Tests for /api/v1/auth/ endpoints."""

    def test_login_success(self, client):
        """Valid credentials should return 200 and access token."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "student@videorag.com", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "student@videorag.com"
        assert data["user"]["role"] == "student"

    def test_login_invalid_password(self, client):
        """Invalid password should return 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "student@videorag.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Non-existent email should return 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@videorag.com", "password": "password123"},
        )
        assert response.status_code == 401
