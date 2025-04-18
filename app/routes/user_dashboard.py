import os
from flask import (
    Blueprint, render_template, flash, request,
    jsonify, redirect, send_file, url_for, abort, current_app
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask_wtf.csrf import generate_csrf
from app import db
from app.forms import AppointmentForm, ProfileForm
from app.models import appointment
from app.models.appointment import Appointment
from app.models.payments import Payment
from app.models.prescription import Prescription
from app.models.user import Patient, Doctor, User
from app.models.message import Message
from app.services.medical_records_service import MedicalRecordsService

user_dashboard = Blueprint('user_dashboard', __name__, template_folder='../../templates')

def _get_service():
    return MedicalRecordsService(db.session)

def get_recent_prescriptions(user_id):
    return Prescription.query.filter_by(patient_id=user_id).order_by(Prescription.date_prescribed.desc()).limit(5).all()

def get_last_payment(user_id):
    if hasattr(current_user, 'payments'):
        return sorted(current_user.payments, key=lambda p: p.date, reverse=True)[0] if current_user.payments else None
    return None

def get_next_appointment(user_id):
    return Appointment.query.filter_by(patient_id=user_id).order_by(Appointment.appointment_date.asc()).first()


def get_last_appointment(user_id):
    return Appointment.query.filter_by(patient_id=user_id).order_by(Appointment.appointment_date.desc()).first()


@user_dashboard.route('/dashboard')
@login_required
def dashboard():
    user = current_user
    # Get logged-in user's appointments & prescriptions
    appointments = Appointment.query.filter_by(patient_id=current_user.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()

    next_appointment = get_next_appointment(user.id)
    last_payment = get_last_appointment(user.id)
    recent_prescriptions = get_recent_prescriptions(user.id)

    if request.accept_mimetypes.best == 'application/json':
        return jsonify({
            'appointments': [a.to_dict() for a in appointments],
            'prescriptions': [p.to_dict() for p in prescriptions]
        })

    return render_template(
        'user/user_dashboard.html',
        user=user,
        appointments=appointments,
        prescriptions=prescriptions,
        next_appointment=next_appointment,
        last_payment=last_payment,
        recent_prescriptions=recent_prescriptions)



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
    doctors = Doctor.query.filter(User.username.ilike(f'%{query}%')).all()

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

@user_dashboard.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    payments = current_user.payments if hasattr(current_user, 'payments') else []
    last_payment = get_last_payment(current_user.id)
    return render_template('user/payments.html', payments=payments, last_payment=last_payment)


@user_dashboard.route('/payments/pay/<int:payment_id>', methods=['GET', 'POST'])
@login_required
def make_payment(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    if payment.user_id != current_user.id:
        flash("Unauthorized payment attempt.", "danger")
        return redirect(url_for("payments.payments_overview"))

    if request.method == "POST":
        method = request.form.get("method")
        success = process_payment(user=current_user, payment=payment, method=method)

        if success:
            flash("Payment successful!", "success")
            return redirect(url_for("payments.payments_overview"))
        else:
            flash("Payment failed. Try again.", "danger")

    return render_template("user/payments.html", payment=payment)



@user_dashboard.route('/', methods=['GET'])
@login_required
def list_records():
    """List all medical records for the current patient."""
    service = _get_service()
    records = service.get_medical_records(user_id=current_user.id)

    if request.accept_mimetypes.best == 'application/json':
        return jsonify([r.to_dict() for r in records])

    return render_template('user/medical_records.html', records=records)


@user_dashboard.route('/<int:record_id>', methods=['GET'])
@login_required
def view_record(record_id):
    """View details of a single medical record."""
    service = _get_service()
    record = service.get_medical_record_by_id(record_id, current_user.id)
    if not record:
        abort(404, description="Record not found.")

    if request.accept_mimetypes.best == 'application/json':
        return jsonify(record.to_dict())

    return render_template('user/record_detail.html', record=record)


@user_dashboard.route('/download/<int:record_id>', methods=['GET'])
@login_required
def download_record(record_id):
    """Download the file associated with a medical record."""
    service = _get_service()
    file_path = service.get_file_path(record_id, current_user.id)
    if not file_path or not os.path.exists(file_path):
        abort(404, description="File not found.")

    return send_file(
        file_path,
        as_attachment=True,
        download_name=os.path.basename(file_path)
    )


@user_dashboard.route('/upload', methods=['POST'])
@login_required
def upload_record():
    """Handle file upload and create a new medical record."""
    file = request.files.get('file')
    if not file:
        flash("No file uploaded.", "danger")
        return redirect(url_for('user_dashboard.list_records'))

    # Secure and save
    filename = secure_filename(file.filename)
    upload_dir = current_app.config['MEDICAL_RECORDS_UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Metadata from form
    description  = request.form.get('description', '')
    doctor_name  = request.form.get('doctor_name', '')
    date_of_visit = request.form.get('date_of_visit')

    service = _get_service()
    service.create_medical_record_with_file(
        description=description,
        doctor_name=doctor_name,
        date_of_visit=date_of_visit,
        file_path=filepath,
        user_id=current_user.id
    )

    flash("Medical record uploaded successfully.", "success")
    return redirect(url_for('user_dashboard.list_records'))


@user_dashboard.route('/share', methods=['POST'])
@login_required
def share_record():
    """Share a record via email to another user."""
    record_id = request.form.get('record_id', type=int)
    email     = request.form.get('email')

    service = _get_service()
    result = service.share_medical_record(record_id, email, current_user.id)

    flash(result["message"], "info")
    return redirect(url_for('user_dashboard.list_records'))


@user_dashboard.route('/grant-access', methods=['POST'])
@login_required
def grant_access():
    """Grant a doctor access to this record."""
    record_id = request.form.get('record_id', type=int)
    doctor_id = request.form.get('doctor_id', type=int)

    service = _get_service()
    result = service.grant_doctor_access(record_id, doctor_id, current_user.id)

    flash(result["message"], "info")
    return redirect(url_for('user_dashboard.list_records'))
@user_dashboard.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.age = form.age.data
        current_user.gender = form.gender.data
        current_user.weight = form.weight.data
        current_user.height = form.height.data
        current_user.blood_type = form.blood_type.data
        current_user.allergies = form.allergies.data
        current_user.medical_conditions = form.medical_conditions.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('user_dashboard.dashboard'))

    return render_template('user/edit_profile.html', form=form)

@user_dashboard.route('/payments/invoice/<int:payment_id>')
@login_required
def invoice(payment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.user_id != current_user.id:
        abort(403)

    doctor = appointment.doctor
    specialty = doctor.specialty
    total_price = specialty.price

    return render_template(
        'user/invoice.html',
        doctor=doctor,
        specialty=specialty,
        appointment=appointment,
        total=total_price
    )

@user_dashboard.route('/notifications')
@login_required
def notifications():
    notifications = Message.query.filter_by(user_id=current_user.id).order_by(Message.timestamp.desc()).all()
    unread_count = sum(1 for n in notifications if not n.seen)

    return render_template(
        'user/notifications.html',
        notifications=notifications,
        unread_notifications_count=unread_count
    )
