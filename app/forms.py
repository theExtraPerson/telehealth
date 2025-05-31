from flask_wtf import FlaskForm
from wtforms import SelectField, DateTimeLocalField, TextAreaField, SubmitField
from wtforms.fields.choices import SelectMultipleField
from wtforms.fields.datetime import DateField, TimeField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import StringField, PasswordField, BooleanField, EmailField, TelField, FileField
from wtforms.validators import DataRequired, Email, Optional
from wtforms.widgets.core import CheckboxInput, ListWidget


from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField, 
                     DateTimeLocalField, SubmitField, HiddenField)
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import TextArea

class AppointmentStep1Form(FlaskForm):
    patient_story = TextAreaField('Describe Your Symptoms', 
                                validators=[DataRequired(), Length(min=10, max=500)],
                                widget=TextArea(),
                                render_kw={"rows": 5, "placeholder": "I've been experiencing..."})
    next_step = SubmitField('Continue')

class AppointmentStep2Form(FlaskForm):
    department = SelectField('Specialty', 
                           validators=[DataRequired()],
                           choices=[
                               ('', 'Select a specialty...'),
                               ('general', 'General Medicine'),
                               ('cardiology', 'Cardiology'),
                               ('dermatology', 'Dermatology'),
                               ('pediatrics', 'Pediatrics'),
                               ('neurology', 'Neurology')
                           ])
    is_urgent = SelectField('Priority', 
                           choices=[
                               (False, 'Routine'),
                               (True, 'Urgent')
                           ],
                           validators=[DataRequired()])
    next_step = SubmitField('Continue')
    prev_step = SubmitField('Back')

class AppointmentStep3Form(FlaskForm):
    patient_id = HiddenField('Patient ID')
    doctor_id = SelectField('Preferred Provider', 
                          coerce=int,
                          validators=[DataRequired()])
    appointment_date = DateTimeLocalField('Date & Time', 
                                        format='%Y-%m-%dT%H:%M',
                                        validators=[DataRequired()])
    appointment_type = SelectField('Visit Type',
                                 choices=[
                                     ('video', 'Video Consultation'),
                                     ('in-person', 'In-Person Visit'),
                                     ('phone', 'Phone Consultation')
                                 ],
                                 validators=[DataRequired()])
    reason = StringField('Reason for Visit',
                        validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Additional Notes',
                               validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Confirm Appointment')
    prev_step = SubmitField('Back')

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