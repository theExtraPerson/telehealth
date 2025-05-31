from datetime import datetime
from sqlalchemy import text, Index, Numeric, event
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, VARBINARY
from app import db
import uuid

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'

    # Primary key and identifiers
    id = db.Column(db.Integer, primary_key=True)
    record_uid = db.Column(UNIQUEIDENTIFIER, unique=True, nullable=False, 
                          default=uuid.uuid4, server_default=text('NEWID()'))  # For external reference
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
   

    # Visit information
    date_of_visit = db.Column(db.DateTime, nullable=False)
    visit_type = db.Column(db.String(50), nullable=False, 
                         server_default=text("'in-person'"))  # in-person, telemedicine, emergency
    facility_id = db.Column(db.Integer, db.ForeignKey('health_facilities.id'))  # Added facility reference
    
    # Clinical documentation
    description = db.Column(db.Text, nullable=False)  # Changed to Text for detailed notes
    diagnosis = db.Column(db.Text)  # Changed to Text
    diagnosis_code = db.Column(db.String(20))  # ICD-10 code
    treatment = db.Column(db.Text)  # Changed to Text
    procedures = db.Column(db.Text)  # Added for procedure documentation
    medications = db.Column(db.Text)  # Changed to Text
    allergies = db.Column(db.Text)  # Added allergy information
    vital_signs = db.Column(db.Text)  # JSON-formatted vital signs
    
    # Telemedicine specific
    is_telemedicine = db.Column(db.Boolean, nullable=False, 
                              server_default=text('0'))
    telemedicine_link = db.Column(db.String(255))
    telemedicine_duration = db.Column(db.Integer)  # Duration in minutes
    
    # Attachments and files
    file_path = db.Column(db.String(255))
    file_hash = db.Column(VARBINARY(64))  # For file integrity verification
    document_type = db.Column(db.String(50))  # report, image, lab_result, etc.
    
    # Audit and metadata
    created_at = db.Column(db.DateTime, nullable=False, 
                         server_default=text('GETDATE()'))
    last_updated = db.Column(db.DateTime, nullable=False, 
                           server_default=text('GETDATE()'), 
                           onupdate=text('GETDATE()'))
    is_confidential = db.Column(db.Boolean, server_default=text('0'))
    record_status = db.Column(db.String(20), nullable=False, 
                            server_default=text("'active'"))  # active, amended, voided
    
    # Relationships
    patient = db.relationship("User", foreign_keys=[patient_id], 
                            back_populates="medical_records_as_patient")
    doctor = db.relationship("User", foreign_keys=[doctor_id], 
                           back_populates="medical_records_as_doctor")
    facility = db.relationship("HealthFacility")  # Added
    access_records = db.relationship("MedicalRecordAccess", 
                                   back_populates="record",
                                   cascade="all, delete-orphan")
    prescriptions = db.relationship("Prescription", 
                                  back_populates="medical_record")
    lab_results = db.relationship("LabResult", 
                                 back_populates="medical_record")  # Added
    

    def __repr__(self):
        return f"<MedicalRecord {self.record_uid} for patient {self.patient_id}>"

    def to_dict(self):
        """HIPAA-compliant serialization"""
        return {
            'record_uid': str(self.record_uid),
            'date_of_visit': self.date_of_visit.isoformat(),
            'visit_type': self.visit_type,
            'description': self.description,
            'diagnosis': self.diagnosis,
            'diagnosis_code': self.diagnosis_code,
            'treatment': self.treatment,
            'is_telemedicine': self.is_telemedicine,
            'created_at': self.created_at.isoformat(),
            'record_status': self.record_status
        }

    def get_redacted_dict(self):
        """For limited access views"""
        data = self.to_dict()
        if self.is_confidential:
            data['description'] = "CONFIDENTIAL - ACCESS RESTRICTED"
            data['diagnosis'] = "CONFIDENTIAL - ACCESS RESTRICTED"
            data['treatment'] = "CONFIDENTIAL - ACCESS RESTRICTED"
        return data

    __table_args__ = (
        Index('ix_medical_records_patient', 'patient_id'),
        Index('ix_medical_records_doctor', 'doctor_id'),
        Index('ix_medical_records_date', 'date_of_visit'),
        Index('ix_medical_records_diagnosis', 'diagnosis_code'),
        Index('ix_medical_records_telemedicine', 'is_telemedicine'),
        Index('ix_medical_records_facility', 'facility_id'),
    )


class MedicalRecordAccess(db.Model):
    __tablename__ = 'medical_record_access'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    accessor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Renamed from doctor_id
    granted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    granted_at = db.Column(db.DateTime, nullable=False, 
                         server_default=text('GETDATE()'))
    access_level = db.Column(db.String(20), nullable=False, 
                           server_default=text("'view'"))  # view, edit, full
    expires_at = db.Column(db.DateTime)
    purpose = db.Column(db.String(255), nullable=False)  # Required for HIPAA compliance
    is_emergency_access = db.Column(db.Boolean, server_default=text('0'))
    
    # Relationships
    record = db.relationship("MedicalRecord", back_populates="access_records")
    accessor = db.relationship("User", foreign_keys=[accessor_id])  # Renamed from doctor
    granter = db.relationship("User", foreign_keys=[granted_by])
    
    def is_active(self):
        return self.expires_at is None or self.expires_at > datetime.utcnow()

    __table_args__ = (
        Index('ix_access_record_user', 'record_id', 'accessor_id'),
        Index('ix_access_granted_at', 'granted_at'),
        Index('ix_access_expiration', 'expires_at'),
    )


# Supporting models
class HealthFacility(db.Model):
    """For tracking where care was provided"""
    __tablename__ = 'health_facilities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    facility_type = db.Column(db.String(50))  # hospital, clinic, lab, etc.
    address = db.Column(db.Text)
    is_telemedicine_capable = db.Column(db.Boolean, server_default=text('0'))


class LabResult(db.Model):
    """For tracking lab results associated with records"""
    __tablename__ = 'lab_results'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    result_value = db.Column(db.String(100))
    result_units = db.Column(db.String(20))
    reference_range = db.Column(db.String(100))
    performed_at = db.Column(db.DateTime, server_default=text('GETDATE()'))
    
    medical_record = db.relationship("MedicalRecord", back_populates="lab_results")


class MedicalRecordAuditLog(db.Model):
    __tablename__ = 'medical_record_audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'view', 'create', 'update', 'delete', 'share'
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    record = db.relationship("MedicalRecord", backref="medical_record_audit_logs")
    user = db.relationship("User")

    def __repr__(self):
        return f"<MedicalRecordAuditLog {self.id} {self.action} by {self.user_id}>"