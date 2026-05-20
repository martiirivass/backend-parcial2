from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from app.db.database import get_session
from app.auth.schemas import LoginRequest, RegisterRequest, UserResponse
from app.auth.services import login_user, register_user, get_me
from app.auth.dependencies import get_current_user
from app.models.usuario import Usuario

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", status_code=201)
def register(
    data: RegisterRequest,
    session: Session = Depends(get_session)
):
    user = register_user(
        nombre=data.nombre,
        email=data.email,
        password=data.password,
        session=session
    )

    return {
        "id": user.id,
        "nombre": user.nombre,
        "email": user.email,
        "mensaje": "Usuario registrado correctamente"
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
        secure=False,
        samesite="lax",
        max_age=1800
    )

    return {
        "message": "Login exitoso"
    }


@router.get("/me", response_model=UserResponse)
def me(
    current_user: Usuario = Depends(get_current_user)
):
    return get_me(current_user)
