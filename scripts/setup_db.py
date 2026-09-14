"""
Database Setup Script — dynamically creates all tables.

Usage:
    python scripts/setup_db.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import create_tables, engine


def main():
    """Create all database tables."""
    print("Setting up VideoRAG database...")
    print(f"   Database URL: {engine.url}")

    try:
        create_tables()
        print("All tables created successfully!")

        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n   Tables created: {', '.join(tables)}")

    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
