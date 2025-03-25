from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models.user import User, Doctor
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.payments import Payment
from app import db

admin = Blueprint("admin", __name__, url_prefix="/admin")

@admin.route("/")
@login_required
def dashboard():
    doctors = Doctor.query.all()
    patients = User.query.filter_by(role="patient").all()
    appointments = Appointment.query.all()
    prescriptions = Prescription.query.all()
    payments = Payment.query.all()
    return render_template("admin/dashboard.html", doctors=doctors, patients=patients, appointments=appointments, prescriptions=prescriptions, payments=payments)

@admin.route("/approve_doctor/<int:doctor_id>")
@login_required
def approve_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.approved = True
    db.session.commit()
    flash("Doctor approved successfully!", "success")
    return redirect(url_for("admin.dashboard"))

@admin.route("/approve_appointment/<int:appointment_id>")
@login_required
def approve_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.approved = True
    db.session.commit()
    flash("Appointment approved successfully!", "success")
    return redirect(url_for("admin.dashboard"))

@admin.route("/manage_prescriptions")
@login_required
def manage_prescriptions():
    prescriptions = Prescription.query.all()
    return render_template("admin/prescriptions.html", prescriptions=prescriptions)

@admin.route("/manage_payments")
@login_required
def manage_payments():
    payments = Payment.query.all()
    return render_template("admin/payments.html", payments=payments)

@admin.route("/reports")
@login_required
def reports():
    return render_template("admin/reports.html")

@admin.route("/settings")
@login_required
def settings():
    return render_template("admin/settings.html")
