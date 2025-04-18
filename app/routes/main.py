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

@main.route('/about')
def about():
    return render_template("main/about.html",
        hospital_name="Konge Medical City - Hospital",
        about_description="KMC - Hospital is a modern health center focused on delivering exceptional healthcare services, combining innovation, integrity, and community trust.",
        vision="To be the preferred 'at home' centre of care with a touch of passion in healthcare delivery aiming at building legacy in human health needs for the pleasure of Allah.",
        mission="To be the leading center of excellency in providing quality , affordable and accessible healthcare that \n"
                "Patients recommend to family and friends, \n"
                "Doctors prefer for their patients, \n"
                "Purchasers select for their clients, \n"
                "Employees are proud of, and \n"
                "Investors seek for long term returns",
        core_values=[
            {"title": "Compassion", "description": "We treat all patients with kindness and empathy."},
            {"title": "Respect and Integrity", "description": "We uphold transparency and ethics in all our actions."},
            {"title": "Innovation and Excellence", "description": "We strive for the highest standards in healthcare services."},
            {"title": "Accountability and Professionalism", "description": "We ensure that all our staff are accountable and responsible." },
            {"title": "Teamwork and Patient Centric", "description": "We work together to deliver a sustainable healthcare experience."},
            {"title": "Empathy and Care", "description": "We strive for a patient-centred care environment."},
        ],
        services=[
            {"title": "Doctor Consultation", "description": "Get professional advice on prescriptions and health concerns."},
            {"title": "Dental Care Services", "description": "Extensive tooth removal and repair services."},
            {"title": "Maternal Care & Child Health", "description": "Comprehensive care for mothers and children."},
            {"title": "Surgeries", "description": "Inpatient and outpatient surgeries with expert care."},
            {"title": "Antenatal Care", "description": "Dedicated care and monitoring for expecting mothers."},
            {"title": "ENT Clinic", "description": "specialised treatment for ear, nose and throat conditions."},
            {"title": "Skin Care Clinic", "description": "Top notch skin care services by the best dermatologists."},
            {"title": "Laboratory Services", "description": "A well equipped medical diagnostics laboratory."}
        ]
    )

@main.route("/contact", methods=['GET'])
def contact():
    return render_template("main/contact.html")

# @main.route("/login", methods=['GET', 'POST'])
# def login():
#     return render_template("main/login.html")



# Favicon route
@main.route("/favicon.ico", methods=['GET'])
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )
