
from flask import Blueprint

display = Blueprint('display', __name__, template_folder="display_templates", url_prefix='/display')