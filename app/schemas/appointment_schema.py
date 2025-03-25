from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AppointmentSchema(BaseModel):
    id: Optional[int] = Field(None, description="The unique identifier of the appointment")
    patient_name: str = Field(..., description="The name of the patient")
    doctor_name: str = Field(..., description="The name of the doctor")
    appointment_date: datetime = Field(..., description="The date and time of the appointment")
    reason: Optional[str] = Field(None, description="The reason for the appointment")
    status: Optional[str] = Field("scheduled", description="The status of the appointment")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "patient_name": "John Doe",
                "doctor_name": "Dr. Smith",
                "appointment_date": "2023-10-15T14:30:00",
                "reason": "Routine check-up",
                "status": "scheduled"
            }
        }


def dump(new_appointment):
    return None