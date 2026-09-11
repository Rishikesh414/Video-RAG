"""
Database Connection — SQLite / PostgreSQL connection setup using SQLAlchemy.

Provides:
- Engine and session factory (auto-configured for SQLite or PostgreSQL)
- Dependency injection for FastAPI routes (get_db)
- Session lifecycle management
- Table creation and seeding functions
"""

import sys
from pathlib import Path
from typing import Generator
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

# Ensure project root and backend dir are in sys.path
_current_file = Path(__file__).resolve()
_project_root = _current_file.parent.parent
_backend_dir = _project_root / "backend"

for _p in [str(_project_root), str(_backend_dir)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from app.config import settings
    from app.models.database import Base
except ImportError:
    from backend.app.config import settings
    from backend.app.models.database import Base


# ─── Engine Configuration ────────────────────────────────────────────

database_url = settings.DATABASE_URL

connect_args = {}
engine_kwargs = {"echo": False}

if database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    engine_kwargs.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
    })

engine = create_engine(
    database_url,
    connect_args=connect_args,
    **engine_kwargs,
)

# ─── Session Factory ─────────────────────────────────────────────────

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── FastAPI Dependency ──────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and closes it after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Table Creation & Initialization ─────────────────────────────────

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables. USE WITH CAUTION."""
    Base.metadata.drop_all(bind=engine)


def init_db(seed: bool = True):
    """
    Initialize the database file/server:
    1. Creates all tables (users, uploads, chat_messages)
    2. Seeds initial default accounts (student, faculty, admin) if seed=True
    """
    create_tables()
    if seed:
        from database.seed.seed_data import seed_users
        seed_users()
