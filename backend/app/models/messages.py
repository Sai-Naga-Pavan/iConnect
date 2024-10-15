from datetime import datetime
from pydantic import BaseModel


class Message(BaseModel):
    sender_id: str
    receiver_id: str
    message: str
    timestamp: datetime