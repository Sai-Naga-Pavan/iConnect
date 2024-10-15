from fastapi import APIRouter, Depends
from app.schemas.comments import CommentCreate, CommentResponse
from app.services.auth import get_current_user
from app.services.comments import add_comment, all_comments, delete_comment, update_comment

comment_router = APIRouter()


@comment_router.post("/", response_model=CommentResponse)
async def create_comment(comment: CommentCreate, current_user: dict = Depends(get_current_user)):
    comment = await add_comment(comment=comment, current_user=current_user)
    return comment

@comment_router.get("/post/{post_id}", response_model=list[CommentResponse])
async def get_comments(post_id: str,  current_user: dict = Depends(get_current_user)):
    comments = await all_comments(post_id=post_id)
    return comments

@comment_router.put("/{comment_id}", response_model=CommentResponse)
async def edit_comments(comment_id: str, content: str, current_user: dict =Depends(get_current_user)):
    edit = await update_comment(comment_id=comment_id, content=content, current_user=current_user)
    return edit

@comment_router.delete("/{comment_id}", response_model=dict)
async def delete_comment_api(comment_id: str, current_user: dict = Depends(get_current_user)):
    delete = await delete_comment(comment_id=comment_id, current_user=current_user)
    return delete
