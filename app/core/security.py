import os
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from click import pass_context
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, PyJWTError
from pwdlib import PasswordHash
from sqlmodel import Session
from app.core.config import settings
from app.core.db import get_db
from app.models.user import User

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

credentials_exc = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="No autenticado",
    headers={"WWW-Authenticate": "Bearer"}
)


def raise_expired_token():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )


def raise_frobidden():
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="No tienes permisos suficientes",
    )


def invalid_credentials():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Credenciales inválidas")


def decode_token(token: str) -> dict:
    playload = jwt.decode(
        jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return playload


# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     expire = datetime.now(
#         tz=timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     token = jwt.encode(payload=to_encode,
#                        key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return token

def create_access_token(sub: str, minutes: int | None = None) -> str:
    expire = datetime.now(
        timezone.utc) + timedelta(minutes=minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": expire}, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:

    try:
        playload = decode_token(token)
        sub: Optional[str] = playload.get("sub")
        username: Optional[str] = playload.get("username")
        if not sub or not username:
            raise credentials_exc

        user_id = int(sub)
    except ExpiredSignatureError:
        raise raise_expired_token()
    except InvalidTokenError:
        raise credentials_exc
    except PyJWTError:
        raise invalid_credentials()

    user = db.get(User, user_id)

    if not user or not user.is_active:
        raise invalid_credentials()

    return user


def hash_password(plain: str) -> str:
    return password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


def require_role(min_role: Literal["user", "editor", "admin"]):
    order = {"user": 0, "editor": 1, "admin": 2}

    def evaluation(user: User = Depends(get_current_user)) -> User:
        if order[user.role] < order[min_role]:
            raise raise_frobidden()
        return user

    return evaluation


require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")
