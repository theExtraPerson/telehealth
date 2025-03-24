from datetime import datetime
from sqlalchemy.orm import relationship
from app.database import Base

class Message(db.Model):
    __tablename__: str = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    file_url = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

    def __init__(self, sender_id, receiver_id, content, file_url=None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.file_url = file_url