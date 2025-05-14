import pytest
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        # Create test users
        patient = User(
            username="testpatient",
            email="patient@example.com",
            password_hash=generate_password_hash("testpass"),
            role="patient"
        )
        doctor = User(
            username="testdoctor",
            email="doctor@example.com",
            password_hash=generate_password_hash("testpass"),
            role="doctor"
        )
        db.session.add_all([patient, doctor])
        db.session.commit()

    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticated_patient(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 1  # Assuming patient is first user
    yield

@pytest.fixture
def authenticated_doctor(client):
    with client.session_transaction() as sess:
        sess["user_id"] = 2  # Assuming doctor is second user
    yield