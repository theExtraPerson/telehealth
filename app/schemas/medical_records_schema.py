from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


# --- CREATE ---
class MedicalRecordCreate(BaseModel):
    description: str
    doctor_name: str
    date_of_birth: date  # Converted from str to `date`

    class Config:
        orm_mode = True


# --- SHARE ---
class ShareRecordCreate(BaseModel):
    record_id: int

    class Config:
        orm_mode = True


# --- ACCESS GRANT (OPTIONAL) ---
class GrantAccessSchema(BaseModel):
    record_id: int
    doctor_id: int


# --- OUT / RETURN ---
class MedicalRecordOut(BaseModel):
    id: int
    description: str
    doctor_name: str
    date_of_birth: date
    patient_id: int
    uploaded_at: datetime

    class Config:
        orm_mode = True

