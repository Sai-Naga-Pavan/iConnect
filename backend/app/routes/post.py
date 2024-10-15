from fastapi import APIRouter, Depends, File, Form, UploadFile
from app.schemas.post import PostCreate, PostResponse
from app.services.auth import get_current_user
from app.services.post import all_posts, delete_post, edit_post, like_post, new_post, unlike_post

post_router = APIRouter()


@post_router.post("/", response_model=PostResponse)
async def create_post(title: str = Form(...),content: str = Form(...),
    image: UploadFile = File(None),  # Optional image upload
    current_user: dict = Depends(get_current_user)
):
   post = await new_post(title=title,content=content,image=image, current_user=current_user)
   return post

@post_router.get("/",response_model=list[PostResponse])
async def get_posts(current_user: dict = Depends(get_current_user)):
    posts = await all_posts()
    return posts

@post_router.put("/{post_id}", response_model=PostResponse)
async def edit_posts(post_id: str, post: PostCreate, current_user: dict = Depends(get_current_user)):
    update = await edit_post(post_id=post_id, post=post, current_user=current_user)
    return update

@post_router.delete("/{post_id}", response_model=dict)
async def delete_post_api(post_id: str, current_user: dict = Depends(get_current_user)):
    delete = await delete_post(post_id=post_id, current_user=current_user)
    return delete

@post_router.put("/{post_id}/like", response_model=PostResponse)
async def like_post_api(post_id: str, current_user: dict = Depends(get_current_user)):
    like = await like_post(post_id=post_id, current_user=current_user)
    return like
    
@post_router.put("/{post_id}/unlike", response_model=PostResponse)
async def unlike_post_api(post_id: str, current_user: dict = Depends(get_current_user)):
    unlike = await unlike_post(post_id=post_id, current_user=current_user)
    return unlike