from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import os

from app import schemas, models
from app.api.deps import get_current_user, get_db
from app.services.medical_records_service import MedicalRecordsService
from app.config import settings
from app.models import MedicalRecord, MedicalRecordAccess, HealthFacility, LabResult
from app.schemas import (
    MedicalRecordCreate,
    MedicalRecordUpdate,
    MedicalRecordOut,
    MedicalRecordAccessCreate,
    LabResultCreate,
    TelemedicineSessionCreate
)

router = APIRouter(
    prefix="/medical-records",
    tags=["medical-records"]
)

## --------------------------
## Core Medical Records CRUD
## --------------------------

@router.post("/", response_model=schemas.MedicalRecordOut)
async def create_medical_record(
    record_data: schemas.MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new medical record with telemedicine support
    """
    if not current_user.is_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can create medical records."
        )
    
    # Validate facility if provided
    if record_data.facility_id:
        facility = db.query(HealthFacility).filter_by(id=record_data.facility_id).first()
        if not facility:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid health facility ID."
            )

    service = MedicalRecordsService(db)
    try:
        return service.create_medical_record(
            record_data=record_data,
            doctor_id=current_user.id,
            is_telemedicine=record_data.is_telemedicine
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[schemas.MedicalRecordOut])
async def get_medical_records(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    facility_id: Optional[int] = None,
    is_telemedicine: Optional[bool] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = Query(default=100, lte=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get medical records with advanced filtering
    """
    service = MedicalRecordsService(db)
    
    # Patients can only see their own records
    if current_user.is_patient:
        if patient_id and patient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other patients' records."
            )
        return service.get_patient_records(
            patient_id=current_user.id,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
    
    # Doctors can see their own records or filter
    elif current_user.is_doctor:
        return service.get_doctor_records(
            doctor_id=doctor_id or current_user.id,
            patient_id=patient_id,
            facility_id=facility_id,
            is_telemedicine=is_telemedicine,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
    
    # Admins can see all records
    elif current_user.is_admin:
        return service.get_all_records(
            patient_id=patient_id,
            doctor_id=doctor_id,
            facility_id=facility_id,
            is_telemedicine=is_telemedicine,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date
        )
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unauthorized access."
    )

@router.get("/{record_uid}", response_model=schemas.MedicalRecordOut)
async def get_medical_record(
    record_uid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get a specific medical record by UID with access control
    """
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Verify access
    if not service.has_access(record.id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this medical record."
        )
    
    return record

@router.put("/{record_uid}", response_model=schemas.MedicalRecordOut)
async def update_medical_record(
    record_uid: str,
    record_data: schemas.MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update a medical record (amendment)
    """
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Only the creating doctor or admin can update
    if not (current_user.id == record.doctor_id or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the creating doctor can update this record."
        )
    
    try:
        return service.update_medical_record(
            record_id=record.id,
            update_data=record_data,
            updated_by=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

## --------------------------
## Record Access Management
## --------------------------

@router.post("/{record_uid}/access", response_model=schemas.MedicalRecordAccessOut)
async def grant_record_access(
    record_uid: str,
    access_data: schemas.MedicalRecordAccessCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Grant access to a medical record
    """
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Only record owner or admin can grant access
    if not (current_user.id == record.doctor_id or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the record owner can grant access."
        )
    
    try:
        return service.grant_access(
            record_id=record.id,
            accessor_id=access_data.doctor_id,
            granted_by=current_user.id,
            access_level=access_data.access_level,
            purpose=access_data.purpose,
            expires_at=access_data.expires_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{record_uid}/access", response_model=List[schemas.MedicalRecordAccessOut])
async def get_record_access_list(
    record_uid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get access list for a medical record
    """
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Only record owner or admin can see access list
    if not (current_user.id == record.doctor_id or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the record owner can view access list."
        )
    
    return service.get_access_list(record.id)

## --------------------------
## Telemedicine Integration
## --------------------------

@router.post("/{record_uid}/telemedicine", response_model=schemas.TelemedicineSessionOut)
async def create_telemedicine_session(
    record_uid: str,
    session_data: schemas.TelemedicineSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create or update a telemedicine session linked to a medical record
    """
    if not current_user.is_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can initiate telemedicine sessions."
        )
    
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Verify the doctor owns the record
    if record.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the record owner can initiate telemedicine sessions."
        )
    
    try:
        return service.create_telemedicine_session(
            record_id=record.id,
            patient_id=record.patient_id,
            doctor_id=current_user.id,
            session_data=session_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

## --------------------------
## Lab Results Management
## --------------------------

@router.post("/{record_uid}/lab-results", response_model=schemas.LabResultOut)
async def add_lab_result(
    record_uid: str,
    lab_data: schemas.LabResultCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Add lab results to a medical record
    """
    if not current_user.is_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can add lab results."
        )
    
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Verify the doctor has access to the record
    if not service.has_access(record.id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this medical record."
        )
    
    try:
        return service.add_lab_result(
            record_id=record.id,
            lab_data=lab_data,
            added_by=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

## --------------------------
## Export and Sharing
## --------------------------

@router.get("/{record_uid}/export")
async def export_medical_record(
    record_uid: str,
    format: str = Query("pdf", regex="^(pdf|json|csv)$"),
    redact: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Export medical record in various formats
    """
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Verify access
    if not service.has_access(record.id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this medical record."
        )
    
    try:
        export_data = service.generate_export(
            record_id=record.id,
            format=format,
            redact=redact,
            requested_by=current_user.id
        )
        
        if format == "pdf":
            return FileResponse(
                export_data["file_path"],
                media_type="application/pdf",
                filename=f"medical_record_{record_uid}.pdf"
            )
        else:
            return JSONResponse(content=export_data)
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{record_uid}/share")
async def share_medical_record(
    record_uid: str,
    share_data: schemas.ShareRecordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Share medical record via secure link
    """
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Verify the user has sharing permissions
    if not service.can_share(record.id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No permission to share this record."
        )
    
    try:
        share_link = service.generate_share_link(
            record_id=record.id,
            recipient_email=share_data.recipient_email,
            shared_by=current_user.id,
            expires_hours=share_data.expires_hours,
            access_level=share_data.access_level
        )
        
        return {"share_link": share_link}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

## --------------------------
## Audit Logs
## --------------------------

@router.get("/{record_uid}/audit-logs")
async def get_audit_logs(
    record_uid: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get audit logs for a medical record
    """
    service = MedicalRecordsService(db)
    record = service.get_record_by_uid(record_uid)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found."
        )
    
    # Only record owner or admin can view audit logs
    if not (current_user.id == record.doctor_id or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the record owner can view audit logs."
        )
    
    return service.get_audit_logs(record.id)