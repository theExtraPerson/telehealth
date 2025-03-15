from flask import Flask, g, app
from app import create_app, db

from flask import Flask
from app import create_app
from app.api import api_bp
from app.services import services_bp
from app.utils import utils_bp
from app.schemas import schemas_bp
from app.routes import routes_bp

def create_app():
    app = Flask(__name__)

    # Register blueprints
    app.register_blueprint(routes_bp, prefic='/routes')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(services_bp, url_prefix='/services')
    app.register_blueprint(utils_bp, url_prefix='/utils')
    app.register_blueprint(schemas_bp, url_prefix='/schemas')

    @app.before_first_request
    def create_tables():
        db.create_all()

    return app

def get_db():
    if 'db' not in g:
        g.db = db.session
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)