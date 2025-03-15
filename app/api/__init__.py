from flask import Blueprint

api_bp = Blueprint('api', __name__)

from . import auth, user, prescriptions, messages, appointments, notifications, register
