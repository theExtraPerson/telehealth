from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

class Appointment(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    date: datetime

appointments = []

@app.post("/appointments/", response_model=Appointment)
def create_appointment(appointment: Appointment):
    appointments.append(appointment)
    return appointment

@app.get("/appointments/", response_model=List[Appointment])
def get_appointments():
    return appointments

@app.get("/appointments/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment.id == appointment_id:
            return appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@app.put("/appointments/{appointment_id}", response_model=Appointment)
def update_appointment(appointment_id: int, updated_appointment: Appointment):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            appointments[index] = updated_appointment
            return updated_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@app.delete("/appointments/{appointment_id}", response_model=Appointment)
def delete_appointment(appointment_id: int):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            deleted_appointment = appointments.pop(index)
            return deleted_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")