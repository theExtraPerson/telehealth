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
    status_changes = db.relationship("PrescriptionStatusChange", back_populates="prescription", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prescription(medication='{self.medication}', dosage='{self.dosage}', instructions='{self.instructions}')>"
    

class PrescriptionStatusChange(db.Model):
    __tablename__ = 'prescription_status_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'))
    from_status = db.Column(db.String(20))
    to_status = db.Column(db.String(20))
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    changed_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    prescription = db.relationship("Prescription", back_populates="status_changes")
    
    def __repr__(self):
        return f"<PrescriptionStatusChange(prescription_id={self.prescription_id}, status={self.to_status})>"