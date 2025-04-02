import os
from flask import Blueprint, render_template, send_from_directory, current_app

from app.api.user import get_current_user

# Define the Blueprint
main = Blueprint("main", __name__,static_folder="static", template_folder="../../templates/main")


# Home page route
@main.route("/", methods=['GET', 'POST'])
def index():
    return render_template("main/home.html")

@main.route("/home", methods=['GET'])
def home():
    doctor_id = get_current_user()
    return  render_template("main/index.html")

@main.route("/about", methods=['GET'])
def about():
    return render_template("main/about.html")

@main.route("/contact", methods=['GET'])
def contact():
    return render_template("main/contact.html")

@main.route("/login", methods=['GET', 'POST'])
def login():
    return render_template("main/login.html")



# Favicon route
@main.route("/favicon.ico", methods=['GET'])
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
