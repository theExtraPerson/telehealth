from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app import db

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_of_visit = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    doctor_name = db.Column(db.String, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    patient = db.relationship("User", foreign_keys=[patient_id], back_populates="medical_records_as_patient")
    doctor = db.relationship("User", foreign_keys=[doctor_id], back_populates="medical_records_as_doctor")
    access_records = db.relationship("MedicalRecordAccess", back_populates="record", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date_of_birth': self.date_of_birth,
            'description': self.description,
            'doctor_name': self.doctor_name,
            'date': self.date,
        }

    def __repr__(self):
        return f"<MedicalRecord(patient_id={self.patient_id}, description={self.description}, doctor={self.doctor_name})>"
