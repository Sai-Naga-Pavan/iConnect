from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Comment(BaseModel):
    post_id: str
    content: str
    created_at: datetime
    updated_at: datetime
    email: str
