from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict

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

# Send notification to a user
async def send_notification(user_email: str, message: str):
    if user_email in active_connections:
        await active_connections[user_email].send_text(message)

# WebSocket endpoint for notifications
async def websocket_endpoint(websocket: WebSocket, user_email: str):
    await connect_user(user_email, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        disconnect_user(user_email)
