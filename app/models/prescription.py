from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    medication = db.Column(db.String, nullable=False)
    dosage = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=True)
    date_prescribed = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("Patient", back_populates="prescriptions")
    doctor = db.relationship("Doctor", back_populates="prescriptions")