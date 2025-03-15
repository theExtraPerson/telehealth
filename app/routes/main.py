
from flask import Flask, render_template, Blueprint

main = Blueprint('main_bp', __name__)

@main.route('/')
def home():
    return render_template('main/home.html')

@main.route('/index')
def index():
    return render_template('index.html')

