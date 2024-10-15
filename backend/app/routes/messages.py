from app.models.messages import Message
from fastapi import APIRouter, Depends
from app.services.auth import get_current_user
from app.services.messages import delete_messages_between_users, get_messages


messages_router = APIRouter()


@messages_router.get("/history/{recipient_email}", response_model=list[Message])
async def chat_history_api(recipient_email:str, limit: int = 50, skip: int = 0, sender_email: dict = Depends(get_current_user)):
    chat_history = await get_messages(recipient_email=recipient_email, limit=limit, skip=skip, sender_email=sender_email)
    return chat_history


@messages_router.delete("/delete/{recipient_email}", response_model=dict)
async def delete_chat_history(
    recipient_email: str,
    sender_email: dict = Depends(get_current_user)
):
    result = await delete_messages_between_users(sender_email=sender_email, recipient_email=recipient_email)
    return result