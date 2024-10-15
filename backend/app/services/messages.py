from fastapi import HTTPException
from pymongo import ASCENDING
from app.database import db


users_collection = db["users"]
messages_collection = db["messages"]

async def get_messages(recipient_email:str, limit:int, skip:int, sender_email:dict):
    check_user = await users_collection.find_one({'email': recipient_email})
    if not check_user:
        raise HTTPException(status_code=404, detail="User Not Found!!!")
    # Fetch chat history between sender and recipient
    chat_history = await messages_collection.find(
        {
            "$or": [
                {"sender_id": sender_email['email'], "receiver_id": recipient_email},
                {"sender_id": recipient_email, "receiver_id": sender_email['email']}
            ]
        }
    ).sort("timestamp", ASCENDING).skip(skip).limit(limit).to_list(length=None)

    # If no chat history, return a message to encourage starting a conversation
    if not chat_history:
        raise HTTPException(status_code=404, detail="No chat history. Start a conversation now!")
    return chat_history


async def delete_messages_between_users(sender_email: dict, recipient_email: str):
    check_user = await users_collection.find_one({'email': recipient_email})
    if not check_user:
        raise HTTPException(status_code=404, detail="User Not Found!!!")
    # Delete chat history between the sender and recipient
    result = await messages_collection.delete_many(
        {
            "$or": [
                {"sender_id": sender_email['email'], "receiver_id": recipient_email},
                {"sender_id": recipient_email, "receiver_id": sender_email['email']}
            ]
        }
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No chat history to delete or already deleted.")
    
    return {"message": "Chat history deleted successfully."}