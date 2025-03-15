import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
import hashlib
import uuid
from datetime import datetime

# File Handling Helpers
def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

def append_to_file(file_path, content):
    with open(file_path, 'a') as file:
        file.write(content)

# Authentication Helpers
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password, provided_password):
    return stored_password == hash_password(provided_password)

# SMS Sending Helper
def send_sms(account_sid, auth_token, from_number, to_number, message):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=from_number,
        to=to_number
    )
    return message.sid

# Email Sending Helper
def send_email(smtp_server, port, sender_email, receiver_email, subject, body, login, password):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# Calculation Helpers
def calculate_total_price(prescriptions):
    total = 0
    for prescription in prescriptions:
        total += prescription['price'] * prescription['quantity']
    return total

# Super Cool Helpers
def generate_unique_id():
    return str(uuid.uuid4())

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')