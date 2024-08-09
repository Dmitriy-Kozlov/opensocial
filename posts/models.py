from typing import Annotated, Optional

from sqlalchemy import text, Text, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

import datetime
from database import Base

created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[created_at]
    comments: Mapped[Optional[list["Comment"]]] = relationship(back_populates="post",)
    owner: Mapped["User"] = relationship(back_populates="posts")
    files: Mapped[Optional[list["PostFile"]]] = relationship(back_populates="post")

    def __repr__(self):
        return f"Post#{self.id}"


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    text: Mapped[str] = mapped_column(String(256))
    created_at: Mapped[created_at]
    owner: Mapped["User"] = relationship(back_populates="comments")
    post: Mapped["Post"] = relationship(back_populates="comments",)

    def __repr__(self):
        return f"{self.text}"


class PostFile(Base):
    __tablename__ = "postfiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[created_at]
    name: Mapped[str] = mapped_column(String(200))
    mimetype: Mapped[str] = mapped_column(String(100))
    post_id: Mapped[Optional[int]] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    owner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    post: Mapped["Post"] = relationship(back_populates="files")
    owner: Mapped["User"] = relationship(back_populates="files")

    def __repr__(self):
        return self.name

