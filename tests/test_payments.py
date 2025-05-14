import pytest
from flask import url_for, session, get_flashed_messages
from app import db
from app.models.payments import Payment
from app.models.user import User
from datetime import datetime, timedelta

def test_payment_processing(client, authenticated_patient):
    """Test successful payment processing"""
    response = client.post(url_for("payments.process_payment"), json={
        "amount": 100.00,
        "card_number": "4111111111111111",
        "expiry_date": "12/25",
        "cvv": "123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert Payment.query.count() == 1

def test_payment_history_access(client, authenticated_patient):
    """Test patient can access their payment history"""
    # Create test payments
    payment1 = Payment(patient_id=authenticated_patient.id, amount=100.00, status="completed")
    payment2 = Payment(patient_id=authenticated_patient.id, amount=150.00, status="completed")
    db.session.add_all([payment1, payment2])
    db.session.commit()
    
    response = client.get(url_for("payments.payment_history"))
    assert response.status_code == 200
    assert b"100.00" in response.data
    assert b"150.00" in response.data

def test_payment_failure_invalid_card(client, authenticated_patient):
    """Test payment failure with invalid card"""
    response = client.post(url_for("payments.process_payment"), json={
        "amount": 100.00,
        "card_number": "4111111111111112",  # Invalid test number
        "expiry_date": "12/25",
        "cvv": "123"
    })
    
    assert response.status_code == 400
    assert "error" in response.json

def test_refund_processing(client, authenticated_doctor):
    """Test doctor-initiated refund"""
    # Create completed payment
    payment = Payment(patient_id=1, amount=100.00, status="completed")
    db.session.add(payment)
    db.session.commit()
    
    response = client.post(url_for("payments.process_refund", payment_id=payment.id))
    assert response.status_code == 200
    assert Payment.query.get(payment.id).status == "refunded"

@pytest.fixture
def authenticated_patient(client):
    """Fixture for logged-in patient"""
    user = User.query.filter_by(role="patient").first()
    with client.session_transaction() as sess:
        sess["user_id"] = user.id
    yield user

@pytest.fixture
def authenticated_doctor(client):
    """Fixture for logged-in doctor"""
    user = User(
        username="testdoctor",
        email="doctor@example.com",
        password_hash="hashed",
        role="doctor"
    )
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["user_id"] = user.id
    yield user