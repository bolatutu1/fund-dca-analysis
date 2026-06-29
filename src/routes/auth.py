from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import User, WatchlistItem
from schemas import UserRegister, UserLogin, TokenResponse, WatchlistItemResponse
from datetime import datetime
import hashlib

router = APIRouter(tags=['认证'])


def hash_password(password: str) -> str:
    salt = 'fund-dca-v1'
    return hashlib.sha256(f'{salt}{password}'.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed


@router.post('/register', response_model=dict)
async def register(request: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail='用户名已存在')

    user = User(
        username=request.username,
        hashed_password=hash_password(request.password),
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {'message': '注册成功', 'username': request.username}


@router.post('/login', response_model=dict)
async def login(request: Request, username: str = Form(...),
                password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail='用户名或密码错误')

    if not user.is_active:
        raise HTTPException(status_code=403, detail='账号已禁用')

    request.session['user_id'] = user.id
    request.session['username'] = user.username

    return {'message': '登录成功', 'username': user.username}


@router.post('/logout')
async def logout(request: Request):
    request.session.clear()
    return {'message': '已退出登录'}


@router.get('/me')
async def get_me(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return {'logged_in': False}
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {'logged_in': False}
    return {
        'logged_in': True,
        'username': user.username,
        'user_id': user.id,
    }


@router.get('/watchlist', response_model=list[WatchlistItemResponse])
async def get_watchlist(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return []

    items = db.query(WatchlistItem).filter(
        WatchlistItem.user_id == user_id
    ).order_by(WatchlistItem.added_at.desc()).all()

    return [
        WatchlistItemResponse(
            fund_code=item.fund_code,
            fund_name='',
            added_at=item.added_at,
        )
        for item in items
    ]
