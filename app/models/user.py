from flask import json
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import text
from app import db
from werkzeug.security import generate_password_hash, check_password_hash 

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)  # Added length
    email = db.Column(db.String(255), unique=True, nullable=False)   # Added length
    password_hash = db.Column(db.String(255), nullable=False)        # Added length
    is_active = db.Column(db.Boolean, default=True, server_default=text('1'))
    is_doctor = db.Column(db.Boolean, default=False, server_default=text('0'))
    is_patient = db.Column(db.Boolean, default=True, server_default=text('1'))
    is_admin = db.Column(db.Boolean, default=False, server_default=text('0'))
    role = db.Column(db.String(20), nullable=False, server_default='patient')
    user_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, server_default=text('GETDATE()'))
    created_appointments = db.relationship("Appointment", foreign_keys="[Appointment.creator_id]", back_populates="creator", lazy="dynamic", cascade="all, delete-orphan")

    # Relationships
    medical_records_as_patient = db.relationship(
        "MedicalRecord",
        foreign_keys="[MedicalRecord.patient_id]",
        back_populates="patient"
    )
    medical_records_as_doctor = db.relationship(
        "MedicalRecord",
        foreign_keys="[MedicalRecord.doctor_id]",
        back_populates="doctor"
    )
    appointments = db.relationship(
        "Appointment",
        foreign_keys="[Appointment.creator_id]",
        back_populates="creator",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

class Doctor(User):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    specialty_id = db.Column(db.String(50), db.ForeignKey('specialties.id'), nullable=False)  # Added length
    license_number = db.Column(db.String(50), unique=True, nullable=False)  # Added length
    bio = db.Column(db.String(1000))  # Added length
    schedule = db.Column(db.Text)
    languages_spoken = db.Column(db.String(255))
    gender = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    medical_license = db.Column(db.String(100))
    conditions_treated = db.Column(db.Text)
    available_days = db.Column(db.String(255))  # For SQL Server, consider JSON or separate table
    photo = db.Column(db.String(255))  # Save filename or cloud path
    whatsapp = db.Column(db.Boolean, default=False, server_default=text('0'))
    phone_call = db.Column(db.Boolean, default=False, server_default=text('0'))
    video_call = db.Column(db.Boolean, default=False, server_default=text('0'))

    # Relationships
    prescriptions = db.relationship("Prescription", back_populates="doctor")
    # appointments = db.relationship("Appointment", back_populates="doctor")
    specialty = db.relationship("Specialty", back_populates="doctors")

    def __repr__(self):
        return f"<Doctor(username='{self.username}', specialty='{self.specialty_id}')>"

    __mapper_args__ = {
        'polymorphic_identity': 'doctor'
    }

    # For SQL Server, consider using a proper JSON column or a separate table for available days
    def set_available_days(self, days):
        self.available_days = json.dumps(days)

    def get_available_days(self):
        return json.loads(self.available_days) if self.available_days else []

    def set_available_days(self, days):
        """Set available days for the doctor. Days should be a list of strings."""
        self.available_days = json.dumps(days)

    def get_available_days(self):
        """Get available days for the doctor. Returns a list of strings."""
        return json.loads(self.available_days)
                           
class Specialty(db.Model):
    __tablename__ = 'specialties'

    id = db.Column(db.String(50), primary_key=True)  # Reduced from 225 to more reasonable
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Better for monetary values

    doctors = db.relationship("Doctor", back_populates="specialty")

class Patient(User):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # Added length
    medical_record_number = db.Column(db.String(50), unique=True, nullable=False)  # Added length

    # Relationships
    prescriptions = db.relationship("Prescription", back_populates="patient")
    # appointments = db.relationship("Appointment", foreign_keys=["Appointment.patient_id"], back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(username='{self.username}', age={self.age})>"

    __mapper_args__ = {
        'polymorphic_identity': 'patient'
    }

class Admin(User):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    access_level = db.Column(db.Integer, default=1, server_default=text('1'))

    def __repr__(self):
        return f"<Admin(username='{self.username}', access_level={self.access_level})>"

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }