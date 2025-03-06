from flask import Blueprint

services_bp = Blueprint('services', __name__)

def init_app(app):
    app.register_blueprint(services_bp)