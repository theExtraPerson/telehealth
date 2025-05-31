from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class MedicalRecordBase(BaseModel):
    patient_id: int
    date_of_visit: datetime
    description: str
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    medications: Optional[str] = None
    notes: Optional[str] = None
    is_telemedicine: bool = False

class MedicalRecordCreate(MedicalRecordBase):
    doctor_id: int
    facility_id: Optional[int] = None
    diagnosis_code: Optional[str] = None
    procedures: Optional[str] = None
    allergies: Optional[str] = None
    vital_signs: Optional[str] = None

class MedicalRecordUpdate(BaseModel):
    description: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    medications: Optional[str] = None
    notes: Optional[str] = None
    is_confidential: Optional[bool] = None

class MedicalRecordOut(MedicalRecordBase):
    id: int
    record_uid: str
    doctor_id: int
    doctor_name: str
    uploaded_at: datetime
    last_updated: Optional[datetime] = None
    is_confidential: bool = False
    record_status: str = "active"

    class Config:
        orm_mode = True

class AccessLevel(str, Enum):
    view = "view"
    edit = "edit"
    full = "full"

class MedicalRecordAccessCreate(BaseModel):
    doctor_id: int
    access_level: AccessLevel = AccessLevel.view
    purpose: str = Field(..., min_length=5, max_length=255)
    expires_at: Optional[datetime] = None

class MedicalRecordAccessOut(BaseModel):
    id: int
    record_id: int
    accessor_id: int
    granted_by: int
    access_level: AccessLevel
    purpose: str
    granted_at: datetime
    expires_at: Optional[datetime]
    is_emergency_access: bool = False

    class Config:
        orm_mode = True

class LabResultCreate(BaseModel):
    test_name: str
    result_value: str
    result_units: Optional[str] = None
    reference_range: Optional[str] = None
    performed_at: Optional[datetime] = None

class LabResultOut(BaseModel):
    id: int
    record_id: int
    test_name: str
    result_value: str
    result_units: Optional[str]
    reference_range: Optional[str]
    performed_at: datetime

    class Config:
        orm_mode = True

class TelemedicineSessionCreate(BaseModel):
    patient_id: int
    platform: str
    expected_duration: int = 30  # minutes
    meeting_url: Optional[str] = None
    meeting_password: Optional[str] = None

class TelemedicineSessionOut(BaseModel):
    record_uid: str
    patient_link: str
    doctor_link: str
    expires_at: datetime
    platform: str

class ShareRecordRequest(BaseModel):
    recipient_email: str
    expires_hours: int = 168  # 7 days default
    access_level: AccessLevel = AccessLevel.view