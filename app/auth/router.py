from datetime import datetime, timedelta, UTC
import secrets
import jwt

from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
    Request
)

from sqlmodel import Session

from app.core.limiter import limiter
from app.core.config import settings

from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    MeResponse
)

from app.auth.services import (
    login_user,
    register_user
)

from app.auth.security import (
    create_access_token,
    hash_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from app.db.database import get_session

from app.repositories.refresh_token_repository import (
    RefreshTokenRepository
)

from app.models.refresh_token_model import (
    RefreshToken
)

from app.auth.dependencies import (
    get_current_user
)

from app.models.usuario import Usuario

from app.core.unit_of_work import (
    UnitOfWork
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="Registrar usuario cliente"
)
@limiter.limit(settings.RATE_LIMIT_REGISTER)
def register(
    request: Request,
    data: RegisterRequest,
    session: Session = Depends(get_session)
):

    with UnitOfWork(session):

        user = register_user(
            nombre=data.nombre,
            apellido=data.apellido or "",
            email=data.email,
            password=data.password,
            session=session,
            tipo_documento_codigo=data.tipo_documento_codigo,
            numero_documento=data.numero_documento,
        )

    return {
        "id": user.id,
        "nombre": user.nombre,
        "apellido": user.apellido,
        "email": user.email
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=200,
    summary="Iniciar sesión"
)
@limiter.limit(settings.RATE_LIMIT_LOGIN)
def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    session: Session = Depends(get_session)
):

    with UnitOfWork(session):

        token = login_user(
            email=data.email,
            password=data.password,
            session=session
        )

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        usuario_id = int(
            payload.get("sub")
        )

        refresh_token_str = secrets.token_urlsafe(64)

        refresh = RefreshToken(
            usuario_id=usuario_id,
            token_hash=hash_token(refresh_token_str),
            expires_at=datetime.now(UTC) + timedelta(days=7)
        )

        session.add(refresh)

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
        max_age=604800
    )

    return {
        "access_token": token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=200,
    summary="Renovar access token"
)
@limiter.limit(settings.RATE_LIMIT_DEFAULT)
def refresh(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
):

    refresh_token_str = request.cookies.get(
        "refresh_token"
    )

    if not refresh_token_str:
        raise HTTPException(
            status_code=400,
            detail="Refresh token requerido"
        )

    repo = RefreshTokenRepository(session)

    stored = repo.get_valid_token(
        hash_token(refresh_token_str)
    )

    if not stored:
        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido o expirado"
        )

    with UnitOfWork(session):

        stored.revoked_at = datetime.now(UTC)

        session.add(stored)

        new_token = create_access_token({
            "sub": str(stored.usuario_id)
        })

        new_raw = secrets.token_urlsafe(64)

        new_refresh = RefreshToken(
            usuario_id=stored.usuario_id,
            token_hash=hash_token(new_raw),
            expires_at=datetime.now(UTC) + timedelta(days=7)
        )

        session.add(new_refresh)

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
        max_age=604800
    )

    return {
        "access_token": new_token,
        "refresh_token": new_raw,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Obtener usuario autenticado"
)
def me(
    request: Request,
    current_user: Usuario = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "nombre": current_user.nombre,
        "apellido": current_user.apellido,
        "email": current_user.email,
        "tipo_documento_id": current_user.tipo_documento_id,
        "numero_documento": current_user.numero_documento,
        "created_at": current_user.created_at,
        "roles": [
            {
                "codigo": ur.rol.codigo,
                "nombre": ur.rol.nombre
            }
            for ur in current_user.usuario_roles
        ],
        "access_token": request.cookies.get("access_token")
    }


@router.post(
    "/logout",
    status_code=204,
    summary="Cerrar sesión"
)
def logout(
    response: Response
):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
