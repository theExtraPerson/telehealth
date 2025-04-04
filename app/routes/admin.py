from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

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
    return render_template("admin/dashboard.html",
                           doctors=Doctor.query.all(),
                           patients=User.query.filter_by(role="patient").all(),
                           appointments=Appointment.query.all(),
                           prescriptions=Prescription.query.all(),
                           payments=Payment.query.all())

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
def manage_payments():
    return render_template("admin/payments.html", payments=Payment.query.all())

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
