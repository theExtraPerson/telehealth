from flask import Blueprint, render_template
from flask_jwt_extended import current_user

from app.api.appointments import appointments
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.user import User

doctor_dashboard = Blueprint('doctor-dashboard', __name__)

@doctor_dashboard.route('/dashboard')
def dashboard():
    # Fetch doctor's appointments and prescriptions
    appointments = appointments.query.filter_by(doctor_id=current_user.id).all()
    prescriptions = prescriptions.query.filter_by(doctor_id=current_user.id).all()
    return render_template('doctor_dashboard.html', appointments=appointments, prescriptions=prescriptions)

@doctor_dashboard.route('/collaborate/<int:doctor_id>')
def collaborate(doctor_id):
    # Doctor-to-doctor collaboration logic
    doctor = User.query.get_or_404(doctor_id)
    return render_template('collaboration.html', doctor=doctor)
