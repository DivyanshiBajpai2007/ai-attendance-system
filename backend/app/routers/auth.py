from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password, verify_password
from app.database import User, get_db

router = APIRouter()


@router.post('/auth/register')
def register(username: str, password: str, role: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail='Username already exists')
    if role not in ('admin', 'hr', 'employee'):
        raise HTTPException(status_code=400, detail='Invalid role')

    user = User(username=username, password_hash=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'message': 'User created', 'username': user.username, 'role': user.role}


@router.post('/auth/login')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Incorrect username or password')

    access_token = create_access_token(data={'sub': user.username, 'role': user.role})
    return {'access_token': access_token, 'token_type': 'bearer', 'role': user.role}
