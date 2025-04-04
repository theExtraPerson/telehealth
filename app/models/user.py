from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_doctor = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), nullable=False, default='patient')

    user_type = db.Column(db.String(50))

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

    @property
    def is_active(self):
        return True

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
    specialization = db.Column(db.String, nullable=False)
    license_number = db.Column(db.String, unique=True, nullable=False)

    prescriptions = db.relationship("Prescription", back_populates="doctor")
    appointments = db.relationship("Appointment", back_populates="doctor")

    def __repr__(self):
        return f"<Doctor(username='{self.username}', specialization='{self.specialization}')>"

    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
        # 'inherit_condition': (User.id == id)
    }

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