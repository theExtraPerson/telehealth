from flask import Blueprint, render_template
from flask_jwt_extended import current_user

from app.models.appointment import Appointment
from app.models.prescription import Prescription

user_dashboard = Blueprint('user_dashboard', __name__)

@user_dashboard.route('/dashboard')
def dashboard():
    # Fetch patients appointments and prescriptions
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()
    render_template('user_dashboard.html', appointments=appointments, prescriptions=prescriptions)

@user_dashboard.route('/appointments/book')
def book_appointment():
    return render_template('book_appointment.html')

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