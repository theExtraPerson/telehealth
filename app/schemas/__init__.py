from flask import Blueprint

schemas_bp = Blueprint('schemas', __name__)

# Import all the schemas here
# from .example_schema import ExampleSchema

__all__ = ['schemas_bp']