# app/models/post.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from app.schemas.post import LikesModel

class Post(BaseModel):
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    email: EmailStr
    image_url: Optional[str] = None
    likes: LikesModel = LikesModel()
