import datetime

from pydantic import BaseModel


class PostAdd(BaseModel):
    text: str


class PostRead(PostAdd):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class CommentAdd(BaseModel):
    post_id: int
    text: str


class CommentRead(CommentAdd):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class PostFileAdd(BaseModel):
    name: str
    mimetype: str


class PostFileRead(PostFileAdd):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True


from auth.schemas import UserRead


class CommentRel(CommentRead):
    owner: UserRead


class PostFileRel(PostFileRead):
    post: PostRead
    owner: UserRead


class PostRel(PostRead):
    comments: list[CommentRel]
    files: list[PostFileRead]
    owner: UserRead




