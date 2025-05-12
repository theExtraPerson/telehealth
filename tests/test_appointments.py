from fastapi.testclient import TestClient
from ..app import create_app
# from app.api.appointments import app, appointments, Appointment
from datetime import datetime

app = create_app()

client = TestClient(app)

def test_create_appointment():
    response = client.post("/appointments/", json={
        "id": 1,
        "title": "Test Appointment",
        "description": "This is a test appointment",
        "date": datetime.now().isoformat()
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test Appointment"

def test_get_appointments():
    response = client.get("/appointments/")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_appointment():
    response = client.get("/appointments/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_update_appointment():
    response = client.put("/appointments/1", json={
        "id": 1,
        "title": "Updated Appointment",
        "description": "This is an updated test appointment",
        "date": datetime.now().isoformat()
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Appointment"

def test_delete_appointment():
    response = client.delete("/appointments/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_nonexistent_appointment():
    response = client.get("/appointments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"

def test_update_nonexistent_appointment():
    response = client.put("/appointments/999", json={
        "id": 999,
        "title": "Nonexistent Appointment",
        "description": "This appointment does not exist",
        "date": datetime.now().isoformat()
    })
    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"

def test_delete_nonexistent_appointment():
    response = client.delete("/appointments/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Appointment not found"