from typing import Optional

from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    username: str
    email: str
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    password: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserFollow(UserRead):
    following: Optional[list[UserRead]]
    followers: Optional[list[UserRead]]


from posts.schemas import PostRead, PostRel


class UserRel(UserRead):
    posts: Optional[list["PostRel"]]


class UserRelFollow(UserFollow):
    posts: Optional[list["PostRead"]]


class UserRelFollowAll(UserRead):
    posts: Optional[list["PostRel"]]
    following: Optional[list[UserRel]]
    followers: Optional[list[UserRead]]