"""
CORS middleware configuration.

Note: CORS is already configured in main.py using FastAPI's built-in middleware.
This module provides additional utilities or custom CORS logic if needed.
"""

from app.config import settings


def get_cors_config() -> dict:
    """
    Return CORS configuration dictionary.
    Can be extended for per-route or per-environment CORS rules.
    """
    return {
        "allow_origins": settings.CORS_ORIGINS,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
