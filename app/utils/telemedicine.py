from app.models.telemedicine_session import TelemedicineSession
from datetime import datetime, timedelta
import uuid

def generate_telemedicine_link():
    """Generate a unique telemedicine session link"""
    return f"telemed-{uuid.uuid4().hex[:10]}"

def create_telemedicine_session(record_id: int, patient_id: int, doctor_id: int, platform: str):
    """Create a new telemedicine session record"""
    session = TelemedicineSession(
        session_uid=str(uuid.uuid4()),
        record_id=record_id,
        patient_id=patient_id,
        doctor_id=doctor_id,
        platform=platform,
        meeting_link=generate_telemedicine_link(),
        start_time=datetime.utcnow(),
        status='scheduled'
    )
    return session