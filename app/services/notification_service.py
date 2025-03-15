import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client
from datetime import datetime, timedelta

class NotificationService:
    def __init__(self, email_config, sms_config):
        self.email_config = email_config
        self.sms_config = sms_config

    def send_email(self, to_email, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.email_config['email']
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['email'], self.email_config['password'])
            text = msg.as_string()
            server.sendmail(self.email_config['email'], to_email, text)
            server.quit()
            print(f"Email sent to {to_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def send_sms(self, to_phone, message):
        client = Client(self.sms_config['account_sid'], self.sms_config['auth_token'])

        try:
            message = client.messages.create(
                body=message,
                from_=self.sms_config['from_phone'],
                to=to_phone
            )
            print(f"SMS sent to {to_phone}")
        except Exception as e:
            print(f"Failed to send SMS: {e}")

    def send_reminder(self, user, doctor, appointment_time):
        reminder_time = appointment_time - timedelta(hours=1)
        current_time = datetime.now()

        if current_time >= reminder_time:
            email_subject = "Appointment Reminder"
            email_body = f"Dear {user['name']},\n\nThis is a reminder for your appointment with Dr. {doctor['name']} at {appointment_time}.\n\nBest regards,\nYour Healthcare Platform"
            self.send_email(user['email'], email_subject, email_body)

            sms_message = f"Reminder: Appointment with Dr. {doctor['name']} at {appointment_time}."
            self.send_sms(user['phone'], sms_message)

# Example usage
email_config = {
    'email': 'your_email@example.com',
    'password': 'your_password',
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587
}

sms_config = {
    'account_sid': 'your_twilio_account_sid',
    'auth_token': 'your_twilio_auth_token',
    'from_phone': '+1234567890'
}

notification_service = NotificationService(email_config, sms_config)

user = {'name': 'John Doe', 'email': 'john.doe@example.com', 'phone': '+19876543210'}
doctor = {'name': 'Dr. Smith'}
appointment_time = datetime(2023, 10, 15, 14, 0)

notification_service.send_reminder(user, doctor, appointment_time)