import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

import logging

logging.basicConfig(level=logging.INFO)

# Initialising extensions
csrf = CSRFProtect()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
     # Path for refresh tokens

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app)

    from app.api import api
    app.register_blueprint(api, url_prefix='/api')

    from app.services import services
    app.register_blueprint(services, url_prefix='/services')

    from app.utils import utils
    app.register_blueprint(utils, url_prefix='/utils')

    from app.schemas import schemas
    app.register_blueprint(schemas, url_prefix='/schemas')

    from app.routes import routes
    app.register_blueprint(routes, url_prefix='/routes')

    from app.api.appointments import appointments_api
    app.register_blueprint(appointments_api, url_prefix='/appointments')

    from app.routes.user_dashboard import user_dashboard
    app.register_blueprint(user_dashboard, url_prefix='/user')

    from app.routes.doctor_dashboard import doctor_dashboard
    app.register_blueprint(doctor_dashboard, url_prefix='/doctor')

    from app.routes.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.payment import payment
    app.register_blueprint(payment, url_prefix='/payment')

    from app.display import display
    app.register_blueprint(display, url_prefix='/display')

    with app.app_context():
        from app.models.user import User, Doctor, Patient, Admin
        from app.models.appointment import Appointment
        from app.models.prescription import Prescription
        from app.models.medical_record import MedicalRecord
        from app.models.payments import Payment

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    login_manager.login_view = "auth_login"
    login_manager.login_message = "Please login to access this page."

    return app


# def root_path():
#     return None
class Base:
    metadata = None


def get_db():
    return None