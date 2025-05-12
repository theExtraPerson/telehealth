from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

class MedicalRecordBase(BaseModel):
    patient_id: int
    date_of_visit: date
    description: str
    doctor_name: str
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    medications: Optional[str] = None
    file_path: Optional[str] = None
    notes: Optional[str]
    is_telemedicine: bool = False

    class Config:
        from_attributes = True

# --- CREATE ---
class MedicalRecordCreate(BaseModel):
    description: str
    doctor_name: str
    date_of_visit: date  # Converted from str to `date`

    class Config:
        from_attributes = True

# --- UPDATE ---
class MedicalRecordUpdate(BaseModel):
    description: Optional[str]
    doctor_name: Optional[str]
    date_of_visit: Optional[date]
    diagnosis: Optional[str]
    treatment: Optional[str]
    medications: Optional[str]
    notes: Optional[str]
    is_telemedicine: Optional[bool]


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
    patient_id: int
    uploaded_at: datetime

    class Config:
        from_attributes = True

