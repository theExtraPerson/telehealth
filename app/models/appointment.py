from datetime import datetime
from sqlalchemy import text, Index, Enum
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from app import db
import uuid

def generate_meeting_link():
    """Generate a unique telemedicine meeting link"""
    return f"https://telemed.example.com/join/{uuid.uuid4().hex[:8]}"

class Appointment(db.Model):
    __tablename__ = 'appointments'

    # Primary key and identifiers
    id = db.Column(db.Integer, primary_key=True)
    appointment_uid = db.Column(UNIQUEIDENTIFIER, unique=True, nullable=False,
                              default=uuid.uuid4, server_default=text('NEWID()'))
    
    # Foreign keys
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Who created the appointment
    
    # Appointment details
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False, server_default=text('30'))  # Minutes
    description = db.Column(db.Text)  # Changed to Text for longer notes
    reason = db.Column(db.String(255))  # Chief complaint/reason for visit
    department = db.Column(db.String(50))  # Cardiology, Neurology, etc.
    
    # Telemedicine specific fields
    appointment_type = db.Column(
        Enum('in-person', 'video', 'phone', 'chat', name='appointment_types'), 
        nullable=False, 
        server_default=text("'in-person'")
    )
    video_platform = db.Column(db.String(50))  # Zoom, Teams, etc.
    meeting_link = db.Column(db.String(255))
    meeting_password = db.Column(db.String(50))
    device_info = db.Column(db.String(100))  # Patient's device for telemed
    
    # Status tracking
    status = db.Column(
        Enum('scheduled', 'confirmed', 'completed', 'cancelled', 'no-show', name='appointment_status'),
        nullable=False, 
        server_default=text("'scheduled'")
    )
    cancellation_reason = db.Column(db.String(255))
    is_urgent = db.Column(db.Boolean, server_default=text('0'))
    reminder_sent = db.Column(db.Boolean, server_default=text('0'))
    last_reminder_at = db.Column(db.DateTime)
    
    # Timestamps with SQL Server defaults
    created_at = db.Column(db.DateTime, nullable=False, server_default=text('GETDATE()'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=text('GETDATE()'), onupdate=text('GETDATE()'))
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    
    creator = db.relationship(
        "User",
        foreign_keys=[creator_id],
        back_populates="created_appointments"
    )
    
    def __repr__(self):
        return f"<Appointment {self.id} ({self.status}) with Dr.{self.doctor_id} for {self.patient_id}>"

    def to_dict(self):
        """Serialization for API responses"""
        return {
            'appointment_uid': str(self.appointment_uid),
            'patient_id': self.patient_id,
            'appointment_date': self.appointment_date.isoformat(),
            'duration': self.duration,
            'appointment_type': self.appointment_type,
            'status': self.status,
            'reason': self.reason,
            'department': self.department,
            'is_urgent': self.is_urgent,
            'video_platform': self.video_platform if self.is_telemedicine() else None,
            'meeting_link': self.meeting_link if self.is_telemedicine() else None
        }

    def is_telemedicine(self):
        return self.appointment_type in ['video', 'phone', 'chat']

    def is_upcoming(self):
        return self.status in ['scheduled', 'confirmed'] and self.appointment_date > datetime.utcnow()

    def start_telemedicine_session(self):
        if self.is_telemedicine() and self.status == 'confirmed':
            if not self.meeting_link:
                self.meeting_link = generate_meeting_link()
            return True
        return False

    __table_args__ = (
        Index('ix_appointments_patient', 'patient_id'),
        Index('ix_appointments_date', 'appointment_date'),
        Index('ix_appointments_status', 'status'),
        Index('ix_appointments_type', 'appointment_type'),
        Index('ix_appointments_urgent', 'is_urgent'),
    )