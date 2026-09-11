"""
Shared pytest fixtures for the VideoRAG test suite.
"""

import sys
from pathlib import Path
import pytest

# Ensure backend directory is on sys.path
backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)


@pytest.fixture
def client():
    """Provide a FastAPI test client (lazy loaded)."""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)
    except Exception as e:
        pytest.skip(f"FastAPI or backend dependencies not fully available: {e}")


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
