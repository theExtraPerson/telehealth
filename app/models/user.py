from flask_login import UserMixin
from pydantic import json
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_doctor = db.Column(db.Boolean, default=0)
    is_patient = db.Column(db.Boolean, default=1)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False, default='patient')

    user_type = db.Column(db.String(50))
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

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

    @property

    def set_password(self, password=password_hash):
        self.password_hash = generate_password_hash(password)
        return f"<User(password='{self.password_hash}')>"

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': user_type
    }

class Doctor(User):
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    specialty_id = db.Column(db.String, db.ForeignKey('specialties.id'),nullable=False)
    license_number = db.Column(db.String, unique=True, nullable=False)
    bio = db.Column(db.String, nullable=False)
    schedule = db.Column(db.Text)
    languages_spoken = db.Column(db.String(255))
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    phone = db.Column(db.String(20))
    medical_license = db.Column(db.String(100))
    conditions_treated = db.Column(db.Text)
    available_days = db.Column(db.String)  # Use JSON if using SQLite
    photo = db.Column(db.String(200))  # Save filename or cloud path
    whatsapp = db.Column(db.Boolean, default=False)
    phone_call = db.Column(db.Boolean, default=False)
    video_call = db.Column(db.Boolean, default=False)

    prescriptions = db.relationship("Prescription", back_populates="doctor")
    appointments = db.relationship("Appointment", back_populates="doctor")
    specialty = db.relationship("Specialty", back_populates="doctors")

    def __repr__(self):
        return f"<Doctor(username='{self.username}', specialty='{self.specialty}')>"

    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
        # 'inherit_condition': (User.id == id)
    }

    def set_available_days(self, days):
        """Set available days for the doctor. Days should be a list of strings."""
        self.available_days = json.dumps(days)

    def get_available_days(self):
        """Get available days for the doctor. Returns a list of strings."""
        return json.loads(self.available_days)
                           
class Specialty(db.Model):
    __tablename__ = 'specialties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)  # Price per consultation

    doctors = db.relationship("Doctor", back_populates="specialty")

class Patient(User):
    __tablename__ = 'patients'

    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)
    medical_record_number = db.Column(db.String, unique=True, nullable=False)

    prescriptions = db.relationship("Prescription", back_populates="patient")
    appointments = db.relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Patient(username='{self.username}', age='{self.age}', password='{self.password}', email='{self.email}')>"

    __mapper_args__ = {
        'polymorphic_identity': 'patient',
        'inherit_condition': (User.id == id)
    }

class Admin(User):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    access_level = db.Column(db.Integer, default=1)

    def __repr__(self):
        return f"<Admin(username='{self.username}', admin_level='{self.access_level}')>"

    __mapper_args__ = {
        'polymorphic_identity': 'admin',
        'inherit_condition': (User.id == id)
    }