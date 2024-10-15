from pydantic import BaseModel, EmailStr
from datetime import datetime

class CommentCreate(BaseModel):
    post_id: str
    content: str

class CommentResponse(BaseModel):
    comment_id: str
    post_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    email: EmailStr
    username: str
