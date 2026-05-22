from fastapi import APIRouter, Depends, Response, HTTPException, Request
from sqlmodel import Session

from app.auth.schemas import LoginRequest, RegisterRequest, UserResponse
from app.auth.services import login_user, register_user
from app.auth.security import create_access_token, hash_token, SECRET_KEY, ALGORITHM
from app.db.database import get_session
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.models.refresh_token_model import RefreshToken
from datetime import datetime, timedelta, UTC
import secrets
import jwt

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=UserResponse, status_code=201)
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
    return user


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

    # Decodifico el user ID del token para crear el refresh
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    usuario_id = int(payload.get("sub"))

    # Creo refresh token (almaceno SHA-256, devuelvo raw)
    refresh_token_str = secrets.token_urlsafe(64)
    refresh = RefreshToken(
        usuario_id=usuario_id,
        token_hash=hash_token(refresh_token_str),
        expires_at=datetime.now(UTC) + timedelta(days=7)
    )
    session.add(refresh)
    session.commit()

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token_str,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800  # 7 días
    )

    return {
        "message": "Login exitoso"
    }


@router.post("/refresh")
def refresh(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
):
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(status_code=400, detail="Refresh token requerido")

    repo = RefreshTokenRepository(session)
    stored = repo.get_valid_token(hash_token(refresh_token_str))
    if not stored:
        raise HTTPException(status_code=401, detail="Refresh token inválido o expirado")

    # Revoco el token usado (rotación)
    stored.revoked_at = datetime.now(UTC)
    session.add(stored)

    # Genero nuevo access token
    new_token = create_access_token({"sub": str(stored.usuario_id)})

    # Genero nuevo refresh token (hash SHA-256)
    new_raw = secrets.token_urlsafe(64)
    new_refresh = RefreshToken(
        usuario_id=stored.usuario_id,
        token_hash=hash_token(new_raw),
        expires_at=datetime.now(UTC) + timedelta(days=7)
    )
    session.add(new_refresh)
    session.commit()

    response.set_cookie(
        key="access_token",
        value=new_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800
    )
    response.set_cookie(
        key="refresh_token",
        value=new_raw,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800  # 7 días
    )

    return {
        "message": "Token renovado exitosamente"
    }