from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.models.medical_record import MedicalRecord

from app import schemas, models
from app.api.deps import get_current_user, get_db
from app.services.medical_records_service import MedicalRecordsService
from app.config import settings

router = APIRouter(
    prefix="/medical-records",
    tags=["medical-records"]
)

@router.post("/", response_model=schemas.MedicalRecordOut)
def create_medical_record(
    record_data: schemas.MedicalRecordCreate,
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create medical records."
        )
    
    service = MedicalRecordsService(db)
    return service.create_medical_record(record_data, current_user.id, file)

@router.get("/", response_model=List[schemas.MedicalRecordOut])
def get_medical_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    service = MedicalRecordsService(db)
    
    if current_user.is_patient:
        return service.get_medical_records(current_user.id, skip, limit)
    elif current_user.is_doctor:
        return service.get_doctor_records(current_user.id, skip, limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access."
        )

@router.get("/{record_id}", response_model=schemas.MedicalRecordOut)
def get_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    service = MedicalRecordsService(db)
    
    if current_user.is_patient:
        return service._verify_patient_access(record_id, current_user.id)
    elif current_user.is_doctor:
        return service._verify_doctor_access(record_id, current_user.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized access."
        )

@router.post("/{record_id}/share")
def share_medical_record(
    record_id: int,
    share_data: schemas.ShareRecordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    service = MedicalRecordsService(db)
    return service.share_record_via_email(
        record_id=record_id,
        recipient_email=share_data.recipient_email,
        user_id=current_user.id
    )

@router.get("/{record_id}/export")
def export_medical_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    service = MedicalRecordsService(db)
    pdf_path = service.generate_pdf_export(record_id, current_user.id)
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"medical_record_{record_id}.pdf"
    )

@router.post("/telemedicine", response_model=schemas.TelemedicineSessionOut)
def create_telemedicine_session(
    session_data: schemas.TelemedicineSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can initiate telemedicine sessions."
        )
    
    service = MedicalRecordsService(db)
    return service.create_telemedicine_session(
        patient_id=session_data.patient_id,
        doctor_id=current_user.id,
        session_data=session_data.dict()
    )

@router.get("/shared/{token}", response_model=schemas.MedicalRecordOut)
def get_shared_record(
    token: str,
    db: Session = Depends(get_db)
):
    # In a real implementation, you would verify the token against a database
    # For this example, we'll just get the record ID from the token
    try:
        record_id = int(token.split('_')[0])
    except (ValueError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid share token."
        )
    
    service = MedicalRecordsService(db)
    record = service.db.query(MedicalRecord).get(record_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found."
        )
    
    return record