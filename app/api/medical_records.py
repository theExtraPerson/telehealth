from fastapi import APIRouter, Depends, HTTPException, status
from flask_login import current_user
from sqlalchemy.orm import Session

from app import schemas, models
from app.api.user import get_current_user
# from app.routes.auth import get_current_user
from app.utils.helpers import get_db
from app.services.medical_records_service import MedicalRecordsService

router = APIRouter(
    prefix="/medical_records",
    tags=["medical_records"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/")
def get_medical_records(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                        current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only patients can access their medical records.")

    medical_records_service = MedicalRecordsService(db)
    records = medical_records_service.get_medical_records(current_user.id, skip, limit)
    return records


@router.post("/")
def create_medical_record(record: schemas.MedicalRecordCreate, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can create medical records.")

    medical_records_service = MedicalRecordsService(db)
    new_record = medical_records_service.create_medical_record(record, current_user.id)
    return new_record


@router.post("/share")
def share_medical_record(share: schemas.ShareRecordCreate, db: Session = Depends(get_db),
                         current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can share medical records.")

    medical_records_service = MedicalRecordsService(db)
    result = medical_records_service.share_medical_record(share, current_user.id)
    return result


@router.get("/export")
def export_medical_record(record_id: int, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can export medical records.")

    medical_records_service = MedicalRecordsService(db)
    result = medical_records_service.export_medical_record(record_id, current_user.id)
    return result


@router.get("/{record_id}")
def get_medical_record_by_id(record_id: int, db: Session = Depends(get_db),
                             current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    
    medical_records_service = MedicalRecordsService(db)
    record = medical_records_service.get_medical_record_by_id(record_id, current_user.id)

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found.")

    return record


@router.post("/grant_access")
def grant_access_to_doctor(access: schemas.GrantAccessSchema, db: Session = Depends(get_db),
                           current_user: models.User = Depends(get_current_user)):
    if not current_user.is_patient:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can grant access.")

    medical_records_service = MedicalRecordsService(db)
    result = medical_records_service.grant_doctor_access(access.record_id, access.doctor_id, current_user.id)
    return result


from fastapi.responses import FileResponse

@router.get("/export/{record_id}")
def export_medical_record(record_id: int, db: Session = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    medical_records_service = MedicalRecordsService(db)
    file_path = medical_records_service.export_medical_record(record_id, current_user.id)

    if not file_path:
        raise HTTPException(status_code=404, detail="Record not found or export failed.")
    
    return FileResponse(path=file_path, filename=f"record_{record_id}.pdf", media_type='application/pdf')


@router.get("/doctor/{patient_id}")
def get_patient_records_for_doctor(patient_id: int, db: Session = Depends(get_db),
                                   current_user: models.User = Depends(get_current_user)):
    if not current_user.is_doctor:
        raise HTTPException(status_code=403, detail="Only doctors can access this.")

    # You should check if doctor has access to this patient
    medical_records_service = MedicalRecordsService(db)
    records = medical_records_service.get_records_shared_with_doctor(patient_id, current_user.id)
    return records
