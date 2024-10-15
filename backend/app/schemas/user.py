from fastapi import Form
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str= Form(...)
    email: EmailStr= Form(...)
    password: str= Form(...)
    full_name: Optional[str]= Form(...)
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str



