from flask import render_template
from .routes.main import main

@main.route('/')
def homepage():
    return render_template('main/home.html')

