"""Test fixtures and configurations for the Festify test suite."""
from __future__ import annotations

import os

import pytest

# Ensure testing environment variables are configured before loading app
os.environ["FESTIFY_ENVIRONMENT"] = "testing"
os.environ["FESTIFY_SECRET_KEY"] = "test-secret-key-32-chars-long-abc-festify"
os.environ["FESTIFY_LLM_PROVIDER"] = "mock"
os.environ["FESTIFY_DATABASE_URL"] = "sqlite:///:memory:"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import create_app
from app.security import create_session_token

# Shared in-memory SQLite engine with StaticPool so memory is preserved across connections in test
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables in memory once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    """Provide a clean transactional database session per test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def app(db_session):
    """FastAPI test application with overridden database session."""
    application = create_app()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    application.dependency_overrides[get_db] = override_get_db
    return application


@pytest.fixture
def client(app):
    """FastAPI TestClient fixture."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def auth_headers():
    """Valid JWT Authorization header fixture."""
    token = create_session_token("test-session-123")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_wedding_payload():
    return {
        "title": "Aria & Thomas Vineyard Wedding",
        "event_type": "wedding",
        "total_budget": 28000.0,
        "guest_count": 120,
        "vibe_theme": "Modern Botanical Elegance",
        "event_date": "2027-06-18",
        "location": "Napa Valley, CA",
        "notes": "Outdoor ceremony and indoor banquet.",
    }


@pytest.fixture
def sample_birthday_payload():
    return {
        "title": "Marcus 40th Speakeasy Celebration",
        "event_type": "birthday",
        "total_budget": 6500.0,
        "guest_count": 40,
        "vibe_theme": "1920s Harlem Renaissance Speakeasy",
        "event_date": "2027-09-12",
        "location": "Chicago, IL",
        "notes": "Craft cocktails and jazz trio.",
    }


@pytest.fixture
def sample_community_payload():
    return {
        "title": "Oakridge Annual Harvest Gala",
        "event_type": "community",
        "total_budget": 45000.0,
        "guest_count": 750,
        "vibe_theme": "Autumn Lantern Harvest Market",
        "event_date": "2027-10-08",
        "location": "Oakridge Town Common, MA",
        "notes": "Food trucks, artisan booths, live bluegrass.",
    }
