from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    created_at: datetime
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    pending_follow_requests: List[str]
    followers: List[str]
    following: List[str]

