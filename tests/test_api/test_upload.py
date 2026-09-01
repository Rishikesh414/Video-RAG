"""
Tests for the upload API endpoints.
"""

import pytest


class TestUploadEndpoints:
    """Tests for /api/v1/upload/ endpoints."""

    def test_upload_video_requires_auth(self, client):
        """Uploading a video without auth should return 401."""
        response = client.post("/api/v1/upload/video")
        assert response.status_code == 401

    def test_upload_pdf_requires_auth(self, client):
        """Uploading a PDF without auth should return 401."""
        response = client.post("/api/v1/upload/pdf")
        assert response.status_code == 401

    def test_list_uploads_requires_auth(self, client):
        """Listing uploads without auth should return 401."""
        response = client.get("/api/v1/upload/list")
        assert response.status_code == 401
