from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, List, Optional
from datetime import datetime
import json
import uuid
from models.message import Message, MessageThread 
from models.user import User  # Assuming your models are in models.py
from database import SessionLocal  # Database session

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_rooms: Dict[str, List[str]] = {}  # Track which chat rooms users are in

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        await self.notify_online_status(user_id, True)

    async def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        await self.notify_online_status(user_id, False)

    async def join_chat_room(self, user_id: str, thread_id: str):
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = []
        self.user_rooms[user_id].append(thread_id)

    async def leave_chat_room(self, user_id: str, thread_id: str):
        if user_id in self.user_rooms and thread_id in self.user_rooms[user_id]:
            self.user_rooms[user_id].remove(thread_id)

    async def send_personal_message(self, message: dict, user_id: str):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_json(message)

    async def send_message_to_thread(self, message: dict, thread_id: str):
        """Send message to all participants in a thread"""
        db = SessionLocal()
        try:
            thread = db.query(MessageThread).filter_by(id=thread_id).first()
            if thread:
                for user_id in [thread.participant1_id, thread.participant2_id]:
                    if user_id in self.active_connections:
                        await self.active_connections[user_id].send_json(message)
        finally:
            db.close()

    async def notify_online_status(self, user_id: str, is_online: bool):
        """Notify all chat partners about online status"""
        db = SessionLocal()
        try:
            user = db.query(User).filter_by(id=user_id).first()
            if user:
                # Notify all threads this user participates in
                threads = db.query(MessageThread).filter(
                    (MessageThread.participant1_id == user_id) | 
                    (MessageThread.participant2_id == user_id)
                ).all()
                
                for thread in threads:
                    partner_id = thread.participant2_id if thread.participant1_id == user_id else thread.participant1_id
                    if partner_id in self.active_connections:
                        await self.active_connections[partner_id].send_json({
                            "type": "presence",
                            "user_id": user_id,
                            "is_online": is_online,
                            "thread_id": thread.id
                        })
        finally:
            db.close()

manager = ConnectionManager()

@app.websocket("/ws/messages/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            
            if data["type"] == "join_thread":
                await manager.join_chat_room(user_id, data["thread_id"])
                await manager.send_personal_message({
                    "type": "system",
                    "message": f"Joined thread {data['thread_id']}"
                }, user_id)
                
            elif data["type"] == "leave_thread":
                await manager.leave_chat_room(user_id, data["thread_id"])
                await manager.send_personal_message({
                    "type": "system",
                    "message": f"Left thread {data['thread_id']}"
                }, user_id)
                
            elif data["type"] == "new_message":
                await handle_new_message(data, user_id)
                
            elif data["type"] == "message_read":
                await handle_message_read(data, user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except json.JSONDecodeError:
        await websocket.send_json({
            "type": "error",
            "message": "Invalid JSON format"
        })
    except KeyError as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Missing required field: {str(e)}"
        })

async def handle_new_message(data: dict, sender_id: str):
    db = SessionLocal()
    try:
        # Validate thread exists and user is participant
        thread = db.query(MessageThread).filter_by(id=data["thread_id"]).first()
        if not thread or sender_id not in [thread.participant1_id, thread.participant2_id]:
            raise HTTPException(status_code=403, detail="Not authorized for this thread")
        
        # Create new message
        new_message = Message(
            thread_id=data["thread_id"],
            sender_id=sender_id,
            receiver_id=thread.participant2_id if thread.participant1_id == sender_id else thread.participant1_id,
            content=data["content"],
            message_type=data.get("message_type", "text"),
            category=data.get("category", "general"),
            is_medical_advice=data.get("is_medical_advice", False)
        )
        
        if "file_url" in data:
            new_message.file_url = data["file_url"]
            new_message.file_type = data.get("file_type")
            new_message.file_size = data.get("file_size")
        
        db.add(new_message)
        db.commit()
        
        # Prepare message for WebSocket
        ws_message = {
            "type": "new_message",
            "message_id": new_message.id,
            "thread_id": new_message.thread_id,
            "sender_id": new_message.sender_id,
            "content": new_message.content,
            "timestamp": new_message.created_at.isoformat(),
            "message_type": new_message.message_type,
            "is_medical": new_message.is_medical_advice
        }
        
        # Send to all thread participants
        await manager.send_message_to_thread(ws_message, new_message.thread_id)
        
    finally:
        db.close()

async def handle_message_read(data: dict, user_id: str):
    db = SessionLocal()
    try:
        message = db.query(Message).filter_by(id=data["message_id"]).first()
        if message and message.receiver_id == user_id:
            message.seen = True
            message.seen_at = datetime.utcnow()
            db.commit()
            
            # Notify sender that message was read
            await manager.send_personal_message({
                "type": "message_read",
                "message_id": message.id,
                "read_at": message.seen_at.isoformat(),
                "reader_id": user_id
            }, message.sender_id)
    finally:
        db.close()

@app.get("/teleconsultation/threads/{user_id}")
async def get_user_threads(user_id: str):
    """Get all message threads for a user"""
    db = SessionLocal()
    try:
        threads = db.query(MessageThread).filter(
            (MessageThread.participant1_id == user_id) | 
            (MessageThread.participant2_id == user_id)
        ).all()
        
        return {
            "threads": [
                {
                    "thread_id": thread.id,
                    "participant1": thread.participant1_id,
                    "participant2": thread.participant2_id,
                    "last_message": thread.last_message_at.isoformat() if thread.last_message_at else None,
                    "unread_count": db.query(Message).filter(
                        Message.thread_id == thread.id,
                        Message.receiver_id == user_id,
                        Message.seen == False
                    ).count()
                }
                for thread in threads
            ]
        }
    finally:
        db.close()

@app.post("/teleconsultation/threads/start")
async def start_new_thread(participant1: str, participant2: str):
    """Create a new message thread between two users"""
    db = SessionLocal()
    try:
        # Check if thread already exists
        existing_thread = db.query(MessageThread).filter(
            ((MessageThread.participant1_id == participant1) & (MessageThread.participant2_id == participant2)) |
            ((MessageThread.participant1_id == participant2) & (MessageThread.participant2_id == participant1))
        ).first()
        
        if existing_thread:
            return {"thread_id": existing_thread.id}
        
        # Create new thread
        new_thread = MessageThread(
            participant1_id=participant1,
            participant2_id=participant2
        )
        db.add(new_thread)
        db.commit()
        
        return {"thread_id": new_thread.id}
    finally:
        db.close()