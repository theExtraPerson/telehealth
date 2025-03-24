from flask import Blueprint, render_template
from app.models.appointment import Appointment
from app.models.prescription import Prescription

user_dashboard = Blueprint('user_dashboard', __name__)

@user_dashboard.route('/dashboard')
def dashboard():
    # Fetch patients appointments and prescriptions
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()
    render_template('user_dashboard.html', appointments=appointments, prescriptions=prescriptions)