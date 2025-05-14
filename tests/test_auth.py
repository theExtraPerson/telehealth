import pytest
from flask import url_for, session, get_flashed_messages
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models.user import User

@pytest.fixture
def test_user(app):
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
    return user


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": True,  # Disable CSRF for testing
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })

    with app.app_context():
        db.create_all()
        # Create test user
        hashed_password = generate_password_hash("testpassword")
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hashed_password,
            role="patient"
        )
        db.session.add(user)
        db.session.commit()

    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_register_page_loads(client):
    """Test that the registration page loads successfully."""
    response = client.get(url_for("auth.register"))
    assert response.status_code == 200
    assert b"Register" in response.data

def test_successful_registration(client):
    """Test successful user registration."""
    response = client.post(url_for("auth.register"), data={
        "username": "newuser",
        "email": "new@example.com",
        "password": "newpassword",
        "confirm_password": "newpassword",
        "role": "patient"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Login" in response.data  # Should redirect to login page
    messages = [msg for msg in get_flashed_messages() if "success" in msg]
    assert len(messages) == 1

def test_duplicate_registration(client):
    """Test registration with existing username."""
    response = client.post(url_for("auth.register"), data={
        "username": "testuser",  # Already exists
        "email": "test@example.com",
        "password": "testpassword",
        "confirm_password": "testpassword",
        "role": "patient"
    })
    
    assert response.status_code == 200
    assert b"Username already exists" in response.data

def test_login_page_loads(client):
    """Test that the login page loads successfully."""
    response = client.get(url_for("auth.login"))
    assert response.status_code == 200
    assert b"Login" in response.data

def test_successful_login(client):
    """Test successful user login."""
    response = client.post(url_for("auth.login"), data={
        "username": "testuser",
        "password": "testpassword",
        "role": "patient"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Dashboard" in response.data  # Should redirect to dashboard
    messages = [msg for msg in get_flashed_messages() if "success" in msg]
    assert len(messages) == 1

def test_failed_login(client):
    """Test failed login attempt."""
    response = client.post(url_for("auth.login"), data={
        "username": "testuser",
        "password": "wrongpassword",
        "role": "patient"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Login" in response.data  # Should stay on login page
    messages = [msg for msg in get_flashed_messages() if "error" in msg]
    assert len(messages) == 1

def test_logout(client):
    """Test user logout functionality."""
    # First login
    client.post(url_for("auth.login"), data={
        "username": "testuser",
        "password": "testpassword",
        "role": "patient"
    })
    
    # Then logout
    response = client.get(url_for("auth.logout"), follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Login" in response.data  # Should redirect to login page

def test_redirect_to_dashboard(client):
    """Test dashboard redirection based on role."""
    # Test patient redirect
    client.post(url_for("auth.login"), data={
        "username": "testuser",
        "password": "testpassword",
        "role": "patient"
    })
    response = client.get(url_for("user_dashboard.dashboard"))
    assert response.status_code == 200

    # Add similar tests for doctor and admin roles
    # You'll need to create test users for these roles in the fixture

def test_protected_route_access(client):
    """Test that protected routes require authentication."""
    response = client.get(url_for("user_dashboard.dashboard"), follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data  # Should redirect to login