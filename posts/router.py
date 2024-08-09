import os
import shutil
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.responses import FileResponse

from auth.user_manager import current_active_user
from database import get_async_session
from posts.schemas import PostRead, PostAdd, PostRel, CommentAdd
from posts.models import Post, Comment, PostFile
from auth.models import User

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get("/", response_model=list[PostRel])
async def get_all_posts(session: AsyncSession = Depends(get_async_session)):
    query = (
        select(Post)
        .options(selectinload(Post.comments))
        .options(selectinload(Post.owner))
        .options(selectinload(Post.files))
            )
    result = await session.execute(query)
    posts = result.scalars().all()
    return posts


@router.get("/user/{user_id}", response_model=list[PostRel])
async def get_posts_by_user(
        user_id: int,
        session: AsyncSession = Depends(get_async_session)):
    query = (
        select(Post)
        .options(selectinload(Post.comments))
        .options(selectinload(Post.owner))
        .options(selectinload(Post.files))
        .filter_by(owner_id=user_id)
    )
    result = await session.execute(query)
    posts = result.scalars().all()
    return posts


@router.get("/{post_id}", response_model=PostRel)
async def get_posts_by_id(post_id: int, session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(Post)
            .options(selectinload(Post.comments))
            .options(selectinload(Post.owner))
            .options(selectinload(Post.files))
            .filter_by(id=post_id)
        )
        result = await session.execute(query)
        post = result.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def checker(data: str = Form(...)):
    try:
        return PostAdd.model_validate_json(data)
    except ValidationError as e:
        raise HTTPException(
            detail=jsonable_encoder(e.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


@router.post("/")
async def create_post(
        new_post: PostAdd = Depends(checker),
        session: AsyncSession = Depends(get_async_session),
        file: Optional[UploadFile] = File(None),
        user: User = Depends(current_active_user)
                ):
    new_post_db = Post(**new_post.dict(), owner=user)
    session.add(new_post_db)
    if file:
        await session.flush()
        os.makedirs(f"media/postfiles/{new_post_db.id}", exist_ok=True)
        with open(f"media/postfiles/{new_post_db.id}/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        mimetype = file.content_type
        name = file.filename

        postfile = PostFile(name=name, mimetype=mimetype, post=new_post_db, owner=user)
        session.add(postfile)
    session.add(new_post_db)
    await session.commit()
    return {"status": "Post created"}


@router.post("/comment")
async def create_comment(
        new_comment: CommentAdd,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
                ):
    try:
        query = (
            select(Post)
            .filter_by(id=new_comment.post_id)
        )
        result = await session.execute(query)
        post = result.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Post not found")
    new_comment_db = Comment(**new_comment.dict(), owner=user)
    session.add(new_comment_db)
    await session.commit()
    return {"status": "Comment created"}


@router.get("/{post_id}/{file_id}/download")
async def download_files(
        post_id: int,
        file_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)):
    try:
        query = select(PostFile).filter_by(post_id=post_id).filter_by(id=file_id)
        result = await session.execute(query)
        file = result.scalars().one()
        path = f"media/postfiles/{post_id}/{file.name}"
        return FileResponse(path, media_type='application/octet-stream', filename=file.name)
    except NoResultFound:
        raise HTTPException(status_code=404, detail="File not found")
