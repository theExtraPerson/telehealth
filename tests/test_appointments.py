import json
from datetime import datetime, timedelta
import pytest

# Sample test data
TEST_APPOINTMENT = {
    "title": "Annual Checkup",
    "description": "Routine physical examination",
    "date": (datetime.now() + timedelta(days=1)).isoformat(),
    "patient_id": 1,
    "doctor_id": 1,
    "department": "General Medicine"
}

def test_create_appointment(client):
    """Test creating a new appointment"""
    response = client.post(
        "/appointments/",
        data=json.dumps(TEST_APPOINTMENT),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == TEST_APPOINTMENT['title']
    assert 'id' in data

def test_get_appointments(client):
    """Test retrieving all appointments"""
    # First create a test appointment
    client.post(
        "/appointments/",
        data=json.dumps(TEST_APPOINTMENT),
        content_type='application/json'
    )
    
    response = client.get("/appointments/")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_appointment(client):
    """Test retrieving a single appointment"""
    # Create and get ID
    create_resp = client.post(
        "/appointments/",
        data=json.dumps(TEST_APPOINTMENT),
        content_type='application/json'
    )
    appt_id = json.loads(create_resp.data)['id']
    
    response = client.get(f"/appointments/{appt_id}")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == TEST_APPOINTMENT['title']

def test_update_appointment(client):
    """Test updating an appointment"""
    # Create first
    create_resp = client.post(
        "/appointments/",
        data=json.dumps(TEST_APPOINTMENT),
        content_type='application/json'
    )
    appt_id = json.loads(create_resp.data)['id']
    
    # Update
    update_data = {**TEST_APPOINTMENT, "title": "Updated Checkup"}
    response = client.put(
        f"/appointments/{appt_id}",
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == "Updated Checkup"

def test_delete_appointment(client):
    """Test deleting an appointment"""
    # Create first
    create_resp = client.post(
        "/appointments/",
        data=json.dumps(TEST_APPOINTMENT),
        content_type='application/json'
    )
    appt_id = json.loads(create_resp.data)['id']
    
    # Delete
    response = client.delete(f"/appointments/{appt_id}")
    assert response.status_code == 204
    
    # Verify deletion
    get_resp = client.get(f"/appointments/{appt_id}")
    assert get_resp.status_code == 404

def test_get_nonexistent_appointment(client):
    """Test getting a non-existent appointment"""
    response = client.get("/appointments/999999")
    assert response.status_code == 404

def test_update_nonexistent_appointment(client):
    """Test updating a non-existent appointment"""
    response = client.put(
        "/appointments/999999",
        data=json.dumps(TEST_APPOINTMENT),
        content_type='application/json'
    )
    assert response.status_code == 404

def test_delete_nonexistent_appointment(client):
    """Test deleting a non-existent appointment"""
    response = client.delete("/appointments/999999")
    assert response.status_code == 404