from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
class Prescription(Base):
    __tablename__ = 'prescriptions'

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    medication = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    instructions = Column(String, nullable=True)
    date_prescribed = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="prescriptions")
    doctor = relationship("Doctor", back_populates="prescriptions")