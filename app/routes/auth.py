from flask import Blueprint, request, jsonify, url_for, make_response, redirect
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from app import db
from app.models.user import User

auth = Blueprint("auth", __name__)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    hashed_password = generate_password_hash(password)
    new_user = User()
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    user = User.query.filter_by(username=username, role=role).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Invalid username or password"}), 401

    access_token = create_access_token(
        identity={"id": user.id, "role": user.role},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    response = jsonify({"msg": "Login successful"})
    set_access_cookies(response, access_token)

    if role == "doctor":
        return redirect(url_for("doctor_dashboard.dashboard"), code=302)
    elif role == "admin":
        return redirect(url_for('admin_panel.dashboard'), code=302)
    else:
        return redirect(url_for('user_dashboard.dashboard'), code=302)


@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    response = jsonify({"msg": "Logged out successfully"})
    unset_jwt_cookies(response)  # Remove the JWT from cookies
    return response, 200

@auth.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200


def get_current_user():
    return None