from flask import (
    Blueprint, render_template, flash, request,
    jsonify, redirect, url_for
)
from flask_login import login_required, current_user
from app import db
from app.forms import AppointmentForm
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.user import Patient, Doctor

user_dashboard = Blueprint('user_dashboard', __name__, template_folder='../../templates')


@user_dashboard.route('/dashboard')
@login_required
def dashboard():
    # Get logged-in user's appointments & prescriptions
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()

    if request.accept_mimetypes.best == 'application/json':
        return jsonify({
            'appointments': [a.to_dict() for a in appointments],
            'prescriptions': [p.to_dict() for p in prescriptions]
        })

    return render_template('user/user_dashboard.html', appointments=appointments, prescriptions=prescriptions)


@user_dashboard.route('/appointments/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    form = AppointmentForm()

    # Choices from DB
    form.patient_id.choices = [(current_user.id, current_user.username)]
    form.doctor_id.choices = [
        (d.id, f'Dr. {d.name} - {d.speciality}') for d in Doctor.query.all()
    ]

    if request.method == 'POST':
        if form.validate_on_submit():
            appointment = Appointment(
                patient_id=current_user.id,
                doctor_id=form.doctor_id.data,
                appointment_date=form.appointment_date.data,
                description=form.description.data
            )
            db.session.add(appointment)
            db.session.commit()
            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('user_dashboard.dashboard'))
        else:
            flash('Failed to book appointment. Please correct the errors.', 'danger')

    return render_template('user/book_appointment.html', form=form)


@user_dashboard.route('/appointments/manage')
@login_required
def manage_appointments():
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()

    if request.accept_mimetypes.best == 'application/json':
        return jsonify([a.to_dict() for a in appointments])

    return render_template('user/manage_appointments.html', appointments=appointments)


@user_dashboard.route('/doctors/search')
@login_required
def search_doctors():
    query = request.args.get('q', '')
    doctors = Doctor.query.filter(Doctor.name.ilike(f'%{query}%')).all()

    if request.accept_mimetypes.best == 'application/json':
        return jsonify([{'id': d.id, 'name': d.name, 'speciality': d.speciality} for d in doctors])

    return render_template('user/search_doctors.html', doctors=doctors, query=query)


@user_dashboard.route('/prescriptions/refill')
@login_required
def prescription_refill():
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()

    if request.accept_mimetypes.best == 'application/json':
        return jsonify([p.to_dict() for p in prescriptions])

    return render_template('user/prescription_refill.html', prescriptions=prescriptions)


@user_dashboard.route('/payments')
@login_required
def payments():
    payments = current_user.payments if hasattr(current_user, 'payments') else []

    if request.accept_mimetypes.best == 'application/json':
        return jsonify([p.to_dict() for p in payments])

    return render_template('user/payments.html', payments=payments)


@user_dashboard.route('/records')
@login_required
def medical_records():
    records = current_user.medical_records if hasattr(current_user, 'medical_records') else []

    if request.accept_mimetypes.best == 'application/json':
        return jsonify([r.to_dict() for r in records])

    return render_template('user/medical_records.html', records=records)
