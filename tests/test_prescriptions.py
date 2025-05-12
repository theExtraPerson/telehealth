import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app
from app import Base, get_db, create_app
from app.schemas import Prescription
import os

SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_prescription(test_db):
    response = client.post("/prescriptions/", json={"name": "Test Prescription", "dosage": "10mg"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test Prescription"
    assert response.json()["dosage"] == "10mg"

def test_read_prescriptions(test_db):
    client.post("/prescriptions/", json={"name": "Test Prescription 1", "dosage": "10mg"})
    client.post("/prescriptions/", json={"name": "Test Prescription 2", "dosage": "20mg"})
    response = client.get("/prescriptions/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_read_prescription(test_db):
    response = client.post("/prescriptions/", json={"name": "Test Prescription", "dosage": "10mg"})
    prescription_id = response.json()["id"]
    response = client.get(f"/prescriptions/{prescription_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Prescription"
    assert response.json()["dosage"] == "10mg"

def test_update_prescription(test_db):
    response = client.post("/prescriptions/", json={"name": "Test Prescription", "dosage": "10mg"})
    prescription_id = response.json()["id"]
    response = client.put(f"/prescriptions/{prescription_id}", json={"name": "Updated Prescription", "dosage": "20mg"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Prescription"
    assert response.json()["dosage"] == "20mg"

def test_delete_prescription(test_db):
    response = client.post("/prescriptions/", json={"name": "Test Prescription", "dosage": "10mg"})
    prescription_id = response.json()["id"]
    response = client.delete(f"/prescriptions/{prescription_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Prescription"
    response = client.get(f"/prescriptions/{prescription_id}")
    assert response.status_code == 404