from datetime import datetime
from app import db

class TelemedicineSession(db.Model):
    __tablename__ = 'telemedicine_sessions'

    id = db.Column(db.Integer, primary_key=True)
    session_uid = db.Column(db.String(36), unique=True, nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # 'Zoom', 'Teams', etc.
    meeting_link = db.Column(db.String(255), nullable=False)
    meeting_password = db.Column(db.String(50))
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in minutes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, in-progress, completed, cancelled
    recording_url = db.Column(db.String(255))
    notes = db.Column(db.Text)

    # Relationships
    record = db.relationship("MedicalRecord", backref="telemedicine_sessions")
    patient = db.relationship("Patient", foreign_keys=[patient_id])
    doctor = db.relationship("Doctor", foreign_keys=[doctor_id])

    def __repr__(self):
        return f"<TelemedicineSession {self.session_uid} ({self.status})>"