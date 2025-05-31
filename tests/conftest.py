import pytest
from app import create_app
from flask.testing import FlaskClient

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config['TESTING'] = True
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()