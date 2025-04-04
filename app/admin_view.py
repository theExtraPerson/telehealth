from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models.user import Doctor, Patient, Admin as AdminUser
from app.models.appointment import Appointment
from app.models.prescription import Prescription
from app.models.payments import Payment
from app import db

admin_interface = Admin(name="Admin Dashboard", template_mode="bootstrap4")

def init_admin_views(app):
    admin_interface.init_app(app)

    admin_interface.add_view(ModelView(Doctor, db.session))
    admin_interface.add_view(ModelView(Patient, db.session))
    admin_interface.add_view(ModelView(Appointment, db.session))
    admin_interface.add_view(ModelView(Prescription, db.session))
    admin_interface.add_view(ModelView(Payment, db.session))
    admin_interface.add_view(ModelView(AdminUser, db.session, name="Admin Users"))
    admin_interface.add_view(ModelView(Prescription, db.session, name="Medical Records"))
