from datetime import datetime
from typing import Optional

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import String, Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from database import Base, get_async_session
from posts.models import PostFile, Post, Comment


user_following = Table(
    'user_following', Base.metadata,
    Column('user_id', Integer, ForeignKey("users.id"), primary_key=True),
    Column('following_id', Integer, ForeignKey("users.id"), primary_key=True)
)


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=False)
    registered_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    posts: Mapped[Optional[list["Post"]]] = relationship(back_populates="owner")
    comments: Mapped[Optional[list["Comment"]]] = relationship(back_populates="owner")
    files: Mapped[Optional[list["PostFile"]]] = relationship(back_populates="owner")
    following = relationship(
        'User', primaryjoin=lambda: User.id == user_following.c.following_id,
        secondaryjoin=lambda: user_following.c.user_id == User.id,
        backref='following_users',
        secondary=user_following,
    )

    followers = relationship(
        'User', primaryjoin=lambda: User.id == user_following.c.user_id,
        secondaryjoin=lambda: user_following.c.following_id == User.id,
        secondary=user_following,
        overlaps="following,following_users"
    )

    def __repr__(self):
        return self.username


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
