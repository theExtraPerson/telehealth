from fastapi import FastAPI, HTTPException
from flask import Blueprint, jsonify, request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app import db
# from app.schemas import appointment_schema
# from app.schemas.appointment_schema import AppointmentSchema

appointments_api = Blueprint('appointments_api', __name__)
app = FastAPI()

class Appointment(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    date: datetime

appointments = []

@appointments_api.route("/appointments/", methods=['POST'])
def create_appointment(appointment_schema):
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}),

    errors = appointment_schema.validate(json_data)
    if errors:
        return jsonify(errors), 400

    new_appointment = Appointment(**json_data)
    db.session.add(new_appointment)
    db.session.commit()

    return jsonify(appointment_schema.dump(new_appointment)), 201

@appointments_api.route("/appointments/", methods=['GET'])
def get_appointments():
    return appointments

@appointments_api.route("/appointments/{appointment_id}", methods=['GET'])
def get_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment.id == appointment_id:
            return appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@appointments_api.route("/appointments/{appointment_id}", methods=['GET', 'POST'])
def update_appointment(appointment_id: int, updated_appointment: Appointment):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            appointments[index] = updated_appointment
            return updated_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@appointments_api.route("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            deleted_appointment = appointments.pop(index)
            return deleted_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")


