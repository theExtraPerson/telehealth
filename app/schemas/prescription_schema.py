from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class Medication(BaseModel):
    name: str = Field(..., description="Name of the medication")
    dosage: str = Field(..., description="Dosage of the medication")
    frequency: str = Field(..., description="Frequency of the medication intake")


class Prescription(BaseModel):
    patient_id: str = Field(..., description="ID of the patient")
    doctor_id: str = Field(..., description="ID of the prescribing doctor")
    medications: List[Medication] = Field(..., description="List of medications prescribed")
    issue_date: date = Field(..., description="Date when the prescription was issued")
    expiration_date: Optional[date] = Field(None, description="Date when the prescription expires")

    class Config:
        schema_extra = {
            "example": {
                "patient_id": "12345",
                "doctor_id": "67890",
                "medications": [
                    {
                        "name": "Ibuprofen",
                        "dosage": "200mg",
                        "frequency": "Twice a day"
                    }
                ],
                "issue_date": "2023-10-01",
                "expiration_date": "2023-12-01"
            }
        }


def prescription_schema():
    return None
