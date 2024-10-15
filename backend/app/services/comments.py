from datetime import datetime
from app.database import db
from bson import ObjectId
from fastapi import HTTPException
from app.schemas.comments import CommentResponse
from app.websockets.notifications import send_notification
comments_collection = db["comments"]
users_collection = db["users"]

async def add_comment(comment, current_user):   
    comment_data = comment.dict()
    comment_data["created_at"] = datetime.now()
    comment_data["updated_at"] = datetime.now()
    comment_data["email"] = current_user["email"]
    # Check if the post exists before adding the comment
    post = await db["posts"].find_one({"_id": ObjectId(comment.post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    result = await comments_collection.insert_one(comment_data)
    created_comment = await comments_collection.find_one({"_id": result.inserted_id})
    user = await users_collection.find_one({"email": current_user["email"]})
    username = user.get("username") if user else None
    # Send real-time notification to the target user
    await send_notification(
        post['email'],
        f"{current_user['username']} is commented on your post."
    )
    return CommentResponse(comment_id=str(result.inserted_id), username=username, **created_comment)


async def all_comments(post_id: str):
    # Check if the post exists before getting the comments
    post = await db["posts"].find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = []
    async for comment in comments_collection.find({"post_id": post_id}):
        user = await users_collection.find_one({"email": comment["email"]})
        username = user.get("username") if user else None
        comments.append(CommentResponse(comment_id=str(comment["_id"]), username=username, **comment))
    return comments


async def update_comment(comment_id:str, content:str, current_user:dict):
    check = await comments_collection.find_one({"_id": ObjectId(comment_id)})
    if not check:
        raise HTTPException(status_code=404, detail="Comment not found")
    if check['email'] != current_user['email']:
        raise HTTPException(status_code=401, detail="You are not authorized to edit this comment")
    check['content'] = content
    check['updated_at'] = datetime.now()
    update_data = {
        "content": content, 
        "updated_at": datetime.now()  
    }
    await comments_collection.update_one({"_id": ObjectId(comment_id)},{"$set": update_data})
    user = await users_collection.find_one({"email": current_user["email"]})
    username = user.get("username") if user else None
    return CommentResponse(comment_id=comment_id, username=username, **check)


async def delete_comment(comment_id, current_user):
    check = await comments_collection.find_one({"_id": ObjectId(comment_id)})
    if not check:
        raise HTTPException(status_code=404, detail="Comment not found")
    if check['email'] == current_user['email']:
        await comments_collection.delete_one({"_id": ObjectId(comment_id), "email": current_user["email"]})
        return {"detail": "Comment deleted Succesfully!!!"}
    else:
        raise HTTPException(status_code=401, detail="Not authorized")
