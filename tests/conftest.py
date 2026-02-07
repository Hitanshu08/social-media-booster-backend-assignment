"""Pytest fixtures for the Social Booster test suite.

A session-scoped PostgreSQL test database is used.  The DB schema SQL is
executed once per session so that the custom enum types, triggers, and
indexes exist.  Each test runs inside a rolled-back transaction to keep
tests isolated without the overhead of recreating tables every time.
"""

import os

import pytest

from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    """Create the Flask application configured for testing."""
    app = create_app("testing")

    with app.app_context():
        # Bootstrap the database from the SQL schema file so PostgreSQL
        # enum types, triggers and indexes are all present.
        schema_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "db-schema.sql"
        )
        with open(schema_path, "r") as fh:
            sql = fh.read()

        with _db.engine.connect() as conn:
            conn.execute(_db.text(sql))
            conn.commit()

    yield app


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_tables(app):
    """Truncate all data between tests for full isolation."""
    yield
    with app.app_context():
        _db.session.execute(_db.text("DELETE FROM campaign_insights"))
        _db.session.execute(_db.text("DELETE FROM campaigns"))
        _db.session.commit()


def make_campaign_payload(**overrides):
    """Helper to build a valid campaign creation payload."""
    defaults = {
        "name": "Test Campaign",
        "status": "draft",
        "platform": "facebook",
        "budget": 1000.00,
        "startDate": "2025-01-01",
        "endDate": "2025-12-31",
        "description": "A test campaign for unit tests",
        "targetAudience": "Adults 25-45",
    }
    defaults.update(overrides)
    return defaults
