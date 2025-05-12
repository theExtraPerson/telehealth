from datetime import datetime, timezone
from app import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    medication = db.Column(db.String, nullable=False)
    dosage = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=True)
    date_prescribed = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    patient = db.relationship("Patient", back_populates="prescriptions")
    doctor = db.relationship("Doctor", back_populates="prescriptions")
    medical_record = db.relationship("MedicalRecord", back_populates="prescriptions")

    def __repr__(self):
        return f"<Prescription(medication='{self.medication}', dosage='{self.dosage}', instructions='{self.instructions}')>"