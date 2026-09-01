"""
Shared pytest fixtures for the VideoRAG test suite.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    """Provide a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """
    Provide authenticated headers with a test JWT token.
    TODO: Generate a real token from the auth service for integration tests.
    """
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def sample_question():
    """Provide a sample student question for query tests."""
    return {
        "question": "Explain the concept of binary search from the lecture.",
        "module": "M1",
    }
