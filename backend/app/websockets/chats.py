from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
from app.database import db
chats_collection = db["messages"]
users_collection = db["users"]

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Connect the user
async def connect_user(user_email: str, websocket: WebSocket):
    await websocket.accept()
    active_connections[user_email] = websocket

# Disconnect the user
def disconnect_user(user_email: str):
    if user_email in active_connections:
        del active_connections[user_email]

# WebSocket endpoint for chat
async def websocket_endpoint(websocket: WebSocket, sender_email: str, recipient_email: str):
    await connect_user(sender_email, websocket)
    sender = await users_collection.find_one({"email": sender_email})
    try:
        while True:
            message = await websocket.receive_text()

            # Save the message to the database
            chat_data = {
                "sender_id": sender_email,
                "receiver_id": recipient_email,
                "message": message,
                "timestamp": datetime.now()
            }
            await chats_collection.insert_one(chat_data)

            # Notify the recipient in real time
            if recipient_email in active_connections:
                await active_connections[recipient_email].send_text(f"New message from {sender['username']}: {message}")
    except WebSocketDisconnect:
        disconnect_user(sender_email)
