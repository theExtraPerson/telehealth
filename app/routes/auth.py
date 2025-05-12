from flask import Blueprint, request, jsonify, url_for, redirect, render_template, flash
from flask_login import login_required, logout_user, login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi import APIRouter

from app import db
from app.models.user import User
from ..forms import RegistrationForm, LoginForm

auth = Blueprint("auth", __name__, template_folder="../../templates/auth")
router = APIRouter(prefix="/auth", tags=["auth"])

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'GET':
        return render_template('auth/register.html', form=form)

    # Handle AJAX form submission
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        role = form.role.data

        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'errors': {'username': 'User already exists'}
            }), 400

        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success' )

        return redirect(url_for('auth.login'))
        # return jsonify({
        #     'success': True,
        #     'message': 'Registration successful!',
        #     'redirect': url_for('auth.login')
        # })

    flash('Registration failed! Please try again')
    return render_template('auth/register.html')
    # Form validation failed
    # return jsonify({
    #     'success': False,
    #     'errors': form.errors
    # }), 400



@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        # If user is already logged in, redirect to appropriate dashboard
        if current_user.is_authenticated:
            return redirect_to_dashboard(current_user.role)
        return render_template('auth/login.html', form=form)

    # Handle AJAX form submission
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data

        user = User.query.filter_by(username=username, role=role).first()

        if user and check_password_hash(user.password_hash, password):
            if user.role == form.role.data:
                login_user(user)
                flash('Login successful!', 'success')
                return redirect_to_dashboard(user.role)

        flash('Login failed!, Please try again later.', 'warning')
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form)


@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


# Helper functions
def get_dashboard_url(role):
    """Return the appropriate dashboard URL based on role"""
    role_dashboards = {
        'admin': 'admin.dashboard',
        'doctor': 'doctor_dashboard.dashboard',
        'patient': 'user_dashboard.dashboard'
    }
    return url_for(role_dashboards.get(role, 'auth.login'))


def redirect_to_dashboard(role):
    """Redirect to the appropriate dashboard based on role"""
    return redirect(get_dashboard_url(role))

