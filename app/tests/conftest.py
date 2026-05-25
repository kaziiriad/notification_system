import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.sql.models import Base
from celery import Celery
from app.worker.tasks import celery_app as app
from unittest.mock import patch

# Add the project root to the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

@pytest.fixture(scope="function")
def test_db_session():
    """Create a test database session for integration tests."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="session")
def celery_config():
    """Configure Celery for testing."""
    return {
        "broker_url": "memory://",
        "result_backend": "cache+memory://",
        "task_always_eager": True,
        "task_eager_propagates": True,
    }

@pytest.fixture(scope="session")
def celery_app(celery_config):
    """Create a Celery app for testing."""
    app.conf.update(celery_config)
    return app

@pytest.fixture(scope="session")
def celery_worker_parameters():
    """Configure Celery worker for testing."""
    return {
        "perform_ping_check": False,
    }

@pytest.fixture(scope="session")
def celery_worker_pool():
    """Define the worker pool for testing."""
    return "solo"

@pytest.fixture(scope="session")
def celery_worker(celery_app, celery_worker_pool, celery_worker_parameters):
    """Start a Celery worker for integration tests."""
    # In eager mode, we don't need a real worker
    # The celery_worker fixture is provided by pytest-celery but we override it
    # since we're using eager mode for simplicity
    yield None

@pytest.fixture(scope="function")
def mock_db_session(test_db_session):
    """Mock the database session used by worker tasks to use test DB."""
    with patch('app.worker.tasks.SessionLocal', return_value=test_db_session):
        yield test_db_session
