from datetime import datetime, timezone
from sqlalchemy.orm import relationship
from app import db

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_of_visit = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String, nullable=False)
    diagnosis = db.Column(db.String)
    treatment = db.Column(db.String)
    medications = db.Column(db.String)
    notes = db.Column(db.String)
    doctor_name = db.Column(db.String, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String)
    is_telemedicine = db.Column(db.Boolean, default=False)
    telemedicine_link = db.Column(db.String)
    uploaded_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    last_updated = db.Column(db.DateTime, onupdate=datetime.now(timezone.utc))

    patient = db.relationship("User", foreign_keys=[patient_id], back_populates="medical_records_as_patient")
    doctor = db.relationship("User", foreign_keys=[doctor_id], back_populates="medical_records_as_doctor")
    access_records = db.relationship("MedicalRecordAccess", back_populates="record", cascade="all, delete-orphan")
    prescriptions = db.relationship("Prescription", back_populates="medical_record")

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'date_of_visit': self.date_of_visit.isoformat(),
            'description': self.description,
            'diagnosis': self.diagnosis,
            'treatment': self.treatment,
            'medications': self.medications,
            'doctor_name': self.doctor_name,
            'is_telemedicine': self.is_telemedicine,
            'uploaded_at': self.uploaded_at.isoformat(),
            'file_path': self.file_path
        }

    def __repr__(self):
        return f"<MedicalRecord(patient_id={self.patient_id}, date={self.date_of_visit}, doctor={self.doctor_name})>"

class MedicalRecordAccess(db.Model):
    __tablename__ = 'medical_record_access'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    granted_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    access_level = db.Column(db.String(20), default='view')  # 'view', 'edit', 'full'
    expires_at = db.Column(db.DateTime)
    
    record = relationship("MedicalRecord", back_populates="access_records")
    doctor = relationship("User", foreign_keys=[doctor_id])
    granter = relationship("User", foreign_keys=[granted_by])