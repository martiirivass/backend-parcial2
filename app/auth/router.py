from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request
)

from sqlmodel import Session

from app.core.limiter import limiter
from app.core.unit_of_work import UnitOfWork

from app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    RefreshResponse,
    MeResponse,
)

from app.auth.services import (
    login_user,
    register_user,
    refresh_user_token,
    revoke_user_tokens,
)

from app.auth.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

from app.db.database import get_session

from app.auth.dependencies import (
    get_current_user
)

from app.models.usuario import Usuario

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
@limiter.limit("5/15minutes")
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
@limiter.limit("5/15minutes")
def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    session: Session = Depends(get_session)
):

    with UnitOfWork(session):
        token, refresh_token_str = login_user(email=data.email, password=data.password, session=session)

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
    response_model=RefreshResponse,
    status_code=200,
    summary="Renovar access token"
)
def refresh(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
):

    refresh_token_str = request.cookies.get("refresh_token")

    with UnitOfWork(session):
        new_token, new_raw = refresh_user_token(session, refresh_token_str)

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
        "message": "Token renovado exitosamente"
    }


@router.get(
    "/me",
    response_model=MeResponse,
    summary="Obtener usuario autenticado"
)
def me(
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
        ]
    }


@router.post(
    "/logout",
    status_code=204,
    summary="Cerrar sesión"
)
def logout(
    response: Response,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user),
):

    with UnitOfWork(session):
        revoke_user_tokens(session, current_user.id)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
