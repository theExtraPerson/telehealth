from datetime import datetime, timezone
from app import db

class Message(db.Model):
    __tablename__: str = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    file_url = db.Column(db.String, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    seen = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    user = db.relationship('User', foreign_keys=[user_id], backref='messages')


    def __init__(self, sender_id, receiver_id, content, file_url=None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.file_url = file_url