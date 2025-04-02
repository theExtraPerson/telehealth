
from flask import Blueprint, jsonify, request, Flask, abort
from pydantic import BaseModel, ValidationError
from typing import Optional
from datetime import datetime

from app import db
from app.schemas import appointment_schema
# from app.schemas.appointment_schema import AppointmentSchema
app = Flask(__name__)
appointments_api = Blueprint('appointments_api', __name__)

appointments = []

class Appointment(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    date: datetime

@appointments_api.route("/appointments/", methods=['POST'])
def create_appointment():
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No input data provided"}), 400

        errors = appointment_schema.validate(json_data)
        if errors:
            return jsonify(errors), 400

        new_appointment = Appointment(**json_data)

        for appointment in appointments:
            if appointment.id == new_appointment.id:
                return jsonify({"error": "Appointment ID already exists"}), 400

        appointments.append(new_appointment)
        db.session.add(new_appointment)
        db.session.commit()
        return jsonify(new_appointment), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

@appointments_api.route("/appointments/", methods=['GET'])
def get_appointments():
    return jsonify([appointment.dict() for appointment in appointments])

@appointments_api.route("/appointments/<int:appointment_id>", methods=['GET'])
def get_appointment(appointment_id: int):
    for appointment in appointments:
        if appointment.id == appointment_id:
            return jsonify(appointment.dict())
    return jsonify({"error": "Appointment not found"})

@appointments_api.route("/appointments/<int:appointment_id>", methods=['PUT'])
def update_appointment(appointment_id: int, updated_appointment: Appointment):
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No input data provided"}), 400

        updated_appointment = Appointment(**json_data)

        for index, appointment in enumerate(appointments):
            if appointment.id == appointment_id:
                appointments[index] = updated_appointment
                db.session.commit()
                return jsonify(updated_appointment), 200
        return jsonify({"error": "Appointment not found"}), 404
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

@appointments_api.route("/appointments/<int:appointment_id>", methods=['DELETE'])
def delete_appointment(appointment_id: int):
    for index, appointment in enumerate(appointments):
        if appointment.id == appointment_id:
            deleted_appointment = appointments.pop(index)
            return deleted_appointment
    return jsonify({"error": "Appointment not found"}), 404

