# app/models/record_access.py

from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app import db


class MedicalRecordAccess(db.Model):
    __tablename__ = "medical_record_access"

    id = db.Column(db.Integer, primary_key=True, index=True)
    record_id = db.Column(db.Integer, db.ForeignKey("medical_records.id"))
    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    granted_by = db.Column(db.Integer, db.ForeignKey("users.id"))
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)

    record = db.relationship("MedicalRecord", back_populates="access_records")
    doctor = db.relationship("User", foreign_keys=[doctor_id])
    granted_by_user = db.relationship("User", foreign_keys=[granted_by])

def __repr__(self):
        return f"<MedicalRecordAccess(id={self.id}, record_id={self.record_id}, doctor_id={self.doctor_id}, granted_by={self.granted_by}, granted_at={self.granted_at})>"