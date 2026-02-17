"""
Database service using SQLAlchemy with SQLite.
Provides session management and initialization.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import Config


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


# Create engine and session factory
engine = create_engine(Config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """
    Initialize the database.
    Preferred: run `alembic upgrade head` for migration-based schema management.
    Fallback: create_all() for quick development when no migration history exists.
    """
    # Import models so they register with Base.metadata
    import models.lead  # noqa: F401
    import models.campaign  # noqa: F401
    import models.interaction  # noqa: F401
    import models.proposal  # noqa: F401
    import models.brand_asset  # noqa: F401
    import models.chat_message  # noqa: F401
    import models.agent_memory  # noqa: F401

    try:
        from alembic.config import Config as AlembicConfig
        from alembic import command
        import os

        alembic_cfg = AlembicConfig(os.path.join(os.path.dirname(os.path.dirname(__file__)), "alembic.ini"))
        command.upgrade(alembic_cfg, "head")
    except Exception:
        # Fallback to create_all if Alembic is not set up or fails
        Base.metadata.create_all(bind=engine)


def get_session():
    """
    Get a new database session.
    Usage:
        session = get_session()
        try:
            ... do work ...
            session.commit()
        finally:
            session.close()
    """
    return SessionLocal()
