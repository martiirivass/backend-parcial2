from fastapi import APIRouter, Depends, Response, status
from sqlmodel import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse
)

from app.auth.services import (
    register_user,
    login_user
)

from app.db.database import get_session
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    session: Session = Depends(get_session)
):
    register_user(
        nombre=data.nombre,
        email=data.email,
        password=data.password,
        session=session
    )

    return {
        "message": "Usuario registrado"
    }


@router.post("/login")
def login(
    data: LoginRequest,
    response: Response,
    session: Session = Depends(get_session)
):
    token = login_user(
        email=data.email,
        password=data.password,
        session=session
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )

    return {
        "message": "Login exitoso"
    }


@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user: Usuario = Depends(
        get_current_user
    )
):
    return current_user


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        "access_token"
    )

    return {
        "message": "Logout exitoso"
    }