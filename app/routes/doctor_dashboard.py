from flask import Blueprint, render_template
from flask_jwt_extended import current_user

from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.user import User

doctor_dashboard = Blueprint('doctor-dashboard', __name__)

@doctor_dashboard.route('/doctor/dashboard')
def dashboard():
    # Fetch doctor's appointments and prescriptions
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(doctor_id=current_user.id).all()
    return render_template('doctor_dashboard.html', appointments=appointments, prescriptions=prescriptions)

@doctor_dashboard.route('/collaborate/<int:doctor_id>')
def collaborate(doctor_id):
    # Doctor-to-doctor collaboration logic
    doctor = User.query.get_or_404(doctor_id)
    return render_template('collaboration.html', doctor=doctor)

@doctor_dashboard.route('/doctor/appointments', methods=['GET', 'POST'])
def manage_appointments():
    return 'Manage Appointments API'

@doctor_dashboard.route('/doctor/teleconference', methods=['POST'])
def start_teleconference():
    # Logic to start teleconferencing
    return "Start Teleconference API"

@doctor_dashboard.route('/doctor/prescriptions', methods=['GET', 'POST'])
def manage_prescriptions():
    # Logic to handle prescriptions
    return "Manage Prescriptions API"

@doctor_dashboard.route('/doctor/medical-records', methods=['GET'])
def view_medical_records():
    # Logic to fetch medical records
    return "View Medical Records API"


