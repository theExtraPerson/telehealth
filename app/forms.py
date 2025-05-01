from flask_wtf import FlaskForm
from wtforms import SelectField, DateTimeLocalField, TextAreaField, SubmitField
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.datetime import DateField, TimeField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, PasswordField, BooleanField, EmailField, TelField, FileField
from wtforms.validators import DataRequired, Email, Optional
from wtforms.widgets.core import CheckboxInput, ListWidget


class AppointmentForm(FlaskForm):
    patient_id = SelectField('Patient', coerce=int, validators=[DataRequired()])
    doctor_id = SelectField('Doctor', coerce=int, validators=[DataRequired()])
    appointment_date = DateTimeLocalField('Appointment Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Book Appointment')

class RegistrationForm(FlaskForm):
    fullname = StringField('Full Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor'), ('admin', 'Admin')], validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    dob = DateField('Date of Birth')
    address = TextAreaField('Address')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('patient', 'Patient'), ('doctor', 'Doctor'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Login')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[Optional()])
    gender = SelectField('Gender', choices=[
        ('Male', 'Male'),
        ('Female', 'Female')
    ])
    photo = FileField('Profile Photo')
    weight = IntegerField('Weight (kg)', validators=[Optional()])
    height = IntegerField('Height (cm)', validators=[Optional()])
    blood_type = SelectField('Blood Type', validators=[Optional()], choices=[
        ('A', 'A'),
        ('B', 'B'),
        ('AB', 'AB'),
        ('O', 'O')
    ])
    allergies = TextAreaField('Allergies', validators=[Optional()])
    medical_conditions = TextAreaField('Medical Conditions', validators=[Optional()])
    submit = SubmitField('Save Changes')

class DoctorProfileForm(FlaskForm):
    # Personal Information
    full_name = StringField('Full Name', validators=[DataRequired()])
    gender = StringField('Gender')
    date_of_birth = DateField('Date of Birth', format='%Y-%m-%d')
    languages_spoken = StringField('Languages Spoken')
    photo = FileField('Profile Photo')

    # Contact Information
    phone = TelField('Phone Number')
    email = EmailField('Email', validators=[Email()])

    # Professional Information
    license_number = StringField('License Number')
    medical_license = StringField('Medical License ID')
    specialty = StringField('Specialty')
    conditions_treated = TextAreaField('Conditions Treated')

    # Availability
    is_available = BooleanField('Currently Available for Consultation')
    available_days = SelectMultipleField('Available Days', choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'),
        ('Saturday', 'Saturday'), ('Sunday', 'Sunday')
    ], option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False))
    whatsapp = BooleanField('Available on WhatsApp')
    phone_call = BooleanField('Available for Phone Call')
    video_call = BooleanField('Available for Video Call')

    # Weekly Schedule (simplified)
    monday_start = TimeField('Monday Start')
    monday_end = TimeField('Monday End')
    tuesday_start = TimeField('Tuesday Start')
    tuesday_end = TimeField('Tuesday End')
    wednesday_start = TimeField('Wednesday Start')
    wednesday_end = TimeField('Wednesday End')
    thursday_start = TimeField('Thursday Start')
    thursday_end = TimeField('Thursday End')
    friday_start = TimeField('Friday Start')
    friday_end = TimeField('Friday End')
    saturday_start = TimeField('Saturday Start')
    saturday_end = TimeField('Saturday End')
    sunday_start = TimeField('Sunday Start')
    sunday_end = TimeField('Sunday End')


    bio = TextAreaField('Medical Bio / Experience')
    submit = SubmitField('Save Changes')