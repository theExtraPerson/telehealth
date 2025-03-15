from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_doctor = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Doctor(User):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    specialization = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Doctor(username='{self.username}', specialization='{self.specialization}')>"

class Admin(User):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    admin_level = Column(Integer, default=1)

    def __repr__(self):
        return f"<Admin(username='{self.username}', admin_level='{self.admin_level}')>"