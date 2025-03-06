from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import schemas, models, crud
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/medical_records",
    tags=["medical_records"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/", response_model=List[schemas.MedicalRecord])
def get_medical_records(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can access their medical records.")
    return crud.get_medical_records(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/", response_model=schemas.MedicalRecord)
def create_medical_record(record: schemas.MedicalRecordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can create medical records.")
    return crud.create_medical_record(db=db, record=record, user_id=current_user.id)

@router.post("/share", response_model=schemas.SharedRecord)
def share_medical_record(share: schemas.ShareRecordCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can share medical records.")
    return crud.share_medical_record(db=db, share=share, user_id=current_user.id)

@router.get("/export", response_model=schemas.ExportRecord)
def export_medical_record(record_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can export medical records.")
    return crud.export_medical_record(db=db, record_id=record_id, user_id=current_user.id)