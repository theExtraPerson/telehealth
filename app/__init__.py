
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_db():
    return current_app.db.session

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    db.init_app(app)
    return app