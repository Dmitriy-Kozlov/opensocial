from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, contains_eager

from auth.models import User, user_following
from auth.schemas import UserRead, UserFollow, UserRelFollow, UserRel, UserRelFollowAll
from auth.user_manager import current_active_user
from database import get_async_session
from posts.models import Post, Comment

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/all", response_model=list[UserFollow])
async def get_all_users(session: AsyncSession = Depends(get_async_session)):
    query = (
        select(User)
        .options(selectinload(User.following))
        .options(selectinload(User.followers))
    )
    result = await session.execute(query)
    users = result.scalars().all()
    return users


# @router.get("/me", response_model=UserRelFollowAll)
@router.get("/me", response_model=UserFollow)
async def get_my_users(session: AsyncSession = Depends(get_async_session),
                        user: User = Depends(current_active_user)
                        ):
    # query = (
    #     select(User)
    #     .options(selectinload(User.following).selectinload(User.posts).selectinload(Post.comments).selectinload(Comment.owner))
    #     .options(selectinload(User.following).selectinload(User.posts).selectinload(Post.files))
    #     .options(selectinload(User.followers))
    #     .options(selectinload(User.posts).selectinload(Post.comments).selectinload(Comment.owner))
    #     .options(selectinload(User.posts).selectinload(Post.files))
    #     .filter_by(id=user.id)
    # )

    query = (
        select(User)
        .options(selectinload(User.following))
        .options(selectinload(User.followers))
        .filter_by(id=user.id)
    )

    result = await session.execute(query)
    user = result.scalars().one()
    return user


@router.get("/{user_id}", response_model=UserRelFollowAll)
async def get_users_by_id_posts(
                        user_id: int,
                        session: AsyncSession = Depends(get_async_session),
                        ):
    try:
        query = (
            select(User)
            .options(selectinload(User.following).selectinload(User.posts).selectinload(Post.comments).selectinload(Comment.owner))
            .options(selectinload(User.following).selectinload(User.posts).selectinload(Post.files))
            .options(selectinload(User.followers))
            .options(selectinload(User.posts).selectinload(Post.comments).selectinload(Comment.owner))
            .options(selectinload(User.posts).selectinload(Post.files))
            .filter_by(id=user_id)
        )
        result = await session.execute(query)
        user = result.scalars().one()
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}/follow")
async def follow_user(
                user_id: int,
                session: AsyncSession = Depends(get_async_session),
                current_user: User = Depends(current_active_user)
                    ):
    try:
        query = (select(User)
                 .options(selectinload(User.followers))
                 .options(selectinload(User.following))
                 .filter_by(id=user_id))
        result = await session.execute(query)
        user = result.scalars().one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")
    user.followers.append(current_user)
    session.add(user)
    await session.commit()
    return {"message": "OK"}


@router.delete("/{user_id}/unfollow")
async def unfollow_user(
                user_id: int,
                session: AsyncSession = Depends(get_async_session),
                current_user: User = Depends(current_active_user)
                    ):
    query = (
        select(user_following)
        .where(user_following.c.user_id == user_id)
        .where(user_following.c.following_id == current_user.id)
    )
    result = await session.execute(query)
    user_following_record = result.fetchone()

    if user_following_record is None:
        raise HTTPException(status_code=404, detail="Not found")

    delete_query = user_following.delete().where(
        user_following.c.user_id == user_id,
        user_following.c.following_id == current_user.id
    )

    await session.execute(delete_query)
    await session.commit()
    return {"message": "OK"}
