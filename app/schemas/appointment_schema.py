from marshmallow import Schema, fields


class AppointmentSchema(Schema):
    id = fields.Int(required=False, description="The unique identifier of the appointment")
    patient_name = fields.Str(required=True, description="The name of the patient")
    doctor_name = fields.Str(required=True, description="The name of the doctor")
    appointment_date = fields.DateTime(required=True, description="The date and time of the appointment")
    reason = fields.Str(required=False, allow_none=True, description="The reason for the appointment")
    status = fields.Str(required=False, default="scheduled", description="The status of the appointment")
