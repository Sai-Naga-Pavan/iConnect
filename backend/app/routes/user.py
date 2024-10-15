from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import EmailStr
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from bson import ObjectId
from app.services.auth import create_access_token, authenticate_user, get_current_user
from app.services.user import follow_request_accept, follow_request_send, register_new_user, unfollow_user

user_router = APIRouter()


@user_router.post("/register", response_model=dict)
async def register_user(username: str = Form(...),email: EmailStr = Form(...),password: str = Form(...),full_name: str = Form(...),image: UploadFile = File(None)):
    user = await register_new_user(username=username, email=email, password=password, full_name=full_name, image=image)
    return user
    

@user_router.post("/login")
async def login_user(user: UserLogin):
    authenticated_user = await authenticate_user(user.email, user.password)
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_access_token(data={"email": authenticated_user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.put("/follow_request_send", response_model=dict)
async def follow_request(target_user_email: str, current_user: dict = Depends(get_current_user)):
    follow_user = await follow_request_send(current_user=current_user, target_user_email=target_user_email)
    return follow_user

@user_router.put("/follow_request_accept", response_model=dict)
async def follow_request_accept_api(target_user_email: str, current_user: dict = Depends(get_current_user)):
    follow_user_accept = await follow_request_accept(current_user=current_user, target_user_email=target_user_email)
    return follow_user_accept


@user_router.put("/unfollow", response_model=dict)
async def unfollow(target_user_email: str, current_user: dict = Depends(get_current_user)):
    unfollow = await unfollow_user(current_user=current_user, target_user_email=target_user_email)
    return unfollow
