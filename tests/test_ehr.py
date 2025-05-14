import pytest
from flask import url_for
from app import db
from app.models.medical_record import MedicalRecord, Prescription
from app.models.user import User

def test_create_medical_record(client, authenticated_doctor):
    """Test doctor creating a medical record"""
    patient = User.query.filter_by(role="patient").first()
    response = client.post(url_for("ehr.create_record"), json={
        "patient_id": patient.id,
        "diagnosis": "Hypertension",
        "treatment": "Lifestyle modification",
        "notes": "Follow up in 2 weeks"
    })
    
    assert response.status_code == 201
    record = MedicalRecord.query.first()
    assert record.diagnosis == "Hypertension"

def test_patient_access_own_records(client, authenticated_patient):
    """Test patient can access their own records"""
    # Create test record
    record = MedicalRecord(
        patient_id=authenticated_patient.id,
        doctor_id=1,
        diagnosis="Test Diagnosis"
    )
    db.session.add(record)
    db.session.commit()
    
    response = client.get(url_for("ehr.patient_records"))
    assert response.status_code == 200
    assert b"Test Diagnosis" in response.data

def test_doctor_access_patient_records(client, authenticated_doctor):
    """Test doctor can access patient records"""
    patient = User.query.filter_by(role="patient").first()
    record = MedicalRecord(
        patient_id=patient.id,
        doctor_id=authenticated_doctor.id,
        diagnosis="Shared Diagnosis"
    )
    db.session.add(record)
    db.session.commit()
    
    response = client.get(url_for("ehr.view_patient_records", patient_id=patient.id))
    assert response.status_code == 200
    assert b"Shared Diagnosis" in response.data

def test_create_prescription(client, authenticated_doctor):
    """Test creating a prescription"""
    patient = User.query.filter_by(role="patient").first()
    response = client.post(url_for("ehr.create_prescription"), json={
        "patient_id": patient.id,
        "medication": "Lisinopril 10mg",
        "dosage": "Once daily",
        "instructions": "Take with water",
        "duration": "30 days"
    })
    
    assert response.status_code == 201
    prescription = Prescription.query.first()
    assert prescription.medication == "Lisinopril 10mg"

def test_record_search(client, authenticated_doctor):
    """Test searching medical records"""
    # Create test records
    record1 = MedicalRecord(patient_id=1, doctor_id=1, diagnosis="Hypertension")
    record2 = MedicalRecord(patient_id=1, doctor_id=1, diagnosis="Diabetes")
    db.session.add_all([record1, record2])
    db.session.commit()
    
    response = client.get(url_for("ehr.search_records") + "?query=Diabetes")
    assert response.status_code == 200
    assert b"Diabetes" in response.data
    assert b"Hypertension" not in response.data