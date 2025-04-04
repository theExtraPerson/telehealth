from datetime import datetime, timezone
# from sqlalchemy.orm import relationship
from app import db

class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    description = db.Column(db.String, nullable=True)

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")

    def __repr__(self):
        return f"<Appointment(date'{self.appointment_date}', description='{self.description}')>'"

    def to_dict(self):
        return {
            'id': self.id,
            'doctor_id': self.id,
            'patient_id': self.patient_id,
            'appointment_date': self.appointment_date.isoformat(),
            'description': self.description
        }