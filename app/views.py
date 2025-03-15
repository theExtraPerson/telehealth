from flask import Flask, render_template
from . import main_bp

@main_bp.route('/')
def homepage():
    return render_template('main/home.html')

