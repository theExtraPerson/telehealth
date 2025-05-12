from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy import func, or_

from app import db
from app.models.appointment import Appointment
from app.models.payments import Payment
from app.models.prescription import Prescription
from app.models.user import User, Doctor, Admin
from app.models.message import Message

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")

# Admin Dashboard Route
@admin_bp.route("/admin")
@login_required
def dashboard():
    users = User.query.all()
    return render_template("admin/dashboard.html",
                           doctors=Doctor.query.all(),
                           patients=User.query.filter_by(role="patient").all(),
                           appointments=Appointment.query.all(),
                           prescriptions=Prescription.query.all(),
                           payments=Payment.query.all())

#Add user
@admin_bp.route('/add-user', methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not username or not email or not password:
        flash('All field are required', 'error')
        return redirect(url_for('admin.dashboard'))

    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    flash('User added successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route("/delete_user/<int:doctor_id>", methods=['POST'])
@login_required
# admin_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f"User {user_to_delete.username} deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting user: {str(e)}", "danger")
    
    if user_to_delete.role == 'doctor':
        return redirect(url_for('admin.manage_doctors'))
    elif user_to_delete.role == 'patient':
        return redirect(url_for('admin.manage_patients'))
    else:
        return redirect(url_for('admin.dashboard'))

# Approve Doctor
@admin_bp.route("/approve_doctor/<int:doctor_id>")
@login_required
def approve_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.approved = True
    db.session.commit()
    flash("Doctor approved successfully!", "success")
    return redirect(url_for("admin.dashboard"))

# Approve Appointment
@admin_bp.route("/approve_appointment/<int:appointment_id>")
@login_required
def approve_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.approved = True
    db.session.commit()
    flash("Appointment approved successfully!", "success")
    return redirect(url_for("admin.dashboard"))

# Fetch all appointments
@admin_bp.route("/appointments")
@login_required
def fetch_appointments():
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()

    return render_template('admin/appointments.html', appointments=appointments)

# Manage Prescriptions
@admin_bp.route("/manage_prescriptions")
@login_required
def manage_prescriptions():
    return render_template("admin/prescriptions.html", prescriptions=Prescription.query.all())

# Manage Payments
@admin_bp.route("/manage_payments")
@login_required
def manage_payments(calender=None):
    payments = Payment.query.order_by(Payment.created_at.desc()).all()

    #Summary metric
    total_amount = db.session.query(func.sum(Payment.total_amount)).scalar() or 0
    success_count = Payment.query.filter_by(status="success").count()
    pending_count = Payment.query.filter_by(status="pending").count()
    failed_count = Payment.query.filter_by(status="failed").count()

    monthly_stats = (
        db.session.query(func.extract('month', Payment.created_at), func.sum(Payment.total_amount))
    .group_by(func.extract('month', Payment.created_at))
    .order_by(func.extract('month', Payment.created_at))
    .all()
    )
    months = [calender.month_name[int(row[0])] for row in monthly_stats]
    monthly_data = [float(row[1]) for row in monthly_stats]

    return render_template("admin/payments.html",
                           payments=payments,
                           total_amount=total_amount,
                           success_count=success_count,
                           pending_count=pending_count,
                           failed_count=failed_count,
                           months=months,
                           monthly_data=monthly_data,
                           )

# Manage patients
@admin_bp.route("/manage_patients")
@login_required
def manage_patients():
    search_query = request.args.get('search')
    patients_query = User.query.filter_by(role='patient')
    if search_query:
        try:
            search_id = int(search_query)
            patients_query = patients_query.filter(or_(
                User.id == search_id,
                User.username.ilike(f"%{search_query}%")
            ))
        except ValueError:
            pass
        patients_query = patients_query.filter(User.username.ilike(f"%{search_query}%"))
    patients = patients_query.order_by(User.id.desc()).all()
    return render_template("admin/patients.html", patients=patients, search_query=search_query)

# Manage Doctors
@admin_bp.route("/manage_doctors")
@login_required
def manage_doctors():
    search_query = request.args.get('search')
    doctors_query = User.query.filter_by(role='doctor')
    if search_query:
        try:
            search_id = int(search_query)
            doctors_query = doctors_query.filter(or_(
                User.id == search_id,
                User.username.ilike(f"%{search_query}%")
            ))
        except ValueError:
            doctors_query = doctors_query.filter(or_(
                User.username.ilike(f"%{search_query}%"),
                User.email.ilike(f"%{search_query}%")
            ))

    doctors = doctors_query.order_by(User.id.desc()).all()
    return render_template("admin/doctors.html", doctors=doctors, search_query=search_query)


@admin_bp.route("/toggle_doctor_active/<int:doctor_id>", methods=['POST'])
@login_required
# @admin_required
def toggle_doctor_active(doctor_id):
    doctor = User.query.filter_by(id=doctor_id, role='doctor').first_or_404()
    doctor.active = not doctor.active
    try: 
        db.session.commit()
        status = 'activated' if doctor.active else 'deactivated'
        flash(f"Doctor {doctor.username} has been {status}.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating doctor status: {str(e)}", "danger")
    return redirect(url_for('admin.manage_doctors'))

@admin_bp.route("/edit_doctor/<int:doctor_id>", methods=['POST'])
@login_required
def edit_doctor(doctor_id):
    doctor = User.query.get_or_404(doctor_id)
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not username or not email or not password:
        flash('All fields are required', 'error')
        return redirect(url_for('admin.manage_doctors'))

    doctor.username = username
    doctor.email = email
    doctor.password = password

    db.session.commit()
    flash('Doctor updated successfully!', 'success')
    return redirect(url_for('admin.manage_doctors'))


# Notifications
@admin_bp.route('/notifications', methods=['GET'])
@login_required
def view_notifications():
    # Fetch all notifications from the database
    notifications = Message.query.order_by(Message.created_at.desc).all()

    # Categorize notifications
    prescription_requests = [n for n in notifications if n.category == 'prescription_request']
    appointment_notifications = [n for n in notifications if n.category == 'appointment']
    doctor_updates = [n for n in notifications if n.category == 'doctor_update']
    patient_registrations = [n for n in notifications if n.category == 'patient_registration']
    complaints = [n for n in notifications if n.category == 'complaint']
    general_notifications = [n for n in notifications if n.category == 'general']

    return render_template(
        'admin/notifications.html',
        prescription_requests=prescription_requests,
        appointment_notifications=appointment_notifications,
        doctor_updates=doctor_updates,
        patient_registrations=patient_registrations,
        complaints=complaints,
        general_notifications=general_notifications
    )

@admin_bp.route('/send_message', methods=['GET', 'POST'])
@login_required
def send_message():
    if request.method == 'POST':
        recipient_type = request.form.get('recipient_type')
        recipient_id = request.form.get('recipient_id')
        message = request.form.get('message')
        platform = request.form.get('platform')

        if not recipient_type or not recipient_id or not message or not platform:
            flash('All fields are required', 'danger')
            return redirect(url_for('admin.send_message'))

        recipient = None
        if recipient_type == 'doctor':
            recipient = Doctor.query.get(recipient_id)
        elif recipient_type == 'patient':
            recipient = User.query.filter_by(id=recipient_id, role='patient').first()

        if not recipient:
            flash('Recipient not found', 'danger')
            return redirect(url_for('admin.send_message'))

        # Simulate sending the message
        if platform == 'direct':
            # Logic for direct messaging
            flash(f'Message sent directly to {recipient.username}', 'success')
        elif platform == 'whatsapp':
            # Logic for sending via WhatsApp
            flash(f'Message sent to {recipient.username} via WhatsApp', 'success')
        elif platform == 'telegram':
            # Logic for sending via Telegram
            flash(f'Message sent to {recipient.username} via Telegram', 'success')
        else:
            flash('Invalid platform selected', 'danger')

        return redirect(url_for('admin.dashboard'))

    doctors = Doctor.query.all()
    patients = User.query.filter_by(role='patient').all()
    return render_template('admin/send_message.html', doctors=doctors, patients=patients)

# Reports
@admin_bp.route('/reports')
@login_required
def generate_reports():
    # Monthly payment trends
    monthly_payment_stats = (
        db.session.query(func.extract('month', Payment.created_at), func.sum(Payment.total_amount))
        .group_by(func.extract('month', Payment.created_at))
        .order_by(func.extract('month', Payment.created_at))
        .all()
    )
    payment_months = [int(row[0]) for row in monthly_payment_stats]
    payment_totals = [float(row[1]) for row in monthly_payment_stats]

    # Number of daily users
    daily_user_stats = (
        db.session.query(func.date(User.created_at), func.count(User.id))
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at))
        .all()
    )
    user_dates = [row[0] for row in daily_user_stats]
    user_counts = [row[1] for row in daily_user_stats]

    # Business intelligence: Health informatics
    total_appointments = Appointment.query.count()
    total_prescriptions = Prescription.query.count()
    total_doctors = Doctor.query.count()
    total_patients = User.query.filter_by(role="patient").count()

    return render_template(
        "admin/reports.html",
        payment_months=payment_months,
        payment_totals=payment_totals,
        user_dates=user_dates,
        user_counts=user_counts,
        total_appointments=total_appointments,
        total_prescriptions=total_prescriptions,
        total_doctors=total_doctors,
        total_patients=total_patients,
    )


# Settings
@admin_bp.route("/settings")
@login_required
def settings():
    return render_template("admin/settings.html")


