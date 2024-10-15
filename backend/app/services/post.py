from datetime import datetime
import os
import shutil
from bson import ObjectId
from fastapi import HTTPException
from app.database import db
from app.schemas.post import PostResponse
from app.websockets.notifications import send_notification

posts_collection = db["posts"]
users_collection = db["users"]
comments_collection = db["comments"]


async def new_post(title, content, image, current_user):
    post_data = {
        "title": title,
        "content": content,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "email": current_user["email"],
        "image_url": None,  # Initialize as None
        "likes": {
            "total": 0,
            "liked_by": []
        }
    }

    # Save image if provided
    if image:
        try:
            os.makedirs('static/posts', exist_ok=True)  # Create upload dir if not exists
            if image.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="Invalid image format. Only JPEG and PNG are allowed.")
            
            image_filename = f"{str(ObjectId())}_{image.filename}"
            image_path = os.path.join('static/posts', image_filename)
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            # Update the image URL in post_data
            post_data["image_url"] = f"/static/posts/{image_filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error saving image.")
    
    result = await posts_collection.insert_one(post_data)
    created_post = await posts_collection.find_one({"_id": result.inserted_id})
    user = await users_collection.find_one({"email": current_user["email"]})
    username = user.get("username") if user else None
    return PostResponse(post_id=str(result.inserted_id), username=username, **created_post)


async def all_posts():
    posts = []
    async for post in posts_collection.find():
        email = post.get("email")
        user = await users_collection.find_one({"email": email})
        username = user.get("username") if user else None
        posts.append(PostResponse(post_id=str(post["_id"]), username=username, **post))
    return posts


async def edit_post(post_id: str, post, current_user: dict):
    check = await posts_collection.find_one({"_id": ObjectId(post_id)})
    if not check:
        raise HTTPException(status_code=404, detail="Post not found")
    if check['email'] != current_user['email']:
        raise HTTPException(status_code=401, detail="You are not authorized to edit this post")
    post_data = post.dict()
    update_data = {
        "title": post_data.get('title', check['title']),
        "content": post_data.get('content', check['content']), 
        "updated_at": datetime.now()  
    }
    await posts_collection.update_one({"_id": ObjectId(post_id)},{"$set": update_data})
    user = await users_collection.find_one({"email": current_user["email"]})
    username = user.get("username") if user else None
    return PostResponse(post_id=post_id,username=username, **check)



async def delete_post(post_id, current_user):
    check = await posts_collection.find_one({"_id": ObjectId(post_id)})
    if not check:
        raise HTTPException(status_code=404, detail="Post Not Found")
    if check['email'] == current_user['email']:
        await posts_collection.delete_one({"_id": ObjectId(post_id), "email": current_user["email"]})
        await comments_collection.delete_many({"post_id": post_id, "email": current_user["email"]})
        return {"detail": "Post deleted Succesfully!!!"}
    else:
        raise HTTPException(status_code=401, detail="Not authorized")
    

async def like_post(post_id: str, current_user:dict):
    post = await posts_collection.find_one({"_id": ObjectId(post_id)})
    user = await users_collection.find_one({"email": post["email"]})
    username = user.get("username") if user else None
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    liked_user = await users_collection.find_one({"email": current_user['email']})
    # Check if the user has already liked the post
    if liked_user["username"] in post['likes']['liked_by']:
        raise HTTPException(status_code=400, detail="User has already liked the post")
    await posts_collection.update_one({"_id": ObjectId(post_id)}, {"$inc": {"likes.total": 1}, "$push": {"likes.liked_by": liked_user["username"]}})
    # Send real-time notification to the post owner
    await send_notification(post['email'], f"{current_user['username']} liked your post")
    updated_post = await posts_collection.find_one({"_id": ObjectId(post_id)})
    return PostResponse(post_id=str(post["_id"]), username=username, **updated_post)


async def unlike_post(post_id: str, current_user:dict):
    post = await posts_collection.find_one({"_id": ObjectId(post_id)})
    user = await users_collection.find_one({"email": post["email"]})
    username = user.get("username") if user else None
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    unliked_user = await users_collection.find_one({"email": current_user['email']})
    # Check if the user has already liked the post
    if unliked_user['username'] not in post["likes"]["liked_by"]:
        raise HTTPException(status_code=400, detail="You have not liked this post")
    # Remove the user from liked_by and decrement the total likes
    post["likes"]["liked_by"].remove(unliked_user['username'])
    post["likes"]["total"] -= 1
    # Update the post in the collection
    await posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"likes": post["likes"]}}
    )
    # Send real-time notification to the post owner
    await send_notification(post['email'], f"{current_user['username']} unliked your post")
    updated_post = await posts_collection.find_one({"_id": ObjectId(post_id)})
    return PostResponse(post_id=str(post["_id"]), username=username, **updated_post)


    