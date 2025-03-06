from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(String, nullable=False)
    file_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    sender = relationship('User', foreign_keys=[sender_id])
    receiver = relationship('User', foreign_keys=[receiver_id])

    def __init__(self, sender_id, receiver_id, content, file_url=None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.file_url = file_url