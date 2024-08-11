from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from auth.schemas import UserCreate, UserRead
from posts.router import router as post_router
from auth.router import router as user_router
from pages.router import router as pages_router
from auth.user_manager import auth_backend, fastapi_users
from config import SECRET

app = FastAPI(
    title="Open Social"
)

app.add_middleware(SessionMiddleware, secret_key=SECRET)
app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(post_router)
app.include_router(user_router)
app.include_router(pages_router)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/users",
    tags=["users"]
)
