from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import Token, UserPublic
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, get_current_user

FAKE_USERS = {
    "ricardo@example.com": {"email": "ricardo@example.com", "username": "ricardo", "password": "secret123"},
    "alumno@example.com":  {"email": "alumno@example.com",  "username": "alumno",  "password": "123456"},
}

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    token = create_access_token(
        data={"sub": user["email"], "username": user["username"]},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserPublic)
async def read_me(current=Depends(get_current_user)):
    return {"email": current["email"], "username": current["username"]}
