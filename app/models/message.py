from datetime import datetime
from sqlalchemy import text, Index
from app import db

class Message(db.Model):
    __tablename__ = 'messages'
    
    # Primary key and identifiers
    id = db.Column(db.Integer, primary_key=True)
    message_uid = db.Column(db.String(36), unique=True, nullable=False)  # UUID for external reference
    thread_id = db.Column(db.Integer, db.ForeignKey('message_threads.id'), nullable=True)  # For conversation threading
    
    # Participant relationships
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Removed redundant user_id as it's not needed with proper sender/receiver relations
    
    # Message content
    content = db.Column(db.Text, nullable=False)  # Changed to Text for longer messages
    category = db.Column(db.String(50), nullable=False, 
                       server_default=text("'general'"))  # general, medical, appointment, prescription
    message_type = db.Column(db.String(20), nullable=False, 
                           server_default=text("'text'"))  # text, image, video, document, audio
    
    # Medical-specific fields
    is_medical_advice = db.Column(db.Boolean, server_default=text('0'))
    related_appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    related_prescription_id = db.Column(db.Integer, db.ForeignKey('prescriptions.id'), nullable=True)
    priority = db.Column(db.String(10), server_default=text("'normal'"))  # low, normal, high, emergency
    
    # Attachments
    file_url = db.Column(db.String(255))  # Main attachment
    thumbnail_url = db.Column(db.String(255))  # For media previews
    file_size = db.Column(db.Integer)  # In bytes
    file_type = db.Column(db.String(50))  # MIME type
    
    # Status tracking
    status = db.Column(db.String(20), server_default=text("'sent'"))  # sent, delivered, read, failed
    seen = db.Column(db.Boolean, server_default=text('0'))
    seen_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Timestamps with SQL Server defaults
    created_at = db.Column(db.DateTime, nullable=False, 
                          server_default=text('GETDATE()'))
    updated_at = db.Column(db.DateTime, nullable=False, 
                          server_default=text('GETDATE()'), 
                          onupdate=text('GETDATE()'))
    
    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], 
                           backref=db.backref('sent_messages', lazy='dynamic'))
    receiver = db.relationship('User', foreign_keys=[receiver_id], 
                             backref=db.backref('received_messages', lazy='dynamic'))
    appointment = db.relationship('Appointment', backref=db.backref('messages', lazy='dynamic'))
    prescription = db.relationship('Prescription', backref=db.backref('messages', lazy='dynamic'))
    thread = db.relationship('MessageThread', backref=db.backref('messages', lazy='dynamic'))

    def __repr__(self):
        return f"<Message {self.id} ({self.category}) from {self.sender_id} to {self.receiver_id}>"

    def mark_as_read(self):
        """Mark message as read with current timestamp"""
        if not self.seen:
            self.seen = True
            self.seen_at = datetime.utcnow()
            db.session.commit()

    @classmethod
    def get_conversation(cls, user1_id, user2_id, limit=50):
        """Get conversation between two users"""
        return cls.query.filter(
            ((cls.sender_id == user1_id) & (cls.receiver_id == user2_id)) |
            ((cls.sender_id == user2_id) & (cls.receiver_id == user1_id))
        ).order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_medical_messages(cls, user_id):
        """Get all medical-related messages for a user"""
        return cls.query.filter(
            (cls.category == 'medical') & 
            ((cls.sender_id == user_id) | (cls.receiver_id == user_id))
        ).order_by(cls.created_at.desc()).all()

    @classmethod
    def get_attachments(self):
        """Return list of all attachments in message"""
        return [a for a in [self.file_url, self.thumbnail_url] if a]

    @classmethod
    def is_urgent(self):
        """Check if message is high priority"""
        return self.priority in ['high', 'emergency']

    __table_args__ = (
        Index('ix_messages_sender_receiver', 'sender_id', 'receiver_id'),
        Index('ix_messages_thread', 'thread_id'),
        Index('ix_messages_created', 'created_at'),
        Index('ix_messages_category', 'category'),
        Index('ix_messages_medical', 'is_medical_advice'),
    )


class MessageThread(db.Model):
    """Model for grouping related messages in conversations"""
    __tablename__ = 'message_threads'
    
    id = db.Column(db.Integer, primary_key=True)
    participant1_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    participant2_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_message_at = db.Column(db.DateTime, server_default=text('GETDATE()'))
    is_active = db.Column(db.Boolean, server_default=text('1'))
    
    # Relationships
    participant1 = db.relationship('User', foreign_keys=[participant1_id])
    participant2 = db.relationship('User', foreign_keys=[participant2_id])
    
    def __repr__(self):
        return f"<Thread {self.id} between {self.participant1_id} and {self.participant2_id}>"