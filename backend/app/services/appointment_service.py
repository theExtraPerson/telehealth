from datetime import datetime

class AppointmentService:
    def __init__(self):
        self.appointments = []

    def create_appointment(self, user_id, appointment_time):
        appointment = {
            'user_id': user_id,
            'appointment_time': appointment_time,
            'created_at': datetime.now(),
            'status': 'scheduled'
        }
        self.appointments.append(appointment)
        return appointment

    def get_appointments(self, user_id=None):
        if user_id:
            return [appt for appt in self.appointments if appt['user_id'] == user_id]
        return self.appointments

    def update_appointment(self, appointment_id, new_time):
        for appt in self.appointments:
            if appt['id'] == appointment_id:
                appt['appointment_time'] = new_time
                appt['updated_at'] = datetime.now()
                return appt
        return None

    def cancel_appointment(self, appointment_id):
        for appt in self.appointments:
            if appt['id'] == appointment_id:
                appt['status'] = 'canceled'
                appt['canceled_at'] = datetime.now()
                return appt
        return None