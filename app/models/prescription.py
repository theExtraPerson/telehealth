from datetime import datetime
from sqlalchemy import text
from app import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    medication = db.Column(db.String(255), nullable=False)  # Added explicit length
    dosage = db.Column(db.String(100), nullable=False)     # Added explicit length
    instructions = db.Column(db.Text)                     # Changed to Text for longer content
    date_prescribed = db.Column(db.DateTime, nullable=False, 
                               server_default=text('GETDATE()'))  # SQL Server specific default
    status = db.Column(db.String(20), server_default=text("'active'"))  # Added status field

    # Relationships
    patient = db.relationship("Patient", foreign_keys=[patient_id], back_populates="prescriptions")
    doctor = db.relationship("Doctor", foreign_keys=[doctor_id], back_populates="prescriptions")
    medical_record = db.relationship("MedicalRecord", back_populates="prescriptions")
    status_changes = db.relationship("PrescriptionStatusChange", 
                                   back_populates="prescription",
                                   cascade="all, delete-orphan")
   
    def __repr__(self):
        return f"<Prescription(id={self.id}, medication='{self.medication}')>"

    __table_args__ = (
        db.Index('ix_prescription_patient', 'patient_id'),
        db.Index('ix_prescription_doctor', 'doctor_id'),
        db.Index('ix_prescription_medication', 'medication'),
    )

class PrescriptionStatusChange(db.Model):
    __tablename__ = 'prescription_status_changes'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=False)
    from_status = db.Column(db.String(20), nullable=True)  # Nullable for initial status
    to_status = db.Column(db.String(20), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_at = db.Column(db.DateTime, nullable=False, 
                         server_default=text('GETDATE()'))  # SQL Server timestamp
    notes = db.Column(db.Text)  # Added for audit purposes
    
    # Relationships
    prescription = db.relationship("Prescription", back_populates="status_changes")
    user = db.relationship("User")  # Reference to who made the change

    def __repr__(self):
        return f"<StatusChange(prescription={self.prescription_id}, status='{self.to_status}')>"

    __table_args__ = (
        db.Index('ix_status_change_prescription', 'prescription_id'),
        db.Index('ix_status_change_timestamp', 'changed_at'),
    )