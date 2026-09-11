"""
Tests for the query API endpoints.
"""

import pytest


class TestQueryEndpoints:
    """Tests for /api/v1/query/ endpoints."""

    def test_ask_question_requires_auth(self, client):
        """Asking a question without auth should return 401."""
        response = client.post(
            "/api/v1/query/ask",
            json={"question": "What is binary search?"},
        )
        assert response.status_code == 401

    def test_get_clip_requires_auth(self, client):
        """Fetching a video clip without auth should return 401."""
        response = client.get("/api/v1/query/clip/test-id")
        assert response.status_code == 401

    def test_health_check(self, client):
        """Health check endpoint should return 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
