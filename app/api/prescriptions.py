from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas import PrescriptionCreate, PrescriptionRead
from app.models import Prescription
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=PrescriptionRead)
def create_prescription(prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    db_prescription = Prescription(**prescription.dict())
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

@router.get("/", response_model=List[PrescriptionRead])
def read_prescriptions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    prescriptions = db.query(Prescription).offset(skip).limit(limit).all()
    return prescriptions

@router.get("/{prescription_id}", response_model=PrescriptionRead)
def read_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    return prescription

@router.put("/{prescription_id}", response_model=PrescriptionRead)
def update_prescription(prescription_id: int, prescription: PrescriptionCreate, db: Session = Depends(get_db)):
    db_prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if db_prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    for key, value in prescription.dict().items():
        setattr(db_prescription, key, value)
    db.commit()
    db.refresh(db_prescription)
    return db_prescription

@router.delete("/{prescription_id}", response_model=PrescriptionRead)
def delete_prescription(prescription_id: int, db: Session = Depends(get_db)):
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if prescription is None:
        raise HTTPException(status_code=404, detail="Prescription not found")
    db.delete(prescription)
    db.commit()
    return prescription