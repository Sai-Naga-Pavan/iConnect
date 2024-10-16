from fastapi import Depends, FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from app.routes import comments, user, post, messages
from app.services.auth import get_current_user, websocket_auth
from app.websockets import chat_bot, chats, notifications

app = FastAPI()

app.include_router(user.user_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(post.post_router, prefix="/api/v1/posts", tags=["Posts"], dependencies=[Depends(get_current_user)])
app.include_router(comments.comment_router, prefix="/api/v1/comments", tags=["Comments"], dependencies=[Depends(get_current_user)])
app.include_router(messages.messages_router, prefix="/api/v1/chat", tags=["Messages"], dependencies=[Depends(get_current_user)])

# WebSocket routes
@app.websocket("/ws/notifications/{user_email}")
async def notification_websocket(websocket: WebSocket, user_email: str):
    # Authenticate the user via JWT token from the WebSocket query params
    user = await websocket_auth(websocket)
    if not user:
        return  # Close connection if authentication fails

    # Ensure the authenticated user matches the user_email provided
    if user['email'] != user_email:
        await websocket.close(code=1008)  # Close connection if user_email doesn't match
        return

    # Handle WebSocket connection after successful authentication
    await notifications.websocket_endpoint(websocket, user_email)


@app.websocket("/ws/chat/{sender_email}/{recipient_email}")
async def chat_websocket(websocket: WebSocket, sender_email: str, recipient_email: str):
    # Authenticate the user via JWT token from the WebSocket query params
    user = await websocket_auth(websocket)
    if not user:
        return  # Close connection if authentication fails

    # Ensure the authenticated user matches the user_email provided
    if user['email'] != sender_email:
        await websocket.close(code=1008)  # Close connection if user_email doesn't match
        return
    await chats.websocket_endpoint(websocket, sender_email, recipient_email)


@app.websocket("/ws/chat_bot/{user_email}")
async def chatbot_websocket(websocket: WebSocket, user_email: str):
    # Authenticate the user via JWT token from the WebSocket query params
    user = await websocket_auth(websocket)
    if not user:
        return  # Close connection if authentication fails
    # Ensure the authenticated user matches the user_email provided
    if user['email'] != user_email:
        await websocket.close(code=1008)  # Close connection if user_email doesn't match
        return

    # Handle WebSocket connection after successful authentication
    await chat_bot.chat_bot_function(websocket)

# Serve static files for uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # This line will run when you execute the script directly
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)