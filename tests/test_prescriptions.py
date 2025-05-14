import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models.prescription import Prescription  
import os

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": os.environ.get('TEST_DATABASE_URI', 'sqlite:///:memory:'),
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })

    with app.app_context():
        db.create_all()
    
    yield app

    # Clean up after tests
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def init_db(app):
    """Initialize the database with test data."""
    with app.app_context():
        # Add any initial test data here if needed
        pass
    return db

def test_create_prescription(client, init_db):
    """Test creating a new prescription."""
    response = client.post("/prescriptions/", json={
        "name": "Test Prescription", 
        "dosage": "10mg"
    })
    assert response.status_code == 201
    assert response.json["name"] == "Test Prescription"
    assert response.json["dosage"] == "10mg"

    # Verify the record was actually created in the database
    with client.application.app_context():
        prescription = Prescription.query.first()
        assert prescription is not None
        assert prescription.name == "Test Prescription"

def test_read_prescriptions(client, init_db):
    """Test retrieving multiple prescriptions."""
    # Create test data
    test_data = [
        {"name": "Prescription 1", "dosage": "10mg"},
        {"name": "Prescription 2", "dosage": "20mg"}
    ]
    
    with client.application.app_context():
        for data in test_data:
            db.session.add(Prescription(**data))
        db.session.commit()

    response = client.get("/prescriptions/")
    assert response.status_code == 200
    assert len(response.json) == 2
    assert {p["name"] for p in response.json} == {"Prescription 1", "Prescription 2"}

def test_read_single_prescription(client, init_db):
    """Test retrieving a single prescription."""
    with client.application.app_context():
        # Create test prescription directly
        prescription = Prescription(name="Test Prescription", dosage="10mg")
        db.session.add(prescription)
        db.session.commit()
        prescription_id = prescription.id

    response = client.get(f"/prescriptions/{prescription_id}")
    assert response.status_code == 200
    assert response.json["name"] == "Test Prescription"
    assert response.json["dosage"] == "10mg"

def test_update_prescription(client, init_db):
    """Test updating a prescription."""
    with client.application.app_context():
        prescription = Prescription(name="Original", dosage="5mg")
        db.session.add(prescription)
        db.session.commit()
        prescription_id = prescription.id

    response = client.put(
        f"/prescriptions/{prescription_id}",
        json={"name": "Updated", "dosage": "10mg"}
    )
    assert response.status_code == 200
    assert response.json["name"] == "Updated"
    assert response.json["dosage"] == "10mg"

    # Verify the update in database
    with client.application.app_context():
        updated = Prescription.query.get(prescription_id)
        assert updated.name == "Updated"

def test_delete_prescription(client, init_db):
    """Test deleting a prescription."""
    with client.application.app_context():
        prescription = Prescription(name="To Delete", dosage="5mg")
        db.session.add(prescription)
        db.session.commit()
        prescription_id = prescription.id

    response = client.delete(f"/prescriptions/{prescription_id}")
    assert response.status_code == 204

    # Verify deletion
    with client.application.app_context():
        deleted = Prescription.query.get(prescription_id)
        assert deleted is None