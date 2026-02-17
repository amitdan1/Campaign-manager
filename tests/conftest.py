"""
Shared test fixtures.
Uses an in-memory SQLite database to avoid touching the real DB.
"""

import os
import pytest

# Force test database before any imports
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["FLASK_DEBUG"] = "false"

from app import app as flask_app  # noqa: E402
from services.database import Base, engine, init_db  # noqa: E402


@pytest.fixture(scope="session")
def app():
    """Create application for testing."""
    flask_app.config["TESTING"] = True
    flask_app.config["SERVER_NAME"] = "localhost"

    # Create all tables in the in-memory database
    Base.metadata.create_all(bind=engine)

    yield flask_app

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()
