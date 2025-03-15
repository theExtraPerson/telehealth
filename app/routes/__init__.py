from flask import Blueprint
from . import views

routes = Blueprint('routes', __name__)

import app.routes.main
