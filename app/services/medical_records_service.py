# app/services/medical_records_service.py

import os
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.medical_record import MedicalRecord
from app.models.record_access import MedicalRecordAccess
from app.models.user import User


class MedicalRecordsService:
    def __init__(self, db: Session):
        self.db = db

    def get_medical_records(self, user_id: int, skip: int = 0, limit: int = 10):
        """
        Fetches the medical records for a specific patient.
        """
        return (
            self.db
            .query(MedicalRecord)
            .filter(MedicalRecord.patient_id == user_id)
            .order_by(MedicalRecord.uploaded_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_medical_record_by_id(self, record_id: int, user_id: int):
        """
        Fetches a single medical record by ID, verifying ownership.
        """
        return (
            self.db
            .query(MedicalRecord)
            .filter(
                MedicalRecord.id == record_id,
                MedicalRecord.patient_id == user_id
            )
            .first()
        )

    def create_medical_record_with_file(
        self,
        description: str,
        doctor_name: str,
        date_of_birth: datetime,
        file_path: str,
        user_id: int
    ):
        """
        Creates a new medical record for the patient, saving the file path.
        """
        db_record = MedicalRecord(
            patient_id=user_id,
            description=description,
            doctor_name=doctor_name,
            date_of_birth=date_of_birth,
            file_path=file_path,
            uploaded_at=datetime.utcnow()
        )
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def get_file_path(self, record_id: int, user_id: int) -> str:
        """
        Retrieves the file path for a given record (for download).
        """
        record = self.get_medical_record_by_id(record_id, user_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found."
            )
        return record.file_path

    def share_medical_record(self, record_id: int, recipient_email: str, user_id: int):
        """
        Logic to share the medical record (e.g., send via email).
        """
        record = self.get_medical_record_by_id(record_id, user_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found."
            )

        # TODO: implement real email-sending logic
        # send_email(to=recipient_email, subject=..., body=..., attachments=[record.file_path])

        return {"message": f"Record {record.id} shared with {recipient_email}"}

    def grant_doctor_access(self, record_id: int, doctor_id: int, user_id: int):
        """
        Grants a doctor access to a patient's record.
        """
        record = self.get_medical_record_by_id(record_id, user_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found."
            )

        # ensure doctor exists
        doctor = self.db.query(User).filter(User.id == doctor_id, User.is_doctor).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found."
            )

        access = MedicalRecordAccess(
            record_id=record_id,
            doctor_id=doctor_id,
            granted_by=user_id,
            granted_at=datetime.utcnow()
        )
        self.db.add(access)
        self.db.commit()
        return {"message": f"Access granted to doctor {doctor_id} for record {record_id}"}

    def export_medical_record(self, record_id: int, user_id: int):
        """
        Returns the path for file download (you can wrap this in a FileResponse).
        """
        return self.get_file_path(record_id, user_id)
