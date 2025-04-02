from flask import Blueprint, render_template, flash
from flask_jwt_extended import current_user, jwt_required, get_jwt_identity

from app import db
from app.forms import AppointmentForm
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.user import Patient, Doctor

user_dashboard = Blueprint('user_dashboard', __name__, template_folder='../../templates')

@user_dashboard.route('/dashboard')
@jwt_required()
def dashboard():
    # Fetch patients appointments and prescriptions
    current_user = get_jwt_identity()
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()
    render_template('user_dashboard.html', appointments=appointments, prescriptions=prescriptions)

@user_dashboard.route('/appointments/book')
def book_appointment():
    form = AppointmentForm()

    form.patient_id.choices = [(p.id, p.name) for p in Patient.query.all()]
    form.doctor_id.choices = [(d.id, f'Dr. {d.name} - {d.speciality}') for d in Doctor.query.all()]

    if form.validate_on_submit():
        new_appointment = Appointment(
            patient_id=form.patient_id.data,
            doctor_id=form.doctor_id.data,
            appointment_date=form.appointment_date.data,
            description=form.description.data
        )
        db.session.add(new_appointment)
        db.session.commit()
        flash('Appointment booked successfully!')

    return render_template('book_appointment.html', form=form)

@user_dashboard.route('/appointments/manage')
def manage_appointments():
    return render_template('manage_appointments.html')

@user_dashboard.route('/doctors/search')
def search_doctors():
    return render_template('search_doctors.html')

@user_dashboard.route('/prescriptions/refill')
def prescription_refill():
    return render_template('prescription_refill.html')

@user_dashboard.route('/payments')
def payments():
    return render_template('payments.html')

@user_dashboard.route('/records')
def medical_records():
    return render_template('medical_records.html')