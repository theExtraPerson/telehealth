from flask import Blueprint, render_template, jsonify, request
# from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.user import User
from flask_login import current_user
from flask_login import login_required

doctor_dashboard = Blueprint('doctor_dashboard', __name__, template_folder='../../templates')


# Secure route for doctor dashboard
@doctor_dashboard.route('/doctor/dashboard')
@login_required
def dashboard():

    # verify_jwt_in_request()

    user_id = current_user()
    if not user_id:
        return jsonify({"msg": "Unauthorized access. Please log in."}), 401

    appointments = Appointment.query.filter_by(doctor_id=user_id).all()
    prescriptions = Prescription.query.filter_by(doctor_id=user_id).all()
    return render_template('doctor_dashboard.html', appointments=appointments, prescriptions=prescriptions)


# Secure route for doctor collaboration
@doctor_dashboard.route('/collaborate/<int:doctor_id>')
@login_required
def collaborate(doctor_id):
    user_id = current_user()
    if not user_id:
        return jsonify({"msg": "Unauthorized access. Please log in."}), 401

    doctor = User.query.get_or_404(doctor_id)
    return render_template('collaboration.html', doctor=doctor)


# Manage appointments route
@doctor_dashboard.route('/doctor/appointments', methods=['GET', 'POST'])
@login_required
def manage_appointments():
    return render_template('consultation.html')


# Start teleconference route
@doctor_dashboard.route('/doctor/teleconference', methods=['GET', 'POST'])
@login_required
def start_teleconference():
    return jsonify({"msg": "Start Teleconference API"})


# Manage prescriptions route
@doctor_dashboard.route('/doctor/prescriptions', methods=['GET', 'POST'])
@login_required
def manage_prescriptions():
    return jsonify({"msg": "Manage Prescriptions API"})


# View medical records route
@doctor_dashboard.route('/doctor/medical-records', methods=['GET'])
@login_required
def view_medical_records():
    return jsonify({"msg": "View Medical Records API"})


