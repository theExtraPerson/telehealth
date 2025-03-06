from flask import Blueprint

utils_bp = Blueprint('utils', __name__)

from . import some_module  # Import your utility modules here