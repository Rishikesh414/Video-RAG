"""
Database Connection — PostgreSQL connection setup using SQLAlchemy.

Provides:
- Engine and session factory
- Dependency injection for FastAPI routes
- Session lifecycle management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.config import settings
from backend.app.models.database import Base


# ─── Engine ──────────────────────────────────────────────────────────

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# ─── Session Factory ─────────────────────────────────────────────────

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Dependency ──────────────────────────────────────────────────────

def get_db() -> Session:
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session after the request.

    Usage:
        @router.get("/example")
        async def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── Table Creation ──────────────────────────────────────────────────

def create_tables():
    """Create all database tables. Use for initial setup only."""
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables. USE WITH CAUTION."""
    Base.metadata.drop_all(bind=engine)
