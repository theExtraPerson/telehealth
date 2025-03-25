from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

# Initialising extensions
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from app.api import api
    app.register_blueprint(api, url_prefix='/api')

    from app.services import services
    app.register_blueprint(services, url_prefix='/services')

    from app.utils import utils
    app.register_blueprint(utils, url_prefix='/utils')

    from app.schemas import schemas
    app.register_blueprint(schemas, url_prefix='/schemas')

    # from app.routes import routes
    # app.register_blueprint(routes, url_prefix='/routes')

    from app.api.appointments import appointments_api
    app.register_blueprint(appointments_api, url_prefix='/appointments')

    from app.routes.user_dashboard import user_dashboard
    app.register_blueprint(user_dashboard, url_prefix='/user')

    from app.routes.doctor_dashboard import doctor_dashboard
    app.register_blueprint(doctor_dashboard, url_prefix='/doctor')

    from app.routes.admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    from app.routes.main import main
    app.register_blueprint(main, url_prefix='/main')

    from app.routes.payment import payment
    app.register_blueprint(payment, url_prefix='/payment')

    return app


# def root_path():
#     return None