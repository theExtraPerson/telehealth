import os
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
import uuid
from pathlib import Path

from app.models.medical_record import MedicalRecord, MedicalRecordAccess
from app.models.user import User
from app.schemas.medical_records_schema import MedicalRecordCreate, MedicalRecordUpdate
from app.config import settings
from app.utils.pdf_generator import generate_pdf_from_record
from app.utils.telemedicine import generate_telemedicine_link

class MedicalRecordsService:
    def __init__(self, db: Session):
        self.db = db

        self.UPLOAD_DIR = 'uploads'

        self.EXPORT_DIR = 'exports'

    def _verify_patient_access(self, record_id: int, user_id: int) -> MedicalRecord:
        record = self.db.query(MedicalRecord).filter(
            MedicalRecord.id == record_id,
            MedicalRecord.patient_id == user_id
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Record not found or access denied."
            )
        return record

    def _verify_doctor_access(self, record_id: int, doctor_id: int) -> MedicalRecord:
        # Check if doctor has direct access or shared access
        record = self.db.query(MedicalRecord).join(
            MedicalRecordAccess,
            MedicalRecord.id == MedicalRecordAccess.record_id
        ).filter(
            (MedicalRecord.id == record_id) &
            (
                (MedicalRecord.doctor_id == doctor_id) |
                (MedicalRecordAccess.doctor_id == doctor_id)
            )
        ).first()
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access to this record is not authorized."
            )
        return record

    def create_medical_record(self, record_data: MedicalRecordCreate, doctor_id: int, file: UploadFile = None) -> MedicalRecord:
        """Create a new medical record with optional file attachment"""
        file_path = None
        if file:
            upload_dir = Path(settings.UPLOAD_DIR) / "medical_records"
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_ext = file.filename.split('.')[-1]
            file_name = f"{uuid.uuid4()}.{file_ext}"
            file_path = str(upload_dir / file_name)
            
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())

        db_record = MedicalRecord(
            patient_id=record_data.patient_id,
            date_of_visit=record_data.date_of_visit,
            description=record_data.description,
            diagnosis=record_data.diagnosis,
            treatment=record_data.treatment,
            medications=record_data.medications,
            notes=record_data.notes,
            doctor_name=record_data.doctor_name,
            doctor_id=doctor_id,
            file_path=file_path,
            is_telemedicine=record_data.is_telemedicine,
            telemedicine_link=generate_telemedicine_link() if record_data.is_telemedicine else None,
            uploaded_at=datetime.now(timezone.utc)
        )
        
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update_medical_record(self, record_id: int, update_data: MedicalRecordUpdate, user_id: int) -> MedicalRecord:
        """Update an existing medical record"""
        record = self._verify_patient_access(record_id, user_id)
        
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(record, field, value)
        
        record.last_updated = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(record)
        return record

    def share_record_via_email(self, record_id: int, recipient_email: str, user_id: int) -> dict:
        """Share a record via email with a secure link"""
        record = self._verify_patient_access(record_id, user_id)
        
        # Generate a secure token for email sharing
        token = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        # In a real implementation, you would send an email here with the token
        share_url = f"{settings.FRONTEND_URL}/shared-records/{token}"
        
        return {
            "message": "Record shared successfully",
            "share_url": share_url,
            "expires_at": expires_at.isoformat()
        }

    def generate_pdf_export(self, record_id: int, user_id: int) -> str:
        """Generate a PDF version of the medical record"""
        record = self._verify_patient_access(record_id, user_id)
        
        output_dir = Path(settings.EXPORT_DIR) / "pdf"
        output_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = str(output_dir / f"record_{record_id}_{user_id}.pdf")
        
        generate_pdf_from_record(record, pdf_path)
        return pdf_path

    def create_telemedicine_session(self, patient_id: int, doctor_id: int, session_data: dict) -> dict:
        """Create a telemedicine session and return join links"""
        doctor = self.db.query(User).filter(User.id == doctor_id, User.is_doctor).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        
        # Create a telemedicine record
        record = MedicalRecord(
            patient_id=patient_id,
            doctor_id=doctor_id,
            doctor_name=f"{doctor.first_name} {doctor.last_name}",
            date_of_visit=datetime.now(timezone.utc),
            description="Telemedicine consultation",
            is_telemedicine=True,
            telemedicine_link=generate_telemedicine_link(),
            uploaded_at=datetime.now(timezone.utc)
        )
        
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        return {
            "patient_link": f"{settings.TELEMEDICINE_URL}/join/{record.telemedicine_link}?role=patient",
            "doctor_link": f"{settings.TELEMEDICINE_URL}/join/{record.telemedicine_link}?role=doctor",
            "record_id": record.id,
            "expires_at": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        }

    def get_records_shared_with_doctor(self, patient_id: int, doctor_id: int) -> list:
        """Get all records shared with a specific doctor for a patient"""
        return self.db.query(MedicalRecord).join(
            MedicalRecordAccess,
            MedicalRecord.id == MedicalRecordAccess.record_id
        ).filter(
            (MedicalRecord.patient_id == patient_id) &
            (MedicalRecordAccess.doctor_id == doctor_id)
        ).all()