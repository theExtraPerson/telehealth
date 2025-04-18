from flask import Blueprint, render_template, jsonify, request, redirect, url_for

from app.forms import DoctorProfileForm
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.medical_record import MedicalRecord
from app.models.user import User
from flask_login import current_user, login_required

# Blueprint for doctor dashboard routes
doctor_dashboard = Blueprint('doctor_dashboard', __name__, template_folder='../../templates')


@doctor_dashboard.route('/doctor/dashboard')
@login_required
def dashboard():
    doctor_id = current_user.id
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
    prescriptions = Prescription.query.filter_by(doctor_id=doctor_id).all()
    medical_records = MedicalRecord.query.filter_by(doctor_id=doctor_id).all()

    return render_template(
        'doctor/doctor_dashboard.html',
        appointments=appointments,
        prescriptions=prescriptions,
        medical_records=medical_records,
        doctor=current_user
    )


@doctor_dashboard.route('/doctor/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    doctor = current_user
    form = DoctorProfileForm(obj=doctor)

    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.email = request.form.get('email')
        doctor.bio = request.form.get('bio')
        doctor.specialty = request.form.get('specialty')
        doctor.consultation_fee = request.form.get('consultation_fee')

        # Handle availability switch
        doctor.is_available = 'is_available' in request.form

        # Handle schedule from form
        schedule = {}
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            start = request.form.get(f'schedule[{day}][start]')
            end = request.form.get(f'schedule[{day}][end]')
            schedule[day] = {"start": start, "end": end}

        # Store schedule as JSON string
        import json
        doctor.schedule = json.dumps(schedule)

        doctor.save()
        return redirect(url_for('doctor_dashboard.dashboard'))

    # Load schedule for display
    try:
        import json
        schedule = json.loads(doctor.schedule) if doctor.schedule else {}
    except Exception:
        schedule = {}

    # Fill any missing days with empty times
    default_schedule = {
        day.lower(): {"start": "", "end": ""}
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    }
    for day in default_schedule:
        schedule.setdefault(day.lower(), default_schedule[day.lower()])

    return render_template('doctor/edit_profile.html', doctor=doctor, schedule=schedule, form=form)



@doctor_dashboard.route('/doctor/collaborate/<int:doctor_id>')
@login_required
def collaborate(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    return render_template('doctor/collaboration.html', doctor=doctor)


@doctor_dashboard.route('/doctor/appointments')
@login_required
def manage_appointments():
    appointments = Appointment.query.filter_by(doctor_id=current_user.id).all()
    return render_template('doctor/appointments.html', appointments=appointments)


@doctor_dashboard.route('/doctor/prescriptions')
@login_required
def manage_prescriptions():
    prescriptions = Prescription.query.filter_by(doctor_id=current_user.id).all()
    return render_template('doctor/prescriptions.html', prescriptions=prescriptions)


@doctor_dashboard.route('/doctor/medical-records')
@login_required
def view_medical_records():
    medical_records = MedicalRecord.query.filter_by(doctor_id=current_user.id).all()
    return render_template('doctor/medical_records.html', records=medical_records)


@doctor_dashboard.route('/doctor/teleconference')
@login_required
def start_teleconference():
    return render_template('doctor/teleconference.html')