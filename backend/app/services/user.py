import re
from fastapi import File, Form, HTTPException, UploadFile
from pydantic import EmailStr
from passlib.context import CryptContext
from app.websockets.notifications import send_notification
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
from datetime import datetime
import os
import shutil
from app.database import db
users_collection = db["users"]
UPLOAD_DIR = "static/profile_images"

async def register_new_user(username: str = Form(...), email: EmailStr = Form(...), password: str = Form(...), full_name: str = Form(...), image: UploadFile = File(None)):
        if await users_collection.find_one({"email": email.lower()}):
            raise HTTPException(status_code=400, detail="Email already registered")
        if await users_collection.find_one({"username": username.lower()}):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password should be at least 8 characters long.")
        if not re.search(r"[A-Z]", password):  # Check for uppercase letter
            raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", password):  # Check for lowercase letter
            raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):  # Check for special character
            raise HTTPException(status_code=400, detail="Password must contain at least one special character.")
        if not re.search(r"[0-9]", password):  # Check for at least one digit
            raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
        
        hashed_password = pwd_context.hash(password)
        user_data = {
        "username": username.lower(),
        "email": email.lower(),
        "password": hashed_password,
        "full_name": full_name,
        "created_at": datetime.now(),
        "profile_image_url": None,
        "pending_follow_requests": [],
        "followers": [],
        "following": []
        }
        # Save image if provided
        if image:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            if image and image.content_type not in ["image/jpeg", "image/png"]:
                    raise HTTPException(status_code=400, detail="Invalid image format. Only JPEG and PNG are allowed.")
            image_filename = f"{username}_{image.filename}"  # Unique filename
            image_path = os.path.join(UPLOAD_DIR, image_filename)
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            user_data["profile_image_url"] = f"/static/profile_images/{image_filename}"
        
        result = await users_collection.insert_one(user_data)
        if result:
            return {"message": "User Created Successfully!!!"}
        
    
async def follow_request_send(current_user: dict,target_user_email:str):
    current_user_check = await users_collection.find_one({"email": current_user["email"]})
    target_user_email_check = await users_collection.find_one({"email": target_user_email})

    if not current_user_check or not target_user_email_check:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    if current_user['email'] in target_user_email_check["followers"]:
        raise HTTPException(status_code=400, detail="Already following this user")
    
    if current_user['email'] in target_user_email_check.get("pending_follow_requests", []):
        raise HTTPException(status_code=400, detail="Follow request already sent")
    
     # Add the current user to the target user's pending requests
    await users_collection.update_one(
        {"email": target_user_email},
        {"$push": {"pending_follow_requests": current_user['email']}}
    )
    # Send real-time notification to the target user
    await send_notification(
        target_user_email,
        f"{current_user_check['username']} sent you a follow request"
    )
    return {"message": "Follow request sent!!!"}


async def follow_request_accept(current_user: dict,target_user_email:str):
    current_user_check = await users_collection.find_one({"email": current_user["email"]})
    target_user_email_check = await users_collection.find_one({"email": target_user_email})

    if not current_user_check or not target_user_email_check:
        raise HTTPException(status_code=404, detail="User not found")
    
    if target_user_email not in current_user.get("pending_follow_requests", []):
        raise HTTPException(status_code=400, detail="No follow request from this user")
    
    # Remove from pending requests and add to followers
    await users_collection.update_one(
        {"email": current_user["email"]},
        {
            "$pull": {"pending_follow_requests": target_user_email},
            "$push": {"followers": target_user_email}
        }
    )

    await users_collection.update_one(
        {"email": target_user_email},
        {"$push": {"following": current_user["email"]}}
    )

    # Send real-time notification to the requester
    await send_notification(
        target_user_email,
        f"{current_user_check['username']} accepted your follow request"
    )

    return {"message": "Follow request accepted!!!"}
    

async def unfollow_user(current_user: dict,target_user_email:str):
    current_user_check = await users_collection.find_one({"email": current_user["email"]})
    target_user_email_check = await users_collection.find_one({"email": target_user_email})

    if not current_user_check or not target_user_email_check:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    if target_user_email not in current_user["followers"]:
        raise HTTPException(status_code=400, detail="You are not following this user")
    
    # remove following and followers list
    await users_collection.update_one(
        {"email": current_user["email"]},
        {"$pull": {"followers": target_user_email}}
    )
    await users_collection.update_one(
        {"email": target_user_email},
        {"$pull": {"following": current_user["email"]}}
    )
    # Send real-time notification to the target user
    await send_notification(
        target_user_email,
        f"{current_user['username']} has unfollowed you"
    )
    return {"message": f"You have unfollowed {target_user_email_check['username']}"}