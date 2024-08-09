from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from auth.models import User
from auth.schemas import UserRead, UserFollow
from auth.user_manager import current_active_user
from database import get_async_session

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


@router.get("/me", response_model=UserFollow)
async def get_all_users(session: AsyncSession = Depends(get_async_session),
                        user: User = Depends(current_active_user)
                        ):
    query = (
        select(User)
        .options(selectinload(User.following))
        .options(selectinload(User.followers))
        .filter_by(id=user.id)
    )
    result = await session.execute(query)
    user = result.scalars().one()
    return user


@router.put("/{user_id}/follow", response_model=UserFollow)
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
