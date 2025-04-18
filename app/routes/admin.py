from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from sqlalchemy import func

from app import db
from app.models.appointment import Appointment
from app.models.payments import Payment
from app.models.prescription import Prescription
from app.models.user import User, Doctor

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

# Delete User
@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted', 'info')
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
    total_amount = db.session.query(func.sum(Payment.amount)).scalar() or 0
    success_count = Payment.query.filter_by(status="success").count()
    pending_count = Payment.query.filter_by(status="pending").count()
    failed_count = Payment.query.filter_by(status="failed").count()

    monthly_stats = (
        db.session.query(func.extract('month', Payment.date), func.sum(Payment.amount))
    .group_by(func.extract('month', Payment.date))
    .order_by(func.extract('month', Payment.date))
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

# Notifications
@admin_bp.route('/send_notifiction', methods=['GET', 'POST'])
def send_notification():
    target = request.form.get('target')
    message = request.form.get('message')

    if not message:
        flash('Message is required', 'danger')
        return redirect(url_for('admin.dashboard'))

    if target == 'all':
        recepients = User.query.all()
    elif target == 'patients':
        recepients = User.query.filter_by(role='patient').all()
    elif target == 'doctors':
        recepients = User.query.filter_by(role='doctor').all()
    else:
        flash('Invalid target group', 'warning')
        return redirect(url_for('admin.dashboard'))

    for user in recepients:
        send_notification(user, message)

    flash(f'Notification sent to {target}.', 'success')
    return redirect(url_for('admin.dashboard'))


# Reports
@admin_bp.route("/reports")
@login_required
def reports():
    return render_template("admin/reports.html")

# Settings
@admin_bp.route("/settings")
@login_required
def settings():
    return render_template("admin/settings.html")
