import os
from flask import Blueprint, render_template, send_from_directory, current_app

# Define the Blueprint
main = Blueprint("main", __name__)

# Home page route
@main.route("/")
def home():
    return render_template("index.html")

# Favicon route
@main.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )

