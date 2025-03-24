from flask import Blueprint

services = Blueprint('services', __name__)

def init_app(app):
    app.register_blueprint(services)