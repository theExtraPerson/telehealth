from fastapi import FastAPI, HTTPException
from flask import Blueprint
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

appointments_api = Blueprint('appointments_api', __name__)
app = FastAPI()

class Appointment(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    date: datetime

appointments = []

@appointments_api.post("/appointments/", response_model=Appointment)
def create_appointment(appointment: Appointment):
    appointments.append(appointment)
    return appointment

@appointments_api.get("/appointments/", response_model=List[Appointment])
def get_appointments():
    return appointments

@appointments_api.get("/appointments/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment.id == appointment_id:
            return appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@appointments_api.put("/appointments/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: int, updated_appointment: Appointment):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            appointments[index] = updated_appointment
            return updated_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@appointments_api.delete("/appointments/{appointment_id}", response_model=Appointment)
def delete_appointment(appointment_id: int):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            deleted_appointment = appointments.pop(index)
            return deleted_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")


