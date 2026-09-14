"""
Tests for authentication endpoints (login, register) with dynamic registration.
"""

import pytest


class TestAuthEndpoints:
    """Tests for dynamic /api/v1/auth/ endpoints."""

    def test_register_and_login_success(self, client):
        """Dynamic user registration followed by successful authentication."""
        reg_payload = {
            "name": "Dynamic Student",
            "email": "dynamic_student@test.com",
            "password": "secure_password_123",
            "role": "student",
        }

        # 1. Dynamic registration
        reg_response = client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_response.status_code == 201
        reg_data = reg_response.json()
        assert "user_id" in reg_data

        # 2. Dynamic login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": "dynamic_student@test.com", "password": "secure_password_123"},
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"
        assert login_data["user"]["email"] == "dynamic_student@test.com"
        assert login_data["user"]["role"] == "student"

    def test_login_invalid_password(self, client):
        """Invalid password should return 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "dynamic_student@test.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Non-existent email should return 401."""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent_user_999@test.com", "password": "anypassword"},
        )
        assert response.status_code == 401

    def test_duplicate_registration_rejected(self, client):
        """Attempting to register with an existing email should return 400."""
        duplicate_payload = {
            "name": "Duplicate Student",
            "email": "dynamic_student@test.com",
            "password": "another_password",
            "role": "student",
        }
        response = client.post("/api/v1/auth/register", json=duplicate_payload)
        assert response.status_code == 400
