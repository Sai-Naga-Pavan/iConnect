from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional, Any

class PostCreate(BaseModel):
    title: str
    content: str


class LikesModel(BaseModel):
    total: int = 0
    liked_by: List[str] = []

class PostResponse(BaseModel):
    post_id: str
    username: str
    email: EmailStr
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    image_url: Optional[str]
    likes: LikesModel
