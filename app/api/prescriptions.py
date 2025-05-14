from flask import Blueprint, request, jsonify, abort
from app.models.prescription import Prescription
from app import db  # or however you import your SQLAlchemy instance
from app.schemas.prescription_schema import prescription_schema

prescriptions_api = Blueprint('prescriptions_api', __name__)


@prescriptions_api.route("/", method=["POST"])
def create_prescription():
    # Get JSON data from the request
    json_data = request.get_json()
    if not json_data:
        abort(400, description="No input data provided")

    # Validate input data using Marshmallow
    errors = prescription_schema.validate(json_data)
    if errors:
        return jsonify(errors), 400

    # Create a new Prescription instance using the validated data
    new_prescription = Prescription(**json_data)
    db.session.add(new_prescription)
    db.session.commit()

    # Serialize the created object and return it
    result = prescription_schema.dump(new_prescription)
    return jsonify(result), 201


@prescriptions_api.route("/", method=["GET"])
def read_prescriptions():
    # Retrieve pagination parameters from the query string
    skip = request.args.get("skip", default=0, type=int)
    limit = request.args.get("limit", default=10, type=int)

    # Query prescriptions with pagination
    prescriptions = Prescription.query.offset(skip).limit(limit).all()
    result = prescription_schema.dump(prescriptions)
    return jsonify(result), 200


@prescriptions_api.route("/<int:prescription_id>", method=["GET"])
def read_prescription(prescription_id):
    prescription = Prescription.query.get(prescription_id)
    if prescription is None:
        abort(404, description="Prescription not found")
    result = prescription_schema.dump(prescription)
    return jsonify(result), 200


@prescriptions_api.route("/<int:prescription_id>", method=["PUT"])
def update_prescription(prescription_id):
    prescription = Prescription.query.get(prescription_id)
    if prescription is None:
        abort(404, description="Prescription not found")

    json_data = request.get_json()
    if not json_data:
        abort(400, description="No input data provided")

    # Validate partial update data (allowing missing fields)
    errors = prescription_schema.validate(json_data, partial=True)
    if errors:
        return jsonify(errors), 400

    # Update the prescription instance with new values
    for key, value in json_data.items():
        setattr(prescription, key, value)

    db.session.commit()
    result = prescription_schema.dump(prescription)
    return jsonify(result), 200

@prescriptions_api.route('/<int:prescription_id>/status', methods=["PATCH"])
def update_prescription_status(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    json_data = request.get_json()
    new_status = json_data.get('status')

    valid_statuses = ['pending', 'approved', 'rejected', 'issued', 'delivered']
    if new_status not in valid_statuses:
        abort(400, description='Invalid status update')

@prescriptions_api.route("/<int:prescription_id>", method=["DELETE"])
def delete_prescription(prescription_id):
    prescription = Prescription.query.get(prescription_id)
    if prescription is None:
        abort(404, description="Prescription not found")

    db.session.delete(prescription)
    db.session.commit()
    result = prescription_schema.dump(prescription)
    return jsonify(result), 200
