import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status, UploadFile
from sqlalchemy import and_, or_
from app.models.medical_record import MedicalRecordAccess, MedicalRecord, LabResult, MedicalRecordAuditLog
from app.models.user import User
from app.schemas.medical_records_schema import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordAccessCreate,
    LabResultCreate,
    TelemedicineSessionCreate
)
from app.config import settings
from app.utils.pdf_generator import generate_pdf_from_record
from app.utils.telemedicine import generate_telemedicine_link
from app.utils.security_helpers import generate_secure_share_token
from app.utils.encryption import ( 
    encrypt_data,
    decrypt_data
)

class MedicalRecordsService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path(settings.MEDICAL_RECORDS_UPLOAD_DIR)
        self.export_dir = Path(settings.MEDICAL_RECORDS_EXPORT_DIR)
        self.ensure_directories()

    def ensure_directories(self):
        """Ensure required directories exist"""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    ## --------------------------
    ## Core Record Operations
    ## --------------------------

    def create_medical_record(self, record_data: MedicalRecordCreate, doctor_id: int, file: UploadFile = None) -> MedicalRecord:
        """
        Create a new medical record with comprehensive validation and telemedicine support
        """
        # Validate patient exists and is a patient
        patient = self.db.query(User).filter(
            User.id == record_data.patient_id,
            User.is_patient == True
        ).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid patient ID."
            )

        # Handle file upload if present
        file_path = self._handle_file_upload(file) if file else None

        # Create the record
        db_record = MedicalRecord(
            record_uid=str(uuid.uuid4()),
            patient_id=record_data.patient_id,
            doctor_id=doctor_id,
            date_of_visit=record_data.date_of_visit,
            visit_type=record_data.visit_type,
            facility_id=record_data.facility_id,
            description=encrypt_data(record_data.description) if record_data.description else None,
            diagnosis=encrypt_data(record_data.diagnosis) if record_data.diagnosis else None,
            diagnosis_code=record_data.diagnosis_code,
            treatment=encrypt_data(record_data.treatment) if record_data.treatment else None,
            procedures=encrypt_data(record_data.procedures) if record_data.procedures else None,
            medications=encrypt_data(record_data.medications) if record_data.medications else None,
            allergies=encrypt_data(record_data.allergies) if record_data.allergies else None,
            vital_signs=encrypt_data(record_data.vital_signs) if record_data.vital_signs else None,
            is_telemedicine=record_data.is_telemedicine,
            telemedicine_link=generate_telemedicine_link() if record_data.is_telemedicine else None,
            telemedicine_duration=record_data.telemedicine_duration,
            file_path=file_path,
            document_type=record_data.document_type,
            is_confidential=record_data.is_confidential
        )

        self.db.add(db_record)
        self.db.commit()

        # Log the creation
        self._log_record_access(
            record_id=db_record.id,
            user_id=doctor_id,
            action="create",
            details="Record created"
        )

        return db_record

    def get_record_by_uid(self, record_uid: str) -> Optional[MedicalRecord]:
        """Get record by its UID with related data"""
        return self.db.query(MedicalRecord)\
            .options(
                joinedload(MedicalRecord.patient),
                joinedload(MedicalRecord.doctor),
                joinedload(MedicalRecord.facility),
                joinedload(MedicalRecord.lab_results)
            )\
            .filter(MedicalRecord.record_uid == record_uid)\
            .first()

    def update_medical_record(self, record_id: int, update_data: MedicalRecordUpdate, updated_by: int) -> MedicalRecord:
        """
        Update a medical record with amendment tracking
        """
        record = self.db.query(MedicalRecord).get(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found."
            )

        # Track changes for audit
        changes = []
        for field, new_value in update_data.dict(exclude_unset=True).items():
            old_value = getattr(record, field)
            if old_value != new_value:
                changes.append(f"{field}: {old_value} → {new_value}")
                setattr(record, field, new_value)

        if changes:
            record.last_updated = datetime.utcnow()
            record.record_status = "amended"
            self.db.commit()

            # Log the changes
            self._log_record_access(
                record_id=record.id,
                user_id=updated_by,
                action="update",
                details=" | ".join(changes)
            )

        return record

    ## --------------------------
    ## Access Control
    ## --------------------------

    def has_access(self, record_id: int, user_id: int) -> bool:
        """
        Check if user has access to a specific record
        """
        user = self.db.query(User).get(user_id)
        if not user:
            return False

        # Patients can access their own records
        record = self.db.query(MedicalRecord).get(record_id)
        if not record:
            return False

        if user.is_patient and record.patient_id == user.id:
            return True

        # Doctors can access records they created or were shared with them
        if user.is_doctor:
            return self.db.query(MedicalRecordAccess).filter(
                and_(
                    MedicalRecordAccess.record_id == record_id,
                    MedicalRecordAccess.accessor_id == user.id,
                    or_(
                        MedicalRecordAccess.expires_at == None,
                        MedicalRecordAccess.expires_at > datetime.utcnow()
                    )
                )
            ).first() is not None or record.doctor_id == user.id

        # Admins have full access
        if user.is_admin:
            return True

        return False

    def grant_access(self, record_id: int, accessor_id: int, granted_by: int, 
                    access_level: str, purpose: str, expires_at: datetime = None) -> MedicalRecordAccess:
        """
        Grant access to a medical record with expiration
        """
        # Validate accessor is a healthcare provider
        accessor = self.db.query(User).filter(
            User.id == accessor_id,
            or_(User.is_doctor == True, User.is_admin == True)
        ).first()
        if not accessor:
            raise ValueError("Access can only be granted to healthcare providers")

        # Create or update access record
        access = self.db.query(MedicalRecordAccess).filter(
            MedicalRecordAccess.record_id == record_id,
            MedicalRecordAccess.accessor_id == accessor_id
        ).first()

        if access:
            access.access_level = access_level
            access.expires_at = expires_at
            access.purpose = purpose
        else:
            access = MedicalRecordAccess(
                record_id=record_id,
                accessor_id=accessor_id,
                granted_by=granted_by,
                access_level=access_level,
                purpose=purpose,
                expires_at=expires_at
            )
            self.db.add(access)

        self.db.commit()

        # Log the access grant
        self._log_record_access(
            record_id=record_id,
            user_id=granted_by,
            action="grant_access",
            details=f"Granted {access_level} access to user {accessor_id}"
        )

        return access

    ## --------------------------
    ## Telemedicine Integration
    ## --------------------------

    def create_telemedicine_session(self, record_id: int, patient_id: int, doctor_id: int, 
                                  session_data: TelemedicineSessionCreate) -> dict:
        """
        Create a telemedicine session linked to a medical record
        """
        # Verify the record exists and belongs to this patient-doctor pair
        record = self.db.query(MedicalRecord).filter(
            MedicalRecord.id == record_id,
            MedicalRecord.patient_id == patient_id,
            MedicalRecord.doctor_id == doctor_id
        ).first()
        if not record:
            raise ValueError("Invalid medical record or patient-doctor mismatch")

        # Update record with telemedicine details
        record.is_telemedicine = True
        record.telemedicine_link = generate_telemedicine_link()
        record.telemedicine_duration = session_data.expected_duration
        record.video_platform = session_data.platform
        record.meeting_link = session_data.meeting_url
        record.meeting_password = session_data.meeting_password

        self.db.commit()

        # Log the telemedicine session
        self._log_record_access(
            record_id=record.id,
            user_id=doctor_id,
            action="telemedicine_start",
            details=f"Started {session_data.platform} session"
        )

        return {
            "record_uid": record.record_uid,
            "meeting_link": record.meeting_link,
            "patient_link": f"{record.meeting_link}?role=patient&name=Patient",
            "doctor_link": f"{record.meeting_link}?role=doctor&name=Dr.{record.doctor.last_name}",
            "expires_at": (datetime.utcnow() + timedelta(hours=2)).isoformat()
        }

    ## --------------------------
    ## Lab Results Management
    ## --------------------------

    def add_lab_result(self, record_id: int, lab_data: LabResultCreate, added_by: int) -> LabResult:
        """
        Add lab results to a medical record
        """
        record = self.db.query(MedicalRecord).get(record_id)
        if not record:
            raise ValueError("Medical record not found")

        lab_result = LabResult(
            record_id=record_id,
            test_name=lab_data.test_name,
            result_value=lab_data.result_value,
            result_units=lab_data.result_units,
            reference_range=lab_data.reference_range,
            performed_at=lab_data.performed_at,
            added_by=added_by
        )

        self.db.add(lab_result)
        self.db.commit()

        # Log the lab result addition
        self._log_record_access(
            record_id=record_id,
            user_id=added_by,
            action="add_lab_result",
            details=f"Added lab result: {lab_data.test_name}"
        )

        return lab_result

    ## --------------------------
    ## Query Methods
    ## --------------------------

    def get_patient_records(self, patient_id: int, skip: int = 0, limit: int = 100,
                          start_date: datetime = None, end_date: datetime = None) -> List[MedicalRecord]:
        """
        Get records for a specific patient with optional date filtering
        """
        query = self.db.query(MedicalRecord)\
            .filter(MedicalRecord.patient_id == patient_id)\
            .order_by(MedicalRecord.date_of_visit.desc())

        if start_date:
            query = query.filter(MedicalRecord.date_of_visit >= start_date)
        if end_date:
            query = query.filter(MedicalRecord.date_of_visit <= end_date)

        return query.offset(skip).limit(limit).all()

    def get_doctor_records(self, doctor_id: int, patient_id: int = None, 
                          facility_id: int = None, is_telemedicine: bool = None,
                          skip: int = 0, limit: int = 100) -> List[MedicalRecord]:
        """
        Get records accessible to a doctor with various filters
        """
        query = self.db.query(MedicalRecord)\
            .outerjoin(MedicalRecordAccess,
                      and_(
                          MedicalRecordAccess.record_id == MedicalRecord.id,
                          or_(
                              MedicalRecordAccess.expires_at == None,
                              MedicalRecordAccess.expires_at > datetime.utcnow()
                          )
                      ))\
            .filter(
                or_(
                    MedicalRecord.doctor_id == doctor_id,
                    MedicalRecordAccess.accessor_id == doctor_id
                )
            )\
            .order_by(MedicalRecord.date_of_visit.desc())

        if patient_id:
            query = query.filter(MedicalRecord.patient_id == patient_id)
        if facility_id:
            query = query.filter(MedicalRecord.facility_id == facility_id)
        if is_telemedicine is not None:
            query = query.filter(MedicalRecord.is_telemedicine == is_telemedicine)

        return query.offset(skip).limit(limit).all()

    ## --------------------------
    ## Export and Sharing
    ## --------------------------

    def generate_export(self, record_id: int, format: str = "pdf", 
                       redact: bool = False, requested_by: int = None) -> dict:
        """
        Generate export of medical record in specified format
        """
        record = self.db.query(MedicalRecord).get(record_id)
        if not record:
            raise ValueError("Medical record not found")

        if format == "pdf":
            pdf_path = self.export_dir / f"record_{record.record_uid}.pdf"
            generate_pdf_from_record(record, str(pdf_path), redact)
            return {
                "file_path": str(pdf_path),
                "format": "pdf"
            }
        else:
            # Handle other formats (JSON, CSV)
            raise ValueError(f"Unsupported export format: {format}")

    def generate_share_link(self, record_id: int, recipient_email: str, 
                           shared_by: int, expires_hours: int = 168, 
                           access_level: str = "view") -> str:
        """
        Generate a secure share link with expiration
        """
        token = generate_secure_share_token(
            record_id=record_id,
            recipient_email=recipient_email,
            expires_hours=expires_hours
        )

        # Store the token in database
        share_record = MedicalRecordAccess(
            record_id=record_id,
            accessor_email=recipient_email,
            granted_by=shared_by,
            access_level=access_level,
            expires_at=datetime.utcnow() + timedelta(hours=expires_hours),
            is_token_based=True,
            share_token=token
        )
        self.db.add(share_record)
        self.db.commit()

        return f"{settings.FRONTEND_URL}/shared-records/{token}"

    ## --------------------------
    ## Audit and Logging
    ## --------------------------

    def _log_record_access(self, record_id: int, user_id: int, action: str, details: str = ""):
        """
        Log an access or modification event for a medical record
        """
        log_entry = MedicalRecordAuditLog(
            record_id=record_id,
            user_id=user_id,
            action=action,
            details=details,
            ip_address="0.0.0.0",  # Would be set from request in actual implementation
            user_agent="system"     # Would be set from request headers
        )
        self.db.add(log_entry)
        self.db.commit()

    def get_audit_logs(self, record_id: int) -> List[MedicalRecordAuditLog]:
        """
        Get audit logs for a specific medical record
        """
        return self.db.query(MedicalRecordAuditLog)\
            .filter(MedicalRecordAuditLog.record_id == record_id)\
            .order_by(MedicalRecordAuditLog.created_at.desc())\
            .all()

    ## --------------------------
    ## Helper Methods
    ## --------------------------

    def _handle_file_upload(self, file: UploadFile) -> str:
        """
        Handle secure file upload for medical records
        """
        try:
            # Validate file type
            allowed_types = settings.ALLOWED_MEDICAL_RECORD_TYPES
            file_ext = os.path.splitext(file.filename)[1].lower().lstrip('.')
            if file_ext not in allowed_types:
                raise ValueError(f"Unsupported file type. Allowed types: {', '.join(allowed_types)}")

            # Generate secure filename
            file_name = f"{uuid.uuid4()}.{file_ext}"
            file_path = self.upload_dir / file_name

            # Save the file
            with open(file_path, "wb") as buffer:
                buffer.write(file.file.read())

            return str(file_path)

        except Exception as e:
            raise ValueError(f"File upload failed: {str(e)}")