from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from auth.models import User
from auth.user_manager import current_active_user
from auth.router import get_my_users
from posts.router import get_all_posts, get_posts_by_id, get_all_my_posts, get_posts_by_user

router = APIRouter(prefix='/pages', tags=['Фронтенд'])
templates = Jinja2Templates(directory='templates')


@router.get('/users/register')
async def get_users_register_form(request: Request):
    return templates.TemplateResponse(name='register_form.html', context={'request': request})


@router.get('/users/login')
async def get_users_login_form(request: Request):
    return templates.TemplateResponse(name='login_form.html', context={'request': request})


@router.get('/users/me')
async def get_me_html(request: Request,
                         user: User = Depends(current_active_user),
                         my_user: User = Depends(get_my_users)
                         ):
    return templates.TemplateResponse(name='my_info.html', context={'request': request,
                                                                  "headline": "Мой кабинет",
                                                                  "user": user,
                                                                  "my_user": my_user,
                                                                  })



@router.get('/')
async def get_index_html(request: Request):
    return templates.TemplateResponse(name='base.html', context={'request': request})


@router.get('/posts')
async def get_posts_html(request: Request, posts=Depends(get_all_posts),
                         user: User = Depends(current_active_user),
                         my_user: User = Depends((get_my_users))):
    return templates.TemplateResponse(name='posts.html', context={'request': request,
                                                                  "headline": "Лента",
                                                                  "posts": posts,
                                                                  "user": user,
                                                                  "my_user": my_user})


@router.get('/posts/me')
async def get_posts_html(request: Request, posts=Depends(get_all_my_posts),
                         user: User = Depends(current_active_user),
                         my_user: User = Depends(get_my_users)
                         ):
    return templates.TemplateResponse(name='posts.html', context={'request': request,
                                                                  "headline": "Моя лента",
                                                                  "posts": posts,
                                                                  "user": user,
                                                                  "my_user": my_user})


@router.get('/posts/create')
async def create_post_html(request: Request,):
    return templates.TemplateResponse(name='post_form.html', context={'request': request})


@router.get('/posts/user/{user_id}')
async def get_posts_html(user_id: int,
                         request: Request, posts=Depends(get_posts_by_user),
                         user: User = Depends(current_active_user),
                         my_user: User = Depends(get_my_users)
                         ):
    return templates.TemplateResponse(name='posts.html', context={'request': request,
                                                                  "headline": "Лента пользователя",
                                                                  "posts": posts,
                                                                  "user": user,
                                                                  "my_user": my_user,
                                                                  "user_id": user_id})


@router.get('/posts/{post_id}')
async def get_posts_html(request: Request, post_id: int,
                         post=Depends(get_posts_by_id),
                         user: User = Depends(current_active_user),
                         my_user: User = Depends(get_my_users)
                         ):
    return templates.TemplateResponse(name='post.html', context={'request': request,
                                                                 "headline": "Пост",
                                                                 "post": post,
                                                                 "user": user,
                                                                 "my_user": my_user,
                                                                 })

